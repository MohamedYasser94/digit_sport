from datetime import timezone

from django.contrib import messages

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


from apps.sport.forms.operations import *
from apps.sport.models.models import Sport

from core.models.core import CommonTranslate

from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import authenticated_staf, staff_only

User = get_user_model()








##########################  Sport Category ################################

@authenticated_staf
@staff_only
def AdminMatchReportList(request):
    matches = Match.objects.filter(status='Active',sport=Sport.objects.get(name='volleyball'))
    reports = MatchReport.objects.filter(status='Active')


    if request.method == "POST":
        report_form = AdminMatchReportForm(request.POST or None, request.FILES or None)

        if report_form:
            match = request.POST.get('match')



            report_object = MatchReport(match=match, status='Active')

            report_object.save()

            messages.success(request, _("Report Add Successfully"), extra_tags='Report')

            return HttpResponseRedirect(reverse_lazy('sport:AdminSportCategoryList'))
        else:

            messages.error(request, _("Report Not Add , Please Try Again"), extra_tags='Report')


    context = {'matches': matches, 'reports': reports, 'report_form': AdminMatchReportForm(), 'current_page': _('Report')


               }
    return render(request, f'{BACKEND_TEMPLATES}/sport/report/match/admin.html', context)


@authenticated_staf
@staff_only
def AdminMatchReportUpdate(request, slug):
    category = SportCategory.objects.get(slug=slug)

    if request.method == "POST":
        category_form = AdminSportCategoryForm(request.POST or None, request.FILES or None, instance=category)

        if category_form:
            title = request.POST.get('title')
            category = request.POST.get('category')
            keyword = request.POST.get('keyword')
            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')
            status = request.POST.get('status')
            print(request.POST)

            if category == None or category == '' or category == 'None':
                category = None
            else:
                category = SportCategory.objects.get(id=category)
            if image == None or image == '':
                image = category.image
            else:
                image = image

            category_object = SportCategory.objects.get(slug=slug)
            category_object.title = title
            category_object.parent = category
            category_object.keyword = keyword
            if image == None or image == '':
                category_object.image = category.image
            else:
                category_object.image = image
            category_object.image_path = image_path
            category_object.status = status
            category_object.save()

            messages.success(request, _("Category Update Successfully"), extra_tags='Category')

            return HttpResponseRedirect(reverse_lazy('sport:AdminSportCategoryList'))
        else:

            messages.error(request, _("Category Not Update , Please Try Again"), extra_tags='Category')

    else:
        context = {'category': category, 'category_form': AdminSportCategoryForm(instance=category),
                   'current_page': _('Update'), 'prev_Page': _('Categories'),
                   'prev_Page_link': reverse_lazy('sport:AdminSportCategoryList'),

                   }
        return render(request, f'{BACKEND_TEMPLATES}/sport/category/update.html', context)
    context = {'category': category, 'category_form': AdminSportCategoryForm(instance=category),
               'current_page': _('Update'), 'prev_Page': _('Categories'),
               'prev_Page_link': reverse_lazy('sport:AdminSportCategoryList'),

               }
    return render(request, f'{BACKEND_TEMPLATES}/sport/report/match/update.html', context)


@authenticated_staf
@staff_only
def AdminMatchReportArchive(request, slug):
    category = SportCategory.objects.get(slug=slug)
    if request.method == 'POST':
        category.status = 'Archive'
        category.save()
        messages.success(request, _("Category Archive Successfully"), extra_tags='Category')
        return HttpResponseRedirect(reverse_lazy('sport:AdminSportCategoryList'))


@authenticated_staf
@staff_only
def AdminMatchReportDelete(request, slug):

    category = SportCategory.objects.get(slug=slug)

    if request.method == "POST":
        category.delete()

        messages.success(request, _("Category Delete Successfully"), extra_tags='Category')

        return HttpResponseRedirect(reverse_lazy('press:AdminPressCategoriesList'))
    else:
        context = {'category': category,

                   'current_page': _('Delete'), 'prev_Page': _('Categories'),
                   'prev_Page_link': reverse_lazy('sport:AdminSportCategoryList'),

                   }
        return render(request, f'{BACKEND_TEMPLATES}/sport/report/match/admin.html', context)


##########################   Match Player Report ################################

@authenticated_staf
@staff_only
def AdminMatchPlayerReportList(request):
    categories = SportCategory.objects.all()

    if request.method == "POST":
        category_form = AdminSportCategoryForm(request.POST or None, request.FILES or None)

        if category_form:
            title = request.POST.get('title')
            category = request.POST.get('category')
            keyword = request.POST.get('keyword')
            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')

            if category == None or category == '':
                category = None
            else:
                category = SportCategory.objects.get(id=category)

            category_object = SportCategory(title=title, parent=category, keyword=keyword, image=image,
                                            image_path=image_path, status='Active')

            category_object.save()
            translate_object = CommonTranslate(title=title_tr, keyword=keyword_tr,
                                               owner_model=ContentType.objects.get(model='SportCategory'),
                                               owner_id=category_object.id)
            translate_object.save()
            messages.success(request, _("Category Add Successfully"), extra_tags='Category')

            return HttpResponseRedirect(reverse_lazy('sport:AdminSportCategoryList'))
        else:

            messages.error(request, _("Category Not Add , Please Try Again"), extra_tags='Category')

    else:
        context = {'categories': categories, 'category_form': AdminSportCategoryForm(), 'current_page': _('Categories')

                   }
        return render(request, f'{BACKEND_TEMPLATES}/sport/category/admin.html', context)
    context = {'categories': categories, 'category_form': AdminSportCategoryForm(), 'current_page': _('Categories')

               }
    return render(request, f'{BACKEND_TEMPLATES}/sport/category/admin.html', context)




@authenticated_staf
@staff_only
def AdminMatchPlayerReportUpdate(request, slug):
    category = SportCategory.objects.get(slug=slug)

    if request.method == "POST":
        category_form = AdminSportCategoryForm(request.POST or None, request.FILES or None, instance=category)

        if category_form:
            title = request.POST.get('title')
            category = request.POST.get('category')
            keyword = request.POST.get('keyword')
            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')
            status = request.POST.get('status')
            print(request.POST)

            if category == None or category == '' or category == 'None':
                category = None
            else:
                category = SportCategory.objects.get(id=category)
            if image == None or image == '':
                image = category.image
            else:
                image = image

            category_object = SportCategory.objects.get(slug=slug)
            category_object.title = title
            category_object.parent = category
            category_object.keyword = keyword
            if image == None or image == '':
                category_object.image = category.image
            else:
                category_object.image = image
            category_object.image_path = image_path
            category_object.status = status
            category_object.save()

            messages.success(request, _("Category Update Successfully"), extra_tags='Category')

            return HttpResponseRedirect(reverse_lazy('sport:AdminSportCategoryList'))
        else:

            messages.error(request, _("Category Not Update , Please Try Again"), extra_tags='Category')

    else:
        context = {'category': category, 'category_form': AdminSportCategoryForm(instance=category),
                   'current_page': _('Update'), 'prev_Page': _('Categories'),
                   'prev_Page_link': reverse_lazy('sport:AdminSportCategoryList'),

                   }
        return render(request, f'{BACKEND_TEMPLATES}/sport/category/update.html', context)
    context = {'category': category, 'category_form': AdminSportCategoryForm(instance=category),
               'current_page': _('Update'), 'prev_Page': _('Categories'),
               'prev_Page_link': reverse_lazy('sport:AdminSportCategoryList'),

               }
    return render(request, f'{BACKEND_TEMPLATES}/sport/category/update.html', context)



@authenticated_staf
@staff_only
def AdminMatchPlayerReportArchive(request, slug):
    category = SportCategory.objects.get(slug=slug)
    if request.method == 'POST':
        category.status = 'Archive'
        category.save()
        messages.success(request, _("Category Archive Successfully"), extra_tags='Category')
        return HttpResponseRedirect(reverse_lazy('sport:AdminSportCategoryList'))


@authenticated_staf
@staff_only
def AdminMatchPlayerReportDelete(request, slug):
    category = SportCategory.objects.get(slug=slug)

    if request.method == "POST":
        category.delete()

        messages.success(request, _("Category Delete Successfully"), extra_tags='Category')

        return HttpResponseRedirect(reverse_lazy('press:AdminPressCategoriesList'))
    else:
        context = {'category': category,

                   'current_page': _('Delete'), 'prev_Page': _('Categories'),
                   'prev_Page_link': reverse_lazy('sport:AdminSportCategoryList'),

                   }
        return render(request, f'{BACKEND_TEMPLATES}/sport/category/admin.html', context)