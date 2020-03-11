import gzip
import json
import ast
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


def decompose_drf_data(od):
    for export_list in od:
        v = list(export_list.values())
        yield v[0], ast.literal_eval(v[1])["filename"]


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
        serializer = self.get_serializer(queryset, many=True)
        current_file = {}
        for id, filename in decompose_drf_data(serializer.data):
            if filename in current_file.keys():
                current_file[filename].append(id)
            else:
                current_file[filename] = [id]
        dataIO = compress_response(current_file)
        returned_file_name = f"rr-{now().strftime('%Y-%m-%dT%H%M%S')}.gz"
        return Response(
            data=dataIO,
            headers={
                "Content-Disposition": f"attachment; filename={returned_file_name}"
            },
        )
