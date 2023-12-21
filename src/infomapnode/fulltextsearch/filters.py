import logging
import operator
from functools import reduce

from rest_framework.compat import distinct
from rest_framework.filters import SearchFilter

from django.db import models
from django.contrib.postgres.search import SearchQuery

logger = logging.getLogger(__name__)
FTS_FIELD = "fulltext__svf"


class FTSDynamicSearchFilter(SearchFilter):

    def get_search_fields(self, view, request):
        # force FTS_FIELD as a search field

        logger.info("CALLING FTSDynamicSearchFilter")
        ret = request.GET.getlist("search_fields", [])
        if FTS_FIELD not in ret:
            ret.append(FTS_FIELD)
        return ret

    def construct_search(self, field_name):
        # prevent diango ORM op to be added to the FTS field

        if field_name == FTS_FIELD:
            return FTS_FIELD
        else:
            return super().construct_search(field_name)

    def filter_queryset(self, request, queryset, view):
        # mostly copied from SearchFilter, adding a SearchQuery for the FTS field

        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset

        orm_lookups = [
            self.construct_search(str(search_field))
            for search_field in search_fields
        ]

        base = queryset
        conditions = []
        for search_term in search_terms:
            queries = [
                models.Q(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups
                if orm_lookup != FTS_FIELD
            ]
            if FTS_FIELD in orm_lookups:
                queries.append(models.Q(**{FTS_FIELD: SearchQuery(search_term)}))

            conditions.append(reduce(operator.or_, queries))
        queryset = queryset.filter(reduce(operator.and_, conditions))

        if self.must_call_distinct(queryset, search_fields):
            # Filtering against a many-to-many field requires us to
            # call queryset.distinct() in order to avoid duplicate items
            # in the resulting queryset.
            # We try to avoid this if possible, for performance reasons.
            queryset = distinct(queryset, base)

        # logger.info(f"QUERYSET {get_sql(queryset)}")
        # logger.info(f"EXPLAIN {queryset.explain()}")

        return queryset


# def get_sql(queryset: models.QuerySet):
#     from pygments import highlight
#     from pygments.formatters import TerminalFormatter
#     from pygments.lexers import PostgresLexer
#     from sqlparse import format
#
#     formatted = format(str(queryset.query), reindent=True)
#     return highlight(formatted, PostgresLexer(), TerminalFormatter())
