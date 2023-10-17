import os
import uuid
from uuid import uuid4

from django.shortcuts import render
from django.utils.crypto import get_random_string
from django.utils.deconstruct import deconstructible

from core.models.localization import Governorates, City


def LoadCitiesHelper(request):
    country_id = request.GET.get('country')
    print(country_id)
    governorates = Governorates.objects.filter(country_id=country_id).order_by('name')
    governorates_id = request.GET.get('governorates')
    print(governorates_id)
    cities = City.objects.filter(governorates_id=governorates_id).order_by('name')
    context = {
        'governorates': governorates,
        'cities': cities,
    }
    return render(request, 'city_dropdown_list_options.html', context)


def file_upload(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'ATO-{get_random_string(5).upper()}'
    sub_folder = 'file'
    if ext.lower() in ["jpg", "png", "gif", "jpeg", "bmp", "svg", "webp", "tiff", "tif", "jfif", "jpe"]:
        sub_folder = "avatar"
    if ext.lower() in ["pdf", "docx","doc", "xlsx", "xls", "pptx", "ppt","zip", "rar", "7z", "tar", "gz", "bz2", "bz", "7z", "tar.gz", "tar.bz2", "tar.bz", "tar.7z"]:
        sub_folder = "document"
    return os.path.join(sub_folder, filename)



@deconstructible
class UploadToPathAndRename(object):

    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # get filename
        if instance.pk:
            filename = '{}.{}'.format(instance.pk, ext)
        else:
            # set filename as random string
            filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.sub_path, filename)




# Read only the domain title of the current URL
def getCurrentDoamin(request):
    domain_name = request.get_host()
    domain_path = request.get_host() + request.path
    domain_scheme_path = request._current_scheme_host + request.path
    domain_scheme = request._current_scheme_host
    print('domain' ,domain_scheme ,'::',domain_scheme_path,'::', domain_path , '::',domain_name)
    return {'domain_name': domain_name, 'domain_path': domain_path, 'domain_scheme': domain_scheme,}

# Read the domain title with the path



def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"

    sub_folder = 'file'
    if ext.lower() in ["jpg", "png", "gif", "jpeg", "bmp", "svg", "webp", "tiff", "tif", "jfif", "jpe"]:
        sub_folder = "images"
    if ext.lower() in ["pdf", "docx", "doc", "xlsx", "xls", "pptx", "ppt", "zip", "rar", "7z", "tar", "gz", "bz2", "bz",
                       "7z", "tar.gz", "tar.bz2", "tar.bz", "tar.7z"]:
        sub_folder = "document"
    if ext.lower() in ["mo3"]:
        sub_folder = "audio"
    else:
        sub_folder  = "other"
    return os.path.join(sub_folder, filename)