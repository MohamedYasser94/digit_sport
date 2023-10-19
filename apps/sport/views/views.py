from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from apps.sport.forms.forms import *
from apps.sport.models.models import *
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import authenticated_staf, staff_only

User = get_user_model()


##########################  Sport ################################


##########################  Sport Category ################################

@authenticated_staf
@staff_only
def AdminSportCategoryList(request):
    categories = SportCategory.objects.all()

    if request.method == "POST":
        category_form = AdminSportCategoryForm(request.POST or None, request.FILES or None)

        if category_form:
            title = request.POST.get('title')
            category = request.POST.get('category')
            keyword = request.POST.get('keyword')
            image = request.FILES.get('image')
            image_url = request.POST.get('image_url')

            if category == None or category == '':
                category = None
            else:
                category = SportCategory.objects.get(id=category)

            category_object = SportCategory(title=title, parent=category, keyword=keyword, image=image,
                                            image_url=image_url, status='Active')

            category_object.save()
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
def AdminSportCategoryUpdate(request, slug):
    category = SportCategory.objects.get(slug=slug)

    if request.method == "POST":
        category_form = AdminSportCategoryForm(request.POST or None, request.FILES or None, instance=category)

        if category_form:
            title = request.POST.get('title')
            category = request.POST.get('category')
            keyword = request.POST.get('keyword')
            image = request.FILES.get('image')
            image_url = request.POST.get('image_url')
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
            category_object.image_url = image_url
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
def AdminSportCategoryArchive(request, slug):
    category = SportCategory.objects.get(slug=slug)
    if request.method == 'POST':
        category.status = 'Archive'
        category.save()
        messages.success(request, _("Category Archive Successfully"), extra_tags='Category')
        return HttpResponseRedirect(reverse_lazy('sport:AdminSportCategoryList'))


@authenticated_staf
@staff_only
def AdminSportCategoryDelete(request, slug):
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


##########################  Sport ################################

@authenticated_staf
@staff_only
def AdminSportList(request):
    sports = Sport.objects.all()

    if request.method == "POST":
        sport_form = AdminSportForm(request.POST or None, request.FILES or None)

        if sport_form:
            title = request.POST.get('title')
            category = request.POST.get('category')
            keyword = request.POST.get('keyword')
            image = request.FILES.get('image')
            image_url = request.POST.get('image_url')

            if category == None or category == '':
                category = None
            else:
                category = SportCategory.objects.get(id=category)

            sport_object = Sport(title=title, parent=category, keyword=keyword, image=image, image_url=image_url,
                                 status='Active')

            sport_object.save()
            messages.success(request, _("Sport Add Successfully"), extra_tags='Sport')

            return HttpResponseRedirect(reverse_lazy('sport:AdminSportList'))
        else:

            messages.error(request, _("Sport Not Add , Please Try Again"), extra_tags='Sport')

    else:
        context = {'sports': sports, 'sport_form': AdminSportForm(), 'current_page': _('Sports')

                   }
        return render(request, f'{BACKEND_TEMPLATES}/sport/sport/admin.html', context)
    context = {'sports': sports, 'sport_form': AdminSportForm(), 'current_page': _('Sports')

               }
    return render(request, f'{BACKEND_TEMPLATES}/sport/sport/admin.html', context)


@authenticated_staf
@staff_only
def AdminSportUpdate(request, slug):
    sport = Sport.objects.get(slug=slug)

    if request.method == "POST":
        title = request.POST.get('title')
        category = request.POST.get('category')
        keyword = request.POST.get('keyword')
        image = request.FILES.get('image')
        image_url = request.POST.get('image_url')

        if category == None or category == '' or category == 'None':
            category = None
        else:
            category = SportCategory.objects.get(id=category)
        if image == None or image == '':
            image = sport.image
        else:
            image = image

        sport_object = Sport.objects.get(slug=slug)
        sport_object.title = title
        sport_object.parent = category
        sport_object.keyword = keyword
        if image == None or image == '':
            sport_object.image = sport.image
        else:
            sport_object.image = image
        sport_object.image_url = image_url
        sport_object.save()

        messages.success(request, _("Sport Update Successfully"), extra_tags='Sport')

        return HttpResponseRedirect(reverse_lazy('sport:AdminSportList'))
    else:

        messages.error(request, _("Sport Not Update , Please Try Again"), extra_tags='Sport')
    context = {'sport': sport, 'sport_form': AdminSportForm(instance=sport), 'current_page': _('Update'),
               'prev_Page': _('Sports'), }
    return render(request, f'{BACKEND_TEMPLATES}/sport/sport/update.html', context)


@authenticated_staf
@staff_only
def AdminSportArchive(request, slug):
    sport = Sport.objects.get(slug=slug)
    if request.method == 'POST':
        sport.status = 'Archive'
        sport.save()
        messages.success(request, _("Sport Archive Successfully"), extra_tags='Sport')
        return HttpResponseRedirect(reverse_lazy('sport:AdminSportList'))
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminSportList'))


@authenticated_staf
@staff_only
def AdminSportDelete(request, slug):
    sport = Sport.objects.get(slug=slug)

    if request.method == "POST":
        sport.delete()

        messages.success(request, _("Sport Delete Successfully"), extra_tags='Sport')

        return HttpResponseRedirect(reverse_lazy('sport:AdminSportList'))
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminSportList'))


##########################  Leagues ################################
@authenticated_staf
@staff_only
def AdminLeaguesList(request):
    leagues = Leagues.objects.all()

    if request.method == "POST":
        leagues_form = AdminLeaguesForm(request.POST or None, request.FILES or None)

        if leagues_form:
            name = request.POST.get('name')
            sport = request.POST.get('sport')
            category = request.POST.get('category')
            sub_category = request.POST.get('sub_category')
            country = request.POST.get('country')
            short_code = request.POST.get('short_code')
            image = request.FILES.get('image')
            image_url = request.POST.get('image_url')
            type = request.POST.get('type')
            keyword = request.POST.get('keyword')
            image = request.FILES.get('image')
            image_url = request.POST.get('image_url')

            if sport == None or sport == '':
                sport = None
            else:
                sport = Sport.objects.get(id=sport)

            if category == None or category == '':
                category = None
            else:
                category = SportCategory.objects.get(id=category)

            if sub_category == None or sub_category == '':
                sub_category = None
            else:
                sub_category = SportCategory.objects.get(id=sub_category)

            leagues_object = Leagues(name=name, sport=sport, category=category, sub_category=sub_category,
                                     country=country, short_code=short_code, image=image, image_url=image_url, )

            leagues_object.save()
            messages.success(request, _("Leagues Add Successfully"), extra_tags='Leagues')

            return HttpResponseRedirect(reverse_lazy('sport:AdminLeaguesList'))
        else:

            messages.error(request, _("Leagues Not Add , Please Try Again"), extra_tags='Leagues')


    else:
        context = {'leagues': leagues, 'leagues_form': AdminLeaguesForm(), 'current_page': _('Leagues')

                   }
        return render(request, f'{BACKEND_TEMPLATES}/sport/leagues/admin.html', context)

    context = {'leagues': leagues, 'leagues_form': AdminLeaguesForm(), 'current_page': _('Leagues')}
    return render(request, f'{BACKEND_TEMPLATES}/sport/leagues/admin.html', context)


@authenticated_staf
@staff_only
def AdminLeaguesUpdate(request, slug):
    league = Leagues.objects.get(slug=slug)

    if request.method == "POST":
        name = request.POST.get('name')
        sport = request.POST.get('sport')
        category = request.POST.get('category')
        sub_category = request.POST.get('sub_category')
        country = request.POST.get('country')
        short_code = request.POST.get('short_code')
        image = request.FILES.get('image')
        image_url = request.POST.get('image_url')
        type = request.POST.get('type')
        keyword = request.POST.get('keyword')
        image = request.FILES.get('image')
        image_url = request.POST.get('image_url')

        if sport == None or sport == '':
            sport = None
        else:
            sport = Sport.objects.get(id=sport)

        if category == None or category == '':
            category = None
        else:
            category = SportCategory.objects.get(id=category)

        if sub_category == None or sub_category == '':
            sub_category = None
        else:
            sub_category = SportCategory.objects.get(id=sub_category)

        leagues_object = Leagues.objects.get(slug=slug)
        leagues_object.name = name
        leagues_object.sport = sport
        leagues_object.category = category
        leagues_object.sub_category = sub_category
        leagues_object.country = country
        leagues_object.short_code = short_code
        leagues_object.image = image
        leagues_object.image_url = image_url
        leagues_object.save()

        messages.success(request, _("Leagues Update Successfully"), extra_tags='Leagues')

        return HttpResponseRedirect(reverse_lazy('sport:AdminLeaguesList'))
    else:

            messages.error(request, _("Leagues Not Update , Please Try Again"), extra_tags='Leagues')

    context = {'league': league, 'leagues_form': AdminLeaguesForm(instance=league), 'current_page': _('Update'),
                'prev_Page': _('Leagues'), }
    return render(request, f'{BACKEND_TEMPLATES}/sport/leagues/update.html', context)


@authenticated_staf
@staff_only
def AdminLeaguesArchive(request, slug):
    league = Leagues.objects.get(slug=slug)
    if request.method == 'POST':
        league.status = 'Archive'
        league.save()
        messages.success(request, _("Leagues Archive Successfully"), extra_tags='Leagues')
        return HttpResponseRedirect(reverse_lazy('sport:AdminLeaguesList'))
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminLeaguesList'))


@authenticated_staf
@staff_only
def AdminLeaguesDelete(request, slug):
    league = Leagues.objects.get(slug=slug)

    if request.method == "POST":
        league.delete()

        messages.success(request, _("Leagues Delete Successfully"), extra_tags='Leagues')

        return HttpResponseRedirect(reverse_lazy('sport:AdminLeaguesList'))
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminLeaguesList'))



##########################  Season ################################
@authenticated_staf
@staff_only
def AdminSeasonList(request):
    seasons = Season.objects.all()

    if request.method == "POST":
        season_form = AdminSeasonForm(request.POST or None, request.FILES or None)

        if season_form:
            name = request.POST.get('name')
            league = request.POST.get('league')
            keyword = request.POST.get('keyword')
            starting_at = request.POST.get('starting_at')
            ending_at = request.POST.get('ending_at')
            standings_recalculated_at = request.POST.get('standings_recalculated_at')
            games_in_current_week = request.POST.get('games_in_current_week')
            status = request.POST.get('status')

            if league == None or league == '':
                league = None
            else:
                league = Leagues.objects.get(id=league)

            season_object = Season(name=name, league=league, keyword=keyword, starting_at=starting_at,
                                        ending_at=ending_at, standings_recalculated_at=standings_recalculated_at,
                                     status=status)

            season_object.save()
            messages.success(request, _("Season Add Successfully"), extra_tags='Season')

            return HttpResponseRedirect(reverse_lazy('sport:AdminSeasonList'))
        else:

            messages.error(request, _("Season Not Add , Please Try Again"), extra_tags='Season')

    else:
        context = {'seasons': seasons, 'season_form': AdminSeasonForm(), 'current_page': _('Seasons')

                   }
        return render(request, f'{BACKEND_TEMPLATES}/sport/season/admin.html', context)



@authenticated_staf
@staff_only
def AdminSeasonUpdate(request, slug):
    season = Season.objects.get(slug=slug)

    if request.method == "POST":
        name = request.POST.get('name')
        league = request.POST.get('league')
        keyword = request.POST.get('keyword')
        starting_at = request.POST.get('starting_at')
        ending_at = request.POST.get('ending_at')
        standings_recalculated_at = request.POST.get('standings_recalculated_at')
        games_in_current_week = request.POST.get('games_in_current_week')
        status = request.POST.get('status')

        if league == None or league == '':
            league = None
        else:
            league = Leagues.objects.get(id=league)

        season_object = Season.objects.get(slug=slug)
        season_object.name = name
        season_object.league = league
        season_object.keyword = keyword
        season_object.starting_at = starting_at
        season_object.ending_at = ending_at
        season_object.standings_recalculated_at = standings_recalculated_at
        season_object.games_in_current_week = games_in_current_week
        season_object.status = status
        season_object.save()

        messages.success(request, _("Season Update Successfully"), extra_tags='Season')

        return HttpResponseRedirect(reverse_lazy('sport:AdminSeasonList'))
    else:

                messages.error(request, _("Season Not Update , Please Try Again"), extra_tags='Season')

    context = {'season': season, 'season_form': AdminSeasonForm(instance=season), 'current_page': _('Update'),
                'prev_Page': _('Seasons'), }
    return render(request, f'{BACKEND_TEMPLATES}/sport/season/update.html', context)


@authenticated_staf
@staff_only
def AdminSeasonArchive(request, slug):
    season = Season.objects.get(slug=slug)
    if request.method == 'POST':
        season.status = 'Archive'
        season.save()
        messages.success(request, _("Season Archive Successfully"), extra_tags='Season')
        return HttpResponseRedirect(reverse_lazy('sport:AdminSeasonList'))
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminSeasonList'))


@authenticated_staf
@staff_only
def AdminSeasonDelete(request, slug):
    season = Season.objects.get(slug=slug)

    if request.method == "POST":
        season.delete()

        messages.success(request, _("Season Delete Successfully"), extra_tags='Season')

        return HttpResponseRedirect(reverse_lazy('sport:AdminSeasonList'))
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminSeasonList'))


