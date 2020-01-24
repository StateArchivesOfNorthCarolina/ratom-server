import logging
import json

from django.conf import settings
from django_elasticsearch_dsl_drf.pagination import PageNumberPagination
from elasticsearch_dsl import connections, Index

logger = logging.getLogger(__name__)


class LoggingPageNumberPagination(PageNumberPagination):
    """
    Pagination that also performs Elasticsearch query logging.
    Only use for debugging.
    """

    def paginate_queryset(self, queryset, request, view=None):
        query = json.dumps(queryset.to_dict(), indent=2)
        logger.debug(f"elasticsearch query: {query}")
        page = super().paginate_queryset(queryset, request, view)
        # This isn't ideal, but seemed easier than rewriting most of
        # paginate_queryset(). Only use use for debugging.
        logger.debug("Re-running last query...")
        page_size = self.get_page_size(request)
        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        page = paginator.page(page_number)
        full_query = json.dumps(page.object_list._d_, indent=2)
        logger.debug(f"elasticsearch response: {full_query}")
        return page


def enable_elasticsearch_debug_logging():
    """
    Configure Elasticsearch itself to use more verbose logging.

    For now manually run in manage.py shell:
        from ratom.search_utils import enable_elasticsearch_debug_logging
        enable_elasticsearch_debug_logging()

    More info:
        https://www.elastic.co/guide/en/elasticsearch/guide/current/logging.html#logging
    """
    connections.create_connection(**settings.ELASTICSEARCH_DSL)
    conn = connections.get_connection()
    cluster_settings = {"transient": {"logger.discovery": "DEBUG"}}
    logger.info(f"setting: {cluster_settings}")
    logger.info(conn.cluster.put_settings(cluster_settings))
    index_name = settings.ELASTICSEARCH_INDEX_NAMES["ratom.documents.message"]
    index = Index(index_name)
    index_settings = {
        "index.search.slowlog.threshold.query.warn": "2ms",
        "index.search.slowlog.threshold.fetch.debug": "2ms",
    }
    logger.info(f"setting: {index_settings}")
    logger.info(index.put_settings(using=None, body=index_settings))
