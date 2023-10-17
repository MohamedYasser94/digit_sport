import logging
import random
import string
from hashlib import sha256
from urllib.parse import urljoin
from datetime import datetime
from django.http import JsonResponse
import requests
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.functional import Promise
from qrcode.compat.pil import Image
from urllib3.util import Url
import qrcode
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from apps.catalog.models.models import Products
from core.models.core import CommonUrlShortener
from digit_sport import settings
import glob
import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, PageBreak
from reportlab.lib.units import inch
logger = logging.getLogger(__name__)

from django.core.mail import EmailMessage
import os

class Util:
  @staticmethod
  def send_email(data):
    email = EmailMessage(
      subject=data['subject'],
      body=data['body'],
      from_email=os.environ.get('EMAIL_FROM'),
      to=[data['to_email']]
    )
    email.send()
# def AdminGetCurrentTime(request):
#     now = datetime.now()
#     return JsonResponse({'time': now.strftime("%H:%M:%S")})


def get_user_channel_name(user_id):
    return f"user_{user_id}"


def get_sha256(str):
    m = sha256(str.encode('utf-8'))
    return m.hexdigest()


def cache_decorator(expiration=3 * 60):
    def wrapper(func):
        def news(*args, **kwargs):
            try:
                view = args[0]
                key = view.get_cache_key()
            except BaseException:
                key = None
            if not key:
                unique_str = repr((func, args, kwargs))

                m = sha256(unique_str.encode('utf-8'))
                key = m.hexdigest()
            value = cache.get(key)
            if value is not None:
                # logger.info('cache_decorator get cache:%s key:%s' % (func.__name__, key))
                if str(value) == '__default_cache_value__':
                    return None
                else:
                    return value
            else:
                logger.info(
                    'cache_decorator set cache:%s key:%s' %
                    (func.__name__, key))
                value = func(*args, **kwargs)
                if value is None:
                    cache.set(key, '__default_cache_value__', expiration)
                else:
                    cache.set(key, value, expiration)
                return value

        return news

    return wrapper


def expire_view_cache(path, servername, serverport, key_prefix=None):
    '''
    刷新视图缓存
    :param path:url路径
    :param servername:host
    :param serverport:端口
    :param key_prefix:前缀
    :return:是否成功
    '''
    from django.http import HttpRequest
    from django.utils.cache import get_cache_key

    request = HttpRequest()
    request.META = {'SERVER_NAME': servername, 'SERVER_PORT': serverport}
    request.path = path

    key = get_cache_key(request, key_prefix=key_prefix, cache=cache)
    if key:
        logger.info('expire_view_cache:get key:{path}'.format(path=path))
        if cache.get(key):
            cache.delete(key)
        return True
    return False


class CommonMarkdown:
    @staticmethod
    def _convert_markdown(value):
        import markdown
        md = markdown.Markdown(
            extensions=[
                'extra',
                'codehilite',
                'toc',
                'tables',
            ]
        )
        body = md.convert(value)
        toc = md.toc
        return body, toc

    @staticmethod
    def get_markdown_with_toc(value):
        body, toc = CommonMarkdown._convert_markdown(value)
        return body, toc

    @staticmethod
    def get_markdown(value):
        body, toc = CommonMarkdown._convert_markdown(value)
        return body


def generate_code() -> str:
    """生成随机数验证码"""
    return ''.join(random.sample(string.digits, 6))


def parse_dict_to_url(dict):
    from urllib.parse import quote
    url = '&'.join(['{}={}'.format(quote(k, safe='/'), quote(v, safe='/'))
                    for k, v in dict.items()])
    return url




def delete_view_cache(prefix, keys):
    from django.core.cache.utils import make_template_fragment_key
    key = make_template_fragment_key(prefix, keys)
    cache.delete(key)


class CustomStorage(FileSystemStorage):
    """Custom storage for django_ckeditor_5 images."""

    location = os.path.join(settings.MEDIA_ROOT, "django_ckeditor_5")
    base_url = urljoin(settings.MEDIA_URL, "django_ckeditor_5/")


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
      return str(obj) if isinstance(obj,Promise) else super().default(obj)


def AdminCommonUrlShortener(request,title,keyword,url,owner_model,owner_id):
    slug = ''.join(random.choice(string.ascii_letters)
                   for x in range(10))
    print('url',url)
    short_url = Url(path=url, slug=slug)
    try:
        shortener_object = CommonUrlShortener.objects.get( owner_model=ContentType.objects.get(model=owner_model), owner_id=owner_id)
        shortener_object.title=title
        shortener_object.keyword=keyword
        shortener_object.url=url
        shortener_object.short_url=short_url
        shortener_object.save()
    except:

        shortener_object = CommonUrlShortener(
            title=title, keyword=keyword, url=url, short_url=short_url,
            owner_model=ContentType.objects.get(model=owner_model), owner_id=owner_id
        )
        shortener_object.save()


def product_qrcode(request, product_id):
    # Get the product from the database
    product = get_object_or_404(Products, pk=product_id)

    # Generate the QR code image using the product URL
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(product.url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Serve the QR code image as an HTTP response
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response


def get_qrcode(request, url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response


def get_qrcode_with_logo(request, url, logo_url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.convert("RGBA")
    icon = Image.open(requests.get(logo_url, stream=True).raw)
    img_w, img_h = img.size
    factor = 4
    size_w = int(img_w / factor)
    size_h = int(img_h / factor)
    icon_w, icon_h = icon.size
    if icon_w > size_w:
        icon_w = size_w
    if icon_h > size_h:
        icon_h = size_h
    icon = icon.resize((icon_w, icon_h), Image.ANTIALIAS)
    w = int((img_w - icon_w) / 2)
    h = int((img_h - icon_h) / 2)
    icon = icon.convert("RGBA")
    img.paste(icon, (w, h), icon)
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response









