from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.response import Response

from api.v1.serializers.common import FrontCommonMediaFilesSerializer
from core.models.core import CommonMediaFiles


##########################      Blog Categories Admin            ################################
class CommonMediaFilesList(RetrieveAPIView):
    queryset = CommonMediaFiles.objects.all()
    serializer_class = FrontCommonMediaFilesSerializer
    lookup_field = 'id'

    def get(self, request, id):
        post = self.get_object(id)
        serializer = FrontCommonMediaFilesSerializer(post)
        return Response({
            'result': serializer.data,
            'message': 'success'
        })



