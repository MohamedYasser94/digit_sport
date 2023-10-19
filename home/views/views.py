import logging

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from apps.sport.views.utils import FrontIndexSportAppData
from core.models.blog import BlogArticle
from core.models.core import CommonMediaFiles, SystemSetting, CommonSocialLink
from core.models.people import TeamSkill, Team
from helper.commonHelper import FRONTEND_TEMPLATES, MAINTENANCE_TEMPLATES, BACKEND_TEMPLATES


# Create your views here.


def HomeIndex(request):
    system_app = SystemSetting.objects.get(title='Digithup')
    print(' system_app.maintenance', system_app.maintenance,system_app.maintenance_temp)
    if system_app.maintenance == 'Active':
        event_data = FrontIndexSportAppData(request)
        context = {
            'event_data': event_data,

            'current_page': 'Home',
        }
        return render(request,  f'frontend/{MAINTENANCE_TEMPLATES}/index.html',context )
    elif system_app.maintenance == 'Inactive':

        articles = BlogArticle.objects.all()
        article_list = []
        for article in articles:
            image = CommonMediaFiles.objects.get(owner_model=ContentType.objects.get(model='BlogArticle'),
                                                    owner_id=article.id,type='hero')
            article_list.append({'article': article, 'image': image})

        event_data = FrontIndexSportAppData(request)




        context = {
            'articles': article_list,
            'event_data': event_data,
            'current_page': 'Home',
        }
        return render(request,  f'frontend/{FRONTEND_TEMPLATES}/index.html',context )



def TheTeamFront(request):
    teams = Team.objects.all()
    team_list = []
    for team in teams:
        skills =TeamSkill.objects.filter(team=team)
        social = CommonSocialLink.objects.filter(owner_model=ContentType.objects.get(model='Team'), owner_id=team.id,
                                                 )
        team_list.append({'team': team, 'skills': skills, 'social': social})
    context = {
        'teams': team_list,
    }
    return render(request, f'{FRONTEND_TEMPLATES}/contact/team.html',context )


def FrontTheTeamDetails(request,slug):
    team = Team.objects.get(slug=slug)
    skills = TeamSkill.objects.filter(team=team)
    social = CommonSocialLink.objects.filter(owner_model=ContentType.objects.get(model='Team'), owner_id=team.id,
                                             )
    context = {
        'team': team,
        'skills': skills,
        'social': social,
    }
    return render(request, f'{FRONTEND_TEMPLATES}/contact/team_details.html',context )

def FAQ(request):
    return render(request, f'{FRONTEND_TEMPLATES}/contact/faq.html', )

def FrontPrivacyPolicy(request):
    return render(request, f'{FRONTEND_TEMPLATES}/contact/privacypolicy.html', )

def FrontTermsOfService(request):
    return render(request, f'{FRONTEND_TEMPLATES}/contact/termsofservice.html', )




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


def server_error_view(request, template_name=f'{FRONTEND_TEMPLATES}/error/500.html'):
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
    return render(request, f'{FRONTEND_TEMPLATES}/error/404.html', status=404)


def error_404_view(request, exception):
    data = {"title": "ThePythonDjango.com"}
    return render(request, f'{FRONTEND_TEMPLATES}/error/404.html', data)


def comming_soon(request):
    return render(request, 'front/ErrorPage/comming-soon.html', )


def FrontTestPage(request):
    confirm_message = _(f'Dear, Hitham Gamal Mohamed \n'
                        f'We have received your request for registration in  Expontion event  \n'
                        f'and will send you an email once your registration is confirmed. \n'

                        f'”Thank you for your interest.”')
    message = confirm_message
    context = {'message': message,

               }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/email/ticket/request.html',context )
