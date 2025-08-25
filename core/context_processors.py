import os
from datetime import timedelta, datetime

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db.models import Sum

from core.models.blog import BlogArticle
from core.models.core import SystemSetting, SiteSetting, CommonMediaFiles, CommonSeo
from core.models.localization import Language
from core.models.notifications import Notification


User = get_user_model()


def setting_processors(request):
    try:
        system_setting_add = SystemSetting.objects.get(title='Digithup')
    except Exception as e:
        system_setting_add = SystemSetting.objects.create(title='Digithup')
    system_info_add = SiteSetting.objects.get_or_create(title='Digithup')
    system_settings = SystemSetting.objects.get(title='Digithup')
    dashboard_setting = SiteSetting.objects.get(title='Digithup')
    dashboard_setting.domain = request._current_scheme_host
    dashboard_setting.save()
    sites = Site.objects.all()
    for site in sites:
        site.domain = request._current_scheme_host
        site.name = 'Digithup'
        site.save()

    try:
        dashboard_image = CommonMediaFiles.objects.filter(type='hero',
                                                          owner_model=ContentType.objects.get(model='SiteSetting'),
                                                          owner_id=dashboard_setting.id)
        dashboard_seo = CommonSeo.objects.filter(owner_model=ContentType.objects.get(model='SiteSetting'),
                                                 owner_id=dashboard_setting.id)
        dashboard_app = SystemSetting.objects.get(title='Digithup').app

        return {
            'dashboard_setting': dashboard_setting,
            'dashboard_image': dashboard_image,
            'dashboard_seo': dashboard_seo,
            'system_settings': system_settings,
            'dashboard_app': dashboard_app,

        }
    except BaseException as e:
        print('SiteSetting', e)
        return {
            'dashboard_setting': None,
            'dashboard_image': None,
            'dashboard_seo': None,
            'dashboard_app': None,
            'system_settings': system_settings,

        }


def geoip_processors(request):
    try:

        import IP2Location
        database = IP2Location.IP2Location(os.path.join("geoip/IP2LOCATION-LITE-DB11.BIN"))

        if x_forwarded_for := request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        if ip == '127.0.0.1':  # Only define the IP if you are testing on localhost.
            ip = '127.0.0.1'

        device_type = ""
        browser_type = ""
        browser_version = ""
        os_type = ""
        os_version = ""
        if request.user_agent.is_mobile:
            device_type = "Mobile"
        if request.user_agent.is_tablet:
            device_type = "Tablet"
        if request.user_agent.is_pc:
            device_type = "PC"

        browser_type = request.user_agent.browser.family
        browser_version = request.user_agent.browser.version_string
        os_type = request.user_agent.os.family
        os_version = request.user_agent.os.version_string

        location = database.get_all(ip)
        # location_country = location["country_name"]
        # print('location_country', location)
        # location_city = location["city"]

        return {
            "ip": ip,
            "device_type": device_type,
            "browser_type": browser_type,
            "browser_version": browser_version,
            "os_type": os_type,
            "os_version": os_version,
            # "location_country": location_country,
            # "location_city": location_city

        }



    except Exception as e:
        print('geoip error', e)

        return {
            "ip": None,
            "device_type": None,
            "browser_type": None,
            "browser_version": None,
            "os_type": None,
            "os_version": None,
            "location_country": None,
            "location_city": None
        }


def language_processors(request):
    language = Language.objects.all()
    en_language = Language.objects.get_or_create(name='English', code='en')
    ar_language = Language.objects.get_or_create(name='Arabic', code='ar')
    try:
        return {
            'available_lang': list(language.values('id', 'code', 'name')),
            'en_language': language.get(code='en'),
            'ar_language': language.get(code='ar'),
        }

    except Exception as e:
        print('language error', e)
        return {
            'en_language': None,
            'ar_language': None,
        }


def template_processors(request):
    try:
        system_check = SystemSetting.objects.get_or_create(title='Digithup')
        system_setting = SystemSetting.objects.get(title='Digithup')
        if system_setting.maintenance == 'Active':
            if not request.user.is_authenticated:
                return {

                'BACKEND_TEMPLATES': SystemSetting.objects.get(title='Digithup').backend_temp,
                'BACKEND_ASSETS': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/assets',
                'BACKEND_BASE': 'backend/' + SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/adminbase.html',
                'BACKEND_HEAD': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/head.html',
                'BACKEND_HEADER': 'backend/' + SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/header.html',
                'BACKEND_SLIDER': 'backend/' + SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/slider.html',
                'BACKEND_SIDEBAR': 'backend/' + SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/sidebar.html',
                'BACKEND_BREADCRUMB': SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/common/breadcrumb.html',
                'BACKEND_BODY': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/content.html',
                'BACKEND_FOOTER': 'backend/' + SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/footer.html',
                'BACKEND_DRAWER': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/drawer.html',
                'BACKEND_JS': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/js.html',

                ############################ Frontend #########################################
                'FRONTEND_TEMPLATES': SystemSetting.objects.get(title='Digithup').maintenance_temp,
                'FRONTEND_ASSETS': 'frontend/' + SystemSetting.objects.get(title='Digithup').maintenance_temp + '/assets',
                'FRONTEND_BASE': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').maintenance_temp + '/homebase.html',
                'FRONTEND_HEAD': 'frontend/' + SystemSetting.objects.get(title='Digithup').maintenance_temp + '/head.html',
                'FRONTEND_HEADER': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').maintenance_temp + '/header.html',
                'FRONTEND_SLIDER': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').maintenance_temp + '/slider.html',
                'FRONTEND_PLAYER': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').maintenance_temp + '/player.html',
                'FRONTEND_VUE': 'frontend/' + SystemSetting.objects.get(title='Digithup').maintenance_temp + '/vuejs.html',
                'FRONTEND_SIDEBAR': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').maintenance_temp + '/sidebar.html',
                'FRONTEND_BREADCRUMB': SystemSetting.objects.get(
                    title='Digithup').maintenance_temp + '/common/breadcrumb.html',
                'FRONTEND_BODY': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').maintenance_temp + '/content.html',
                'FRONTEND_FOOTER': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').maintenance_temp + '/footer.html',
                'FRONTEND_MODAL': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').maintenance_temp + '/modal.html',
                'FRONTEND_JS': 'frontend/' + SystemSetting.objects.get(title='Digithup').maintenance_temp + '/js.html',

            }
            else:
                return {

                    'BACKEND_TEMPLATES': SystemSetting.objects.get(title='Digithup').backend_temp,

                    'BACKEND_ASSETS': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/assets',
                    'BACKEND_BASE': 'backend/' + SystemSetting.objects.get(
                        title='Digithup').backend_temp + '/adminbase.html',
                    'BACKEND_HEAD': 'backend/' + SystemSetting.objects.get(
                        title='Digithup').backend_temp + '/head.html',
                    'BACKEND_HEADER': 'backend/' + SystemSetting.objects.get(
                        title='Digithup').backend_temp + '/header.html',
                    'BACKEND_SLIDER': 'backend/' + SystemSetting.objects.get(
                        title='Digithup').backend_temp + '/slider.html',
                    'BACKEND_SIDEBAR': 'backend/' + SystemSetting.objects.get(
                        title='Digithup').backend_temp + '/sidebar.html',
                    'BACKEND_BREADCRUMB': SystemSetting.objects.get(
                        title='Digithup').backend_temp + '/common/breadcrumb.html',
                    'BACKEND_BODY': 'backend/' + SystemSetting.objects.get(
                        title='Digithup').backend_temp + '/content.html',
                    'BACKEND_FOOTER': 'backend/' + SystemSetting.objects.get(
                        title='Digithup').backend_temp + '/footer.html',
                    'BACKEND_DRAWER': 'backend/' + SystemSetting.objects.get(
                        title='Digithup').backend_temp + '/drawer.html',
                    'BACKEND_JS': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/js.html',

                    'FRONTEND_TEMPLATES': SystemSetting.objects.get(title='Digithup').frontend_temp,
                    'FRONTEND_ASSETS': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/assets',
                    'FRONTEND_BASE': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/homebase.html',
                    'FRONTEND_HEAD': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/head.html',
                    'FRONTEND_HEADER': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/header.html',
                    'FRONTEND_SLIDER': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/slider.html',
                    'FRONTEND_PLAYER': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/player.html',
                    'FRONTEND_VUE': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/vuejs.html',
                    'FRONTEND_SIDEBAR': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/sidebar.html',
                    'FRONTEND_BREADCRUMB': SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/common/breadcrumb.html',
                    'FRONTEND_BODY': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/content.html',
                    'FRONTEND_FOOTER': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/footer.html',
                    'FRONTEND_MODAL': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/modal.html',
                    'FRONTEND_JS': 'frontend/' + SystemSetting.objects.get(title='Digithup').frontend_temp + '/js.html',

                }
        else:
            return {

                'BACKEND_TEMPLATES': SystemSetting.objects.get(title='Digithup').backend_temp,

                'BACKEND_ASSETS': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/assets',
                'BACKEND_BASE': 'backend/' + SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/adminbase.html',
                'BACKEND_HEAD': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/head.html',
                'BACKEND_HEADER': 'backend/' + SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/header.html',
                'BACKEND_SLIDER': 'backend/' + SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/slider.html',
                'BACKEND_SIDEBAR': 'backend/' + SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/sidebar.html',
                'BACKEND_BREADCRUMB': SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/common/breadcrumb.html',
                'BACKEND_BODY': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/content.html',
                'BACKEND_FOOTER': 'backend/' + SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/footer.html',
                'BACKEND_DRAWER': 'backend/' + SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/drawer.html',
                'BACKEND_JS': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/js.html',

                'FRONTEND_TEMPLATES': SystemSetting.objects.get(title='Digithup').frontend_temp,
                'FRONTEND_ASSETS': 'frontend/' + SystemSetting.objects.get(title='Digithup').frontend_temp + '/assets',
                'FRONTEND_BASE': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').frontend_temp + '/homebase.html',
                'FRONTEND_HEAD': 'frontend/' + SystemSetting.objects.get(title='Digithup').frontend_temp + '/head.html',
                'FRONTEND_HEADER': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').frontend_temp + '/header.html',
                'FRONTEND_SLIDER': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').frontend_temp + '/slider.html',
                'FRONTEND_PLAYER': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').frontend_temp + '/player.html',
                'FRONTEND_VUE': 'frontend/' + SystemSetting.objects.get(title='Digithup').frontend_temp + '/vuejs.html',
                'FRONTEND_SIDEBAR': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').frontend_temp + '/sidebar.html',
                'FRONTEND_BREADCRUMB': SystemSetting.objects.get(
                    title='Digithup').frontend_temp + '/common/breadcrumb.html',
                'FRONTEND_BODY': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').frontend_temp + '/content.html',
                'FRONTEND_FOOTER': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').frontend_temp + '/footer.html',
                'FRONTEND_MODAL': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').frontend_temp + '/modal.html',
                'FRONTEND_JS': 'frontend/' + SystemSetting.objects.get(title='Digithup').frontend_temp + '/js.html',

            }






    except Exception as e:
        print('TEMPLATES Error', e)
        return {
            'BASE_USE': 'good',
            'TEMPLATES_USE': 'good',
            'FOOTER_USE': 'good',
            'JS_USE': 'good',
        }


def admin_chart(request):
    try:
        order = BlogArticle.objects.values('title', 'circuit', 'first_session')

        data = {
            'data': [
                {
                    'title': item['title'],
                    'total': float(item['total']),
                    'first_session': item['first_session'],
                }
                for item in order
            ]
        }

        return {

            'admin_orders_location': data,

        }
    except Exception as e:
        return {

            'admin_orders_location': None,

        }


def user_processors(request):
    if not request.user.is_authenticated:
        return {
            'user_address': None,
            'user_mode': None,
            'wish_count': None,
            'active_currency': None,

        }
    try:
        employee_access = None


        current_user = User.objects.get(id=request.user.id)
        if current_user.access_level == 'Employee':

            access = 'Employee'

        elif current_user.access_level == 'Owner':
            access = 'Owner'
        elif current_user.access_level == 'ThirdPartyService':
            access = 'ThirdPartyService'
        elif current_user.access_level == 'Customer':
            access = 'Customer'
        elif current_user.access_level == 'SuperAdmin':
            access = 'SuperAdmin'
        else:
            access = None
        print('UserSetting', access, employee_access)
        return {
            'user_access': access,
            'employee_access': employee_access,
        }
    except BaseException as e:
        print('UserSetting', e)
        return {
            'user_access': None,
            'employee_access': None,

        }


def notifications(request):
    one_week_ago = datetime.now() - timedelta(days=1)
    one_week_next = datetime.now() + timedelta(days=7)
    try:
        if not request.user.is_authenticated:
            return {
                'admin_notifications': None,
            }
        user = User.objects.get(id=request.user.id)
        context_notifications = Notification.objects.filter(receiver_model=ContentType.objects.get(model='User'),
                                                            receiver_id=user.id,
                                                            is_read=False, notification_time__gte=one_week_ago,
                                                            notification_time__lt=one_week_next).order_by('-id')[:4]
        notification_count = Notification.objects.filter(receiver_model=ContentType.objects.get(model='User'),
                                                         receiver_id=user.id,
                                                         is_read=False, notification_time__gte=one_week_ago,
                                                         notification_time__lt=one_week_next).count()
        allnotifications = Notification.objects.all()

        return {
            'context_notifications': context_notifications,
            'notification_count': notification_count,
            'notifications': allnotifications
        }



    except Exception as e:
        print('notification context error ', e)
        admin = User.objects.get(is_superuser=True)
        if not request.user.is_authenticated:
            return {
                'admin_notifications': request.user.notifications.filter(is_read=False, to_user=admin,
                                                                         extra_time__gte=one_week_ago,
                                                                         extra_time__lt=one_week_next),
                'seller_notifications': None,
                'deliver_notifications': None,

            }
        admin = User.objects.filter(is_superuser=True)

        if request.user.is_authenticated and admin:
            return {'admin_notifications': None}


def admin_summary(request):
    try:
        article_view = BlogArticle.objects.filter(pub_type='Publish').aggregate(TOTAL=Sum('views'))['TOTAL']
        all_user = User.objects.all()
        return {
            # 'admin_earnings_total': Order.objects.filter(status='New').aggregate(total=sum('total')),
            # 'admin_earnings_total': Order.objects.aggregate(total_price=Sum('total')),
            'admin_article_view': article_view,
            'all_user': all_user,

        }
    except Exception as e:

        return {
            # 'admin_earnings_total':  Order.objects.aggregate(total=Sum('total')),
            'admin_article_view': None,
            'admin_products_count': None,
            'all_user': None,

        }



