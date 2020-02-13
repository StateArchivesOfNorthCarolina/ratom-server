import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import File
from etl.tasks import import_file_task

__all__ = ("FileUpdateView",)

logger = logging.getLogger(__name__)


class FileUpdateView(APIView):
    """
    A view to restart a file.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # MVP: We assume this will always be one and only one failed file.
        qs = File.objects.filter(account=request.data["id"]).filter(
            import_status=File.FAILED
        )
        if qs:
            import_file_task.delay(
                [qs[0].filename], qs[0].account.title, clean_file=True
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)
