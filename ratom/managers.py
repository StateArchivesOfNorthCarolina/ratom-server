from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
)
from django.db import models

""""
Experimental?
"""

search_vectors = (
    SearchVector("msg_subject", weight="A")
    + SearchVector("msg_body", weight="B")
    + SearchVector("msg_headers", weight="C")
)


class MessageManager(models.Manager):
    def search(self, text: str) -> models.QuerySet:
        search_query = SearchQuery("Pinnacle West")
        search_rank = SearchRank(search_vectors, search_query)
        return (
            self.get_queryset()
            .annotate(search=search_vectors,)
            .filter(search=search_query,)
            .annotate(rank=search_rank,)
            .order_by("-rank")
        )
