from calendar import monthrange
from datetime import datetime, date
from time import timezone

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView


from core.models.blog import BlogServices, CommonTags, BlogCategories, BlogArticle
from core.models.core import CommonMediaFiles
from core.models.people import Employee
from home.views.views import FRONTEND_TEMPLATES


##########################      Services Home            ################################


def FrontBookingAppointmentDoctor(request,slug):
    doctor = Employee.objects.get(role='Doctor',slug=slug)


    current_month = date.today().month
    last_day_of_month = monthrange(date.today().year, current_month)[1]
    print('last_day_of_month',last_day_of_month)
    day_list = []
    for day in range(date.today().day, last_day_of_month+1):
        day_name = datetime.strptime(str(day), "%d").strftime("%A")
        print('day_name', day_name, day, current_month)
        day_list.append( {"day": day, "name": day_name, })
    print('day_list', day_list, )


    context = {
        'doctor': doctor,
        'doctor_slug': doctor.slug,

        'day_list': day_list,

    }
    return render(request, f'{FRONTEND_TEMPLATES}/booking/booking.html',context )
def front_service_detail(request, slug):
    service = get_object_or_404(BlogServices, slug=slug,service_type='Service')
    hero_image = CommonMediaFiles.objects.get(Q(owner_id=service.id), type='hero')
    video = CommonMediaFiles.objects.get(Q(owner_id=service.id), type='video')
    video_cover= CommonMediaFiles.objects.get(Q(owner_id=service.id), type='video')
    images = CommonMediaFiles.objects.filter(Q(owner_id=service.id), type='image')
    tags  = CommonTags.objects.filter(services_tags=service)
    print(tags)
    context = {
        'service': service,
        'hero':hero_image,
        'video':video,
        'video_cover': video_cover,
        'images': images,
        'tags': tags,
    }
    return render(request, f'{FRONTEND_TEMPLATES}/labtest/service-details.html', context)


def front_portfolio(request):
    portfolios = BlogServices.objects.filter(service_type='Portfolio')
    portfolio_list = []
    for portfolio in portfolios:
        cover = CommonMediaFiles.objects.get(Q(owner_id=portfolio.id), type='hero')
        data = {'portfolio': portfolio, 'cover': cover, }
        portfolio_list.append(data)
    categories = BlogCategories.objects.all()
    context = {
        'portfolios': portfolio_list,
        'categories': categories,
    }
    return render(request, f'{FRONTEND_TEMPLATES}/labtest/portfolio.html',context )
def front_portfolio_detail(request, slug):
    portfolio = get_object_or_404(BlogServices, slug=slug,service_type='Service')
    hero_image = CommonMediaFiles.objects.get(Q(owner_id=portfolio.id), type='hero')
    video = CommonMediaFiles.objects.get(Q(owner_id=portfolio.id), type='video')
    video_cover= CommonMediaFiles.objects.get(Q(owner_id=portfolio.id), type='video')
    images = CommonMediaFiles.objects.filter(Q(owner_id=portfolio.id), type='image')
    tags  = CommonTags.objects.filter(services_tags=portfolio)
    print(tags)
    context = {
        'portfolio': portfolio,
        'hero':hero_image,
        'video':video,
        'video_cover': video_cover,
        'images': images,
        'tags': tags,
    }
    return render(request, f'{FRONTEND_TEMPLATES}/labtest/portfolio-details.html', context)

def front_work(request):
    works = BlogServices.objects.filter(service_type='Work')
    work_list = []
    for work in works:
        cover = CommonMediaFiles.objects.get(owner_model=ContentType.objects.get(model='BlogServices')
                                             , owner_id=work.id, type='hero')
        data= {'work':work,'cover':cover,}
        work_list.append(data)
    categories = BlogCategories.objects.all()
    context = {
        'works': work_list,
        'categories': categories,
    }
    return render(request, f'{FRONTEND_TEMPLATES}/labtest/work.html',context)
def front_work_detail(request, slug):
    work = get_object_or_404(BlogServices, slug=slug,service_type='Work')

    hero_image = CommonMediaFiles.objects.get(owner_model=ContentType.objects.get(model='BlogServices'),
                                              owner_id=work.id, type='hero')
    video = CommonMediaFiles.objects.get(owner_model=ContentType.objects.get(model='BlogServices'), owner_id=work.id,
                                         type='video')
    images = CommonMediaFiles.objects.filter(owner_model=ContentType.objects.get(model='BlogServices'),
                                             owner_id=work.id, type='image')
    works = BlogServices.objects.filter(service_type='Product')

    categories = BlogCategories.objects.all()
    tags = CommonTags.objects.all()
    articles = BlogArticle.objects.all()
    calendars = datetime.now().month
    work_list = []
    for work in works:
        cover = CommonMediaFiles.objects.get(owner_model=ContentType.objects.get(model='BlogServices')
                                             , owner_id=work.id, type='hero')
        data = {'work': work, 'cover': cover, }
        work_list.append(data)
    context = {
        'work': work,
        'hero_image':hero_image,
        'video':video,
        'images': images,
        'works':work_list,
        'categories':categories,
        'tags': tags,
        'articles':articles,
        'calendars': calendars,
    }
    return render(request, f'{FRONTEND_TEMPLATES}/labtest/work-details.html', context)
def front_package(request):
    return render(request, f'{FRONTEND_TEMPLATES}/labtest/package.html', )


def front_product(request):
    works = BlogServices.objects.filter(service_type='Product')
    categories = BlogCategories.objects.all()
    work_list = []
    for work in works:
        cover = CommonMediaFiles.objects.get(owner_model=ContentType.objects.get(model='BlogServices')
    ,owner_id=work.id, type='hero')
        data= {'work':work,'cover':cover,}
        work_list.append(data)
    categories = BlogCategories.objects.all()
    context = {
        'products': work_list,
        'categories': categories,

    }
    return render(request, f'{FRONTEND_TEMPLATES}/product/product.html',context)
def front_product_detail(request, slug):
    work = get_object_or_404(BlogServices, slug=slug,service_type='Product')

    hero_image = CommonMediaFiles.objects.get(owner_model=ContentType.objects.get(model='BlogServices'),owner_id=work.id, type='hero')
    video = CommonMediaFiles.objects.get(owner_model=ContentType.objects.get(model='BlogServices'),owner_id=work.id, type='video')
    images = CommonMediaFiles.objects.filter(owner_model=ContentType.objects.get(model='BlogServices'),owner_id=work.id, type='image')
    works = BlogServices.objects.filter(service_type='Product')

    categories = BlogCategories.objects.all()
    tags = CommonTags.objects.all()
    articles = BlogArticle.objects.all()
    calendars = datetime.now().month
    work_list = []
    for work in works:
        cover = CommonMediaFiles.objects.get(owner_model=ContentType.objects.get(model='BlogServices')
                                             , owner_id=work.id, type='hero')
        data = {'work': work, 'cover': cover, }
        work_list.append(data)
    context = {
        'work': work,
        'hero_image':hero_image,
        'video':video,
        'images': images,
        'works':work_list,
        'categories':categories,
        'tags': tags,
        'articles':articles,
        'calendars': calendars,
    }
    return render(request, f'{FRONTEND_TEMPLATES}/product/details.html', context)

def FrontBookAppointment(request):
    services = BlogServices.objects.filter(service_type='Service')
    service_list = []
    for service in services:
        cover = CommonMediaFiles.objects.get(Q(owner_id=service.id), type='hero')
        data = {'service': service, 'cover': cover, }
        service_list.append(data)
    categories = BlogCategories.objects.all()
    context = {
        'labtest': service_list,
        'categories': categories,
    }
    return render(request, f'{FRONTEND_TEMPLATES}/labtest/book-appointment.html',context )