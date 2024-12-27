"""digit_sport URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt import views as jwt_views
from two_factor.urls import urlpatterns as tf_urls
from core.sitemaps import ArticleSitemap

sitemaps = {'blog': ArticleSitemap,

            }

schema_view = get_schema_view(openapi.Info(title="Digithup API", default_version='v1', description="Api For App",
                                           terms_of_service="https://www.digithup.com/en/",
                                           contact=openapi.Contact(email="info@digithup.com"),
                                           license=openapi.License(name="BSD License"), ), public=True,
                              permission_classes=[permissions.AllowAny], )

urlpatterns = [path('i18n/', include('django.conf.urls.i18n')),

               path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
               path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
                path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
               path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),

               path('dj-rest-auth/', include('dj_rest_auth.urls')),
               path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
               path('', include(tf_urls)),
               path('api/', include('api.v3.urls', namespace='APIV3')),


               ]

urlpatterns += i18n_patterns(

    path('dashboard/', include('core.urls'), name='core'),
    path('dashboard/', include('apps.catalog.urls'), name='catalog'),
    path('dashboard/sport/', include('apps.sport.urls'), name='sport'),
    path('dashboard/', include('apps.wallet.urls'), name='wallet'),
    path('', include('home.urls'), name='home'),
    path('', include('user.urls', namespace='user')),

    # path('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
    prefix_default_language=True

)

handler404 = "home.views.views.error404"
handler500 = 'home.views.views.server_error_view'
handle403 = 'home.views.views.permission_denied_view'

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r'^rosetta/', include('rosetta.urls'))]