import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import File
from etl.tasks import remove_file_task

__all__ = ("FileDeleteView",)

logger = logging.getLogger(__name__)


class FileDeleteView(APIView):
    """
    A view to remove a file.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request):
        qs = File.objects.filter(account=request.data["id"]).filter(
            import_status=File.FAILED
        )
        if qs.exists():
            remove_file_task.delay(list(qs.values_list(flat=True)))
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)
