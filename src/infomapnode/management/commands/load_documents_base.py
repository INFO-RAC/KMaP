import csv
from enum import Enum
import logging
import os

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from geonode.base.enumerations import SOURCE_TYPE_REMOTE
from geonode.base.models import ResourceBase, LinkedResource
from geonode.documents.models import Document
from geonode.resource.manager import resource_manager


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Generic command for loading CSV files and create remote documents out of them.
    It needs a csv file with fields 'title' and 'document_link'.
    Most useful when subclassed.
    """

    help = "Load documents into DB"
    PERMS = {"users": {"AnonymousUser": ["view_resourcebase", "download_resourcebase"]}, "groups": {}}

    def add_arguments(self, parser):
        parser.add_argument("--file", dest="file",
                            help="Full path to a CSV file.")
        parser.add_argument("--owner", dest="owner", default='admin',
                            help="Username of the owner of the created resources.")

        parser.add_argument("--start", dest="start_row", default=1, type=int,
                            help="Starting row to import (1 based), default 1.")
        parser.add_argument("--max", dest="max_rows", default=None, type=int,
                            help="Max number of rows to import")

        parser.add_argument(
            "-d",
            "--dry-run",
            action="store_false",
            dest="persist",
            help="Only parse and print the CSV file, without adding records in the DB.",
        )

    def handle(self, **options):
        owner_username = options.get("owner")
        input_file = options.get("file")
        persist = options.get("persist")

        if not owner_username:
            raise CommandError("Missing owner (--owner)")

        try:
            owner = get_user_model().objects.get(username=owner_username)
        except ObjectDoesNotExist:
            raise CommandError(f"User not found '{owner_username}'")

        if not input_file:
            raise CommandError("Missing CSV file path (--file)")

        start_row = options.get("start_row")
        if start_row < 1:
            raise CommandError("Start row must be > 0")

        max_rows = options.get("max_rows")
        if max_rows is not None and max_rows < 0:
            raise CommandError("Max rows must be >= 0")

        logger.info(f"Data will { 'NOT ' if not persist else ''}be persisted into the DB")

        self.load_documents(input_file, owner, persist, start_row=start_row, max_rows=max_rows)

    def load_documents(self, input_file, owner, persist, start_row=0, max_rows=None):
        logger.info(f"Importing {max_rows if max_rows is not None else 'all'} rows starting from row {start_row}")

        extras = []
        curr_row = 0

        with open(input_file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            headers = next(reader, None)
            index = self.create_headers_index(headers)
            logger.debug(f"Header index: {index}")

            for data_row in reader:
                curr_row += 1

                if curr_row < start_row:
                    continue
                if max_rows is not None and curr_row >= start_row + max_rows:
                    break

                doc_dict, extra = self.build_document(curr_row, data_row, index, owner)
                extras.append(extra)

                if persist:
                    doc = resource_manager.create(None, resource_type=Document, defaults=doc_dict)
                    resource_manager.set_permissions(doc.id, instance=doc, permissions=self.PERMS, created=True)
                else:
                    doc = None

                self.post_create(doc, extra, persist)

            self.post_process(extras, persist)

    def get_headers(self):
        """
        Overridable by subclasses
        @return: list of usable headers
        """
        return ['title', 'document_link']

    def create_headers_index(self, headers):
        index = {}
        for idx, h in enumerate(headers):
            found = False
            for wkh in self.get_headers():
                if wkh == h:
                    found = True
                    logger.info(f"Mapped header found #{idx} [{h}]")
                    index[wkh] = idx
                    break
            if not found:
                logger.debug(f"Found unused header #{idx} [{h}] ")

        return index

    def build_document(self, line, row, index, owner):
        """
        Overridable by subclasses
        @return: list of usable headers
        """
        def _get_field(row, index, field, deflt=None):
            v = row[index[field]]
            return v if v != "NA" else deflt

        title = _get_field(row, index, 'title')
        if len(title) > 255:
            logger.warning(f"Title too long -- line:{line} len:{len(title)}")
            title255 = f"{title[:252]}..."
        else:
            title255 = title

        doc_dict = dict(
            title=title255,
            abstract=title,
            doc_url=self.get_field(row, index, "document_link"),
            sourcetype=SOURCE_TYPE_REMOTE,
            owner=owner,
        )

        return doc_dict, {'title': title}

    def post_create(self, doc, extra, persist):
        """
        Called after a doc has been created.

        Overridable by subclasses
        @param doc: Document, or None if persist is False
        @param extra: dict of extra info returned by build_document()
        @param persist: bool
        """
        pass

    def post_process(self, extras, persist):
        """
        Called after all docs have been created.

        Overridable by subclasses
        @param extras: list of dict of extra info returned by build_document()
        @param persist: bool
        """
        pass
