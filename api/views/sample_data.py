from django.db import transaction

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from api.sample_data.data import sample_reset_all

__all__ = ("reset_sample_data",)


@permission_classes([IsAuthenticated])
@api_view(["POST"])
@transaction.atomic
def reset_sample_data(request):
    sample_reset_all()
    return Response("Done")
