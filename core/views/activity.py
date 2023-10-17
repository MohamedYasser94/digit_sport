from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from rest_framework.views import APIView

from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import authenticated_staf, staff_only


@authenticated_staf
@staff_only
def AdminActivityLog(request,model):
    print('model',model)
    Active_logs = ContentType.objects.get(model=model).model_class().objects.all()
    print('Active_logs', Active_logs)
    context = {
        'Active_logs': Active_logs,

        'current_page': _('All Activity'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/activity/admin.html', context)


class  AdminFaceBookWhatsappWebHooks(APIView):
    def get(self, request):
        """Necessary for webhook url validation from Facebook"""

        verify_token = request.GET.get("hub.verify_token", "")

        if verify_token != "MyVerificationToken":
            return Response("Wrong verification token", status=403)

        return Response(int(request.GET.get("hub.challenge", 0)))