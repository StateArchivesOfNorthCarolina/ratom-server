import gzip
import json
from collections import defaultdict
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework import renderers
from rest_framework.permissions import IsAuthenticated
from api.views import MessageDocumentView
from api.serializers import ExportDocumentSerializer


class FileRenderer(renderers.BaseRenderer):
    media_type = "application/x-gzip"
    format = "gzip"
    charset = None
    render_style = "binary"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


def compress_response(data):
    fo = json.dumps(data).encode("utf-8")
    return gzip.compress(fo)


class ExportDocumentView(MessageDocumentView):
    """Returns a zipped json file that has this structure:

    {
        "filename01.pst": [001,002,003,004],
        "filename02.pst": [005,006,007,008],
    }
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ExportDocumentSerializer
    pagination_class = None
    renderer_classes = [FileRenderer]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        hits = queryset.source(fields=["source_id", "file"]).scan()
        export = defaultdict(list)
        for hit in hits:
            export[hit.file["filename"]].append(hit.source_id)
        dataIO = compress_response(export)
        returned_file_name = f"rr-{now().strftime('%Y-%m-%dT%H%M%S')}.txt.gz"
        return Response(
            data=dataIO,
            headers={
                "Content-Disposition": f"attachment; filename={returned_file_name}"
            },
        )
