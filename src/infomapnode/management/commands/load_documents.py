from enum import Enum
import logging
import os
from itertools import groupby

from django.core.management.base import CommandError

from geonode.base.enumerations import SOURCE_TYPE_REMOTE
from geonode.base.models import ResourceBase, LinkedResource
from geonode.resource.manager import resource_manager

from infomapnode.management.commands.load_documents_base import Command as LoadBase

logger = logging.getLogger(__name__)

MAX_LINK_LEN = 512
MAX_TITLE_LEN = 255


class Command(LoadBase):
    help = "Load FTS documents into DB"

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument("--dir", dest="dir",
                            help="Full path to the directory containing the text files to index.")

        parser.add_argument(
            "--fts",
            action="store_true",
            dest="fts",
            default=False,
            help="Load data for FTS",
        )

    def handle(self, **options):
        input_dir = options.get("dir")
        if not input_dir:
            raise CommandError("Missing directory path (--dir)")

        self.input_dir = input_dir

        fts = options.get("fts")
        self.fts = fts

        super().handle(**options)

    class CsvField(Enum):
        FIELD_TITLE = 'title'
        FIELD_LINK = 'document_link'
        FIELD_LANG = 'language_ISO_639_1'
        FIELD_YEAR = 'year'
        FIELD_IMAGE = 'image_link'
        FIELD_FILENAME = 'filenameid'
        FIELD_EXT = 'file_extension'
        FIELD_DOMAIN = 'domain'
        FIELD_ERR = 'error_txt_write'
        FIELD_SRCID = 'id'

    def get_headers(self):
        return [v.value for v in self.CsvField]

    def build_document(self, line, row, index, owner):
        def get_field(row, index, field, deflt=None):
            v = row[index[field.value]]
            return v if v != "NA" else deflt

        id = get_field(row, index, self.CsvField.FIELD_SRCID)

        title = get_field(row, index, self.CsvField.FIELD_TITLE)
        if len(title) > MAX_TITLE_LEN:
            logger.warning(f"Title too long -- id:{id} len:{len(title)}")
            title_short = f"{title[:MAX_TITLE_LEN-3]}..."
        else:
            title_short = title

        abstract_fields = [
                (self.CsvField.FIELD_DOMAIN, "- DOMAIN"),
                (self.CsvField.FIELD_YEAR, "- YEAR"),
                (self.CsvField.FIELD_LANG, "- LANG"),
                (self.CsvField.FIELD_SRCID, "- Source id"),]

        link = get_field(row, index, self.CsvField.FIELD_LINK)
        if len(link) > MAX_LINK_LEN:
            logger.error(f"URL too long -- id:{id} len:{len(link)}")
            abstract_fields.append((self.CsvField.FIELD_LINK, "- Doc URL"))

        abstr = f"{title}<BR/>"
        for f, label in abstract_fields:
            val = get_field(row, index, f)
            if val:
                abstr = f"{abstr}\n   \n   <BR/>{label}: {val} "

        thumb = get_field(row, index, self.CsvField.FIELD_IMAGE)

        # find fts file
        filename = get_field(row, index, self.CsvField.FIELD_FILENAME)
        filepath = os.path.join(self.input_dir, filename + ".txt")
        filegood = get_field(row, index, self.CsvField.FIELD_ERR) == "OK"

        if os.path.exists(filepath):
            logger.debug(f"FTS file found at {filepath}")
            if not filegood:
                logger.warning(f"FTS file {filepath} should not exist")
        else:
            filepath = None
            if filegood:
                # file does not exist even if it should
                logger.warning(f"FTS file not found {filepath} - good {filegood}")
            else:
                logger.debug(f"FTS file not provided for {id}")

        doc_dict = dict(
            title=title_short,
            abstract=abstr,
            doc_url=link[:MAX_LINK_LEN],  # cut urls will not work!
            extension=get_field(row, index, self.CsvField.FIELD_EXT),
            sourcetype=SOURCE_TYPE_REMOTE,
            owner=owner,
        )

        if filepath:
            doc_dict['supplemental_information'] = "FTS indexed"
        if thumb:
            doc_dict['thumbnail_url'] = thumb

        return doc_dict, {'filepath': filepath, 'title': title, 'id': id, 'thumb':thumb}

    def post_create(self, doc, extra, persist):
        if doc:
            extra['doc'] = doc
        if doc and not extra['thumb']:
            logger.debug(f"Creating thumb for {doc.id if doc else extra['id']}")
            resource_manager.set_thumbnail(doc.id, instance=doc)

    def post_process(self, extras, persist):
        self.add_related_links(extras, persist)

        if self.fts:
            self.load_fts(extras, persist)

    def add_related_links(self, extras, persist):
        extras = sorted(extras, key=lambda x: x['title'])
        for title, group in groupby(extras, key=lambda x: x['title']):
            ids = [x['doc'].id for x in group] if persist else [x['id'] for x in group]
            if len(ids) > 1:
                logger.info(f"Creating related links for {len(ids)} docs: '{title}' --> {ids}")
                for source_id in ids:
                    targets = set(ids) - {source_id}
                    for target_id in targets:
                        logger.debug(f"Linking doc {source_id} --> {target_id}")
                        if persist:
                            LinkedResource.objects.get_or_create(
                                source=ResourceBase.objects.get(pk=source_id),
                                target=ResourceBase.objects.get(pk=target_id),
                                internal=False)

    def load_fts(self, extras, persist):
        from infomapnode.fulltextsearch.models import FullText
        from pathlib import Path
        import re

        found = 0
        stored = 0
        skipped = 0
        for extra in extras:
            file = extra['filepath']
            if file:
                found += 1
                logger.info(f'Loading FTI for {extra["doc"].id if persist else extra["id"]}')
                if persist:
                    txt = re.sub("\s{2,}", ' ', Path(file).read_text())
                    txt = txt.strip()
                    if txt:
                        ft = FullText()
                        ft.base = ResourceBase.objects.get(pk=extra['doc'].id)
                        ft.content = txt
                        ft.save()
                        stored += 1
                    else:
                        logger.warning(f'Skipping empty FTI for {extra["doc"].id if persist else extra["id"]}')
                        skipped += 1

        logger.info(f"Added full text index for {stored} records, found {found} text, skipped {skipped}")
