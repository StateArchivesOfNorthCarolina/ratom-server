import logging
import json

from django.conf import settings
from elasticsearch_dsl import connections, Index
from elasticsearch_dsl.search import Search

logger = logging.getLogger(__name__)


class LoggingSearch(Search):
    """Elasticsearch DSL Search extension that performs optional logging."""

    def execute(self, *args, **kwargs):
        if settings.ELASTICSEARCH_LOG_QUERIES:
            query = json.dumps(self.to_dict(), indent=2)
            logger.debug(f"elasticsearch query: {query}")
        response = super().execute(*args, **kwargs)
        if settings.ELASTICSEARCH_LOG_QUERIES:
            output = json.dumps(response.to_dict(), indent=2)
            logger.debug(f"elasticsearch response: {output}")
        return response


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
