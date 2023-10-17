import logging

from django.shortcuts import render
# Create your views here.
from django.urls import reverse_lazy, reverse

from core.models.core import SystemSetting
from Digithup.settings import FRONTEND_TEMPLATES, MAINTENANCE_TEMPLATES



def HomeIndex(request):
    system_setting = SystemSetting.objects.get(title='Digithup')
    if system_setting.maintenance == 'Active':

        return render(request, f'frontend/{MAINTENANCE_TEMPLATES}/maintenance.html')


    elif system_setting.maintenance == 'Inactive':
        return render(request, f'frontend/{FRONTEND_TEMPLATES}/index.html')


def SiteGo(request):
    systemseeting = SystemSetting.objects.get(title='Digithup')
    systemseeting.maintenance = 'Inactive'
    systemseeting.save()
    return render(request, f'frontend/{FRONTEND_TEMPLATES}/index.html')


def FrontedLawyer(request):
    lawyers = Lawyer.objects.all()

    context = {
        'lawyers': lawyers,
    }

    return render(request, f'{FRONTEND_TEMPLATES}/services/lawyer.html', context)


def FrontedDetailsLawyer(request, slug):
    lawyers = Lawyer.objects.all()
    lawyer = Lawyer.objects.get(slug=slug)

    context = {
        'lawyers': lawyers,
        'lawyer': lawyer,
    }

    return render(request, f'{FRONTEND_TEMPLATES}/services/lawyer-detail.html', context)


logger = logging.getLogger(__name__)


def page_not_found_view(
        request,
        exception,
        template_name=f'{FRONTEND_TEMPLATES}/error/403.html'):
    if exception:
        logger.error(exception)
    url = request.get_full_path()
    return render(request, template_name, {'message': f'哎呀，您访问的地址 {url} 是一个未知的地方。请点击首页看看别的？', 'statuscode': '404'},
                  status=404)


def server_error_view(request, template_name=f'{FRONTEND_TEMPLATES}/error/505.html'):
    return render(request,
                  template_name,
                  {'message': '哎呀，出错了，我已经收集到了错误信息，之后会抓紧抢修，请点击首页看看别的？',
                   'statuscode': '500'},
                  status=500)


def permission_denied_view(
        request,
        exception,
        template_name=f'{FRONTEND_TEMPLATES}/error/403.html'):
    if exception:
        logger.error(exception)
    return render(
        request, template_name, {
            'message': '哎呀，您没有权限访问此页面，请点击首页看看别的？', 'statuscode': '403'}, status=403)


def page_not_found_view(request, exception):
    return render(request, f'{FRONTEND_TEMPLATES}/error/404.html', status=404)


def error403(request, ):
    return render(request, f'{FRONTEND_TEMPLATES}/error/403.html', status=403)


def error404(request, exception):
    return render(request, 'front/ErrorPage/404.html', status=404)


def error_404_view(request, exception):
    data = {"title": "ThePythonDjango.com"}
    return render(request, 'front/ErrorPage/404.html', data)


def comming_soon(request):
    return render(request, 'front/ErrorPage/comming-soon.html', )
