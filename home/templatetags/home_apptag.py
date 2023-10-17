from django import template
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from apps.catalog.models.models import Categories
from core.models.shop import ShopCart
register = template.Library()


@register.simple_tag
def categorylist():
    return Categories.objects.all()

@register.simple_tag
def set_user_preferences(request):
    lasturl = request.META.get('HTTP_REFERER')
    html = HttpResponseRedirect(lasturl)
    if request.COOKIES.get('UserPreferences'):
        html.set_cookie('UserPreferences', 'User Preferences')
        value = int(request.COOKIES.get('UserPreferences'))
        dark = request.COOKIES.get('UserPreferences')
        html.set_cookie('UserPreferences', value + 1)
    else:
        value = 1
        dark = 0
        html.set_cookie('UserPreferences', value)
    html.set_cookie('UserPreferences', dark)
    return html


@register.simple_tag
def get_user_preferences(request):
    if request.COOKIES.get('UserPreferences') is None:
        return render(request, 'front/index.html')
    value = request.COOKIES.get('UserPreferences')
    text = request.COOKIES.get('dataflair')
    html = HttpResponse(
        "<center><h1>{0}<br>You have requested this page {1} times</h1></center>".format(text, value))
    html.set_cookie('UserPreferences', int(value) + 1)
    return html






@register.simple_tag
def shopcartcount(userid):
    return ShopCart.objects.filter(user_id=userid).count()


@register.simple_tag
def shopcart(userid):
    return ShopCart.objects.filter(user_id=userid)
