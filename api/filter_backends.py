import operator
from functools import reduce
from elasticsearch_dsl.query import Q

from django_elasticsearch_dsl_drf.filter_backends.filtering.common import (
    FilteringFilterBackend,
)


class CustomFilteringFilterBackend(FilteringFilterBackend):
    def _email_search_backend(cls, queryset, options, value):
        values = value.split(",")
        queries = []
        for _value in values:
            queries.append(
                Q("wildcard", **{"msg_to": {"value": "*{}*".format(_value)}})
            )
            queries.append(
                Q("wildcard", **{"msg_from": {"value": "*{}*".format(_value)}})
            )

        if queries:
            queryset = cls.apply_query(
                queryset=queryset, options=options, args=[reduce(operator.or_, queries)]
            )
        return queryset

    @classmethod
    def apply_query_contains(cls, queryset, options, value):
        if options["field"] == "msg_to":
            return cls._email_search_backend(cls, queryset, options, value)

        return super().apply_query_contains(queryset, options, value)
