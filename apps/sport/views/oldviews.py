from datetime import timezone, datetime
import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

import os
import re
from OpenSSL.rand import status
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage,EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from apps.sport.forms.forms import *
from apps.sport.forms.operations import *
from apps.sport.models.models import *
from apps.sport.utils.pdf_parser import parse_match_report
from core.models.core import CommonTranslate
from core.views.notifications import AdminFcmNotifications
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
def AdminSportCategoryUpdate(request, slug):
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
            name = request.POST.get('name')
            keyword = request.POST.get('keyword')
            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')



            sport_object = Sport(name=name,  keyword=keyword, image=image, image_path=image_path,
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
        name = request.POST.get('name')
        country = request.POST.get('country')
        keyword = request.POST.get('keyword')
        image = request.FILES.get('image')
        image_path = request.POST.get('image_path')
        status = request.POST.get('status')


        if image == None or image == '':
            image = sport.image
        else:
            image = image

        sport_object = Sport.objects.get(slug=slug)
        sport_object.name = name
        sport_object.country = country
        sport_object.keyword = keyword
        if image == None or image == '':
            sport_object.image = sport.image
        else:
            sport_object.image = image
        sport_object.image_path = image_path
        sport_object.status = status
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

@authenticated_staf
@staff_only
def AdminSportByCountry(request, slug):
    sport = Sport.objects.get(slug=slug)
    country_list = Country_List
    leagues_list = []
    for key , value in country_list:
        leagues = Leagues.objects.filter(country=key,sport=sport).count()
        leagues_list.append({'country':value,'leagues':leagues})

    context = {'sport': sport, 'leagues_list': leagues_list, 'current_page': _('Sports')

               }
    return render(request, f'{BACKEND_TEMPLATES}/sport/sport/country.html', context)






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
            image_path = request.POST.get('image_path')
            keyword = request.POST.get('keyword')

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
                                     country=country, short_code=short_code, image=image, image_path=image_path,keyword=keyword )

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
def AdminLeaguesBySport(request, slug):
    sport = Sport.objects.get(slug=slug)
    leagues = Leagues.objects.filter(sport=sport)

    if request.method == "POST":
        leagues_form = AdminLeaguesForm(request.POST or None, request.FILES or None)

        if leagues_form:
            name = request.POST.get('name')
            gender = request.POST.get('gender')
            category = request.POST.get('category')
            short_code = request.POST.get('short_code')
            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')
            keyword = request.POST.get('keyword')


            if category == None or category == '':
                category = None
            else:
                category = SportCategory.objects.get(id=category)



            leagues_object = Leagues(name=name, sport=sport, category=category,
                                     country=sport.country,gender=gender, short_code=short_code, image=image, image_path=image_path,keyword=keyword )

            leagues_object.save()
            messages.success(request, _("Leagues Add Successfully"), extra_tags='Leagues')

            return HttpResponseRedirect(reverse_lazy('sport:AdminLeaguesBySport', kwargs={'slug': slug}))
        else:

            messages.error(request, _("Leagues Not Add , Please Try Again"), extra_tags='Leagues')
    context = {'leagues': leagues, 'leagues_form': AdminLeaguesForm(), 'current_page': _('Leagues'),
               'sport': sport}
    return render(request, f'{BACKEND_TEMPLATES}/sport/sport/leagues.html', context)

@authenticated_staf
@staff_only
def AdminLeaguesUpdate(request, slug):
    league = Leagues.objects.get(slug=slug)

    if request.method == "POST":
        leagues_form = AdminLeaguesForm(request.POST or None, request.FILES or None, instance=league)
        if leagues_form:
            name = request.POST.get('name')
            name_tr = request.POST.get('name_tr')
            sport = request.POST.get('sport')
            country = request.POST.get('country')
            short_code = request.POST.get('short_code')
            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')
            country_image = request.POST.get('country_image')
            currentseason = request.POST.get('currentseason')
            status= request.POST.get('status')

            if sport == None or sport == '':
                sport = None
            else:
                sport = Sport.objects.get(id=sport)
            leagues_object = Leagues.objects.get(slug=slug)
            leagues_object.name = name
            leagues_object.name_tr = name_tr
            leagues_object.sport = sport
            leagues_object.country = country
            leagues_object.short_code = short_code
            if image:
                leagues_object.image = image
            else:
                leagues_object.image = leagues_object.image
            leagues_object.image_path = image_path
            leagues_object.country_image = country_image
            leagues_object.currentseason = currentseason
            leagues_object.status = status
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



@authenticated_staf
@staff_only
def AdminLeaguesTeams(request, slug):
    league = Leagues.objects.get(slug=slug)
    teams = Teams.objects.filter(league=league)
    teams_form = AdminTeamsForm()
    context = {'league': league, 'teams': teams,
                'teams_form': teams_form,
               'current_page': _('Teams')}
    return render(request, f'{BACKEND_TEMPLATES}/sport/leagues/teams.html', context)


@authenticated_staf
@staff_only
def AdminMatchByLeague(request, slug):
    league = Leagues.objects.get(slug=slug)
    matches = Match.objects.filter(league=league).order_by('-start_time')
    matches_form = AdminMatchForm()
    context = {'league': league, 'matches': matches,
                'matches_form': matches_form,
               'current_page': _('Matches')}
    return render(request, f'{BACKEND_TEMPLATES}/sport/leagues/matches.html', context)

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
            is_current = request.POST.get('is_current')

            if is_current == None or is_current == '' or is_current == 'None' or is_current == 'No':
                is_current = False
            else:
                is_current = True



            if league == None or league == '':
                league = None
            else:
                league = Leagues.objects.get(id=league)

            title = f'{name} - {league.name}'

            season_object = Season(name=name,title=title, league=league, sport=league.sport,
                                   keyword=keyword, starting_at=starting_at,
                                        ending_at=ending_at, is_current=is_current,
                                     status='Active')

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
def AdminSeasonByLeague(request, slug):
    league = Leagues.objects.get(slug=slug)
    seasons = Season.objects.filter(league=league)

    if request.method == "POST":
        season_form = AdminSeasonForm(request.POST or None, request.FILES or None)

        if season_form:
            name = request.POST.get('name')
            is_current = request.POST.get('is_current')
            keyword = request.POST.get('keyword')
            starting_at = request.POST.get('starting_at')
            ending_at = request.POST.get('ending_at')
            standings_recalculated_at = request.POST.get('standings_recalculated_at')
            games_in_current_week = request.POST.get('games_in_current_week')
            status = 'Active'
            title = f'{name} - {league.name}'

            season_object = Season(name=name,title=title, league=league,sport=league.sport, keyword=keyword,is_current=is_current, starting_at=starting_at,
                                        ending_at=ending_at, standings_recalculated_at=standings_recalculated_at,
                                     games_in_current_week=games_in_current_week, status=status)

            season_object.save()
            messages.success(request, _("Season Add Successfully"), extra_tags='Season')

            return HttpResponseRedirect(reverse_lazy('sport:AdminSeasonByLeague', kwargs={'slug': slug}))
        else:

            messages.error(request, _("Season Not Add , Please Try Again"), extra_tags='Season')
    context = {'seasons': seasons, 'season_form': AdminSeasonForm(), 'current_page': _('Seasons'),
               'league': league}
    return render(request, f'{BACKEND_TEMPLATES}/sport/leagues/season.html', context)

@authenticated_staf
@staff_only
def AdminSeasonUpdate(request, slug):
    season = Season.objects.get(slug=slug)

    if request.method == "POST":
        season_form = AdminSeasonForm(request.POST or None, request.FILES or None, instance=season)
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
            title = f'{name} - {league.name}'
            season_object = Season.objects.get(slug=slug)
            season_object.name = name
            season_object.title = title
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




##########################  Stages ################################
@authenticated_staf
@staff_only
def AdminStagesList(request):
    stages = Stages.objects.all()

    if request.method == "POST":
        stages_form = AdminStagesForm(request.POST or None, request.FILES or None)

        if stages_form:
            name = request.POST.get('name')
            league = request.POST.get('league')
            keyword = request.POST.get('keyword')
            starting_at = request.POST.get('starting_at')
            ending_at = request.POST.get('ending_at')
            is_current = request.POST.get('is_current')

            if is_current == None or is_current == '' or is_current == 'None' or is_current == 'No':
                is_current = False
            else:
                is_current = True

            if league == None or league == '':
                league = None
            else:
                league = Leagues.objects.get(id=league)

            stage_object = Stages(name=name, league=league, keyword=keyword, starting_at=starting_at,
                                        ending_at=ending_at, is_current=is_current,
                                        status='Active')

            stage_object.save()
            messages.success(request, _("Stage Add Successfully"), extra_tags='Stage')

            return HttpResponseRedirect(reverse_lazy('sport:AdminStagesList'))
        else:

                messages.error(request, _("Stage Not Add , Please Try Again"), extra_tags='Stage')

    else:
        context = {'stages': stages, 'stages_form': AdminStagesForm(), 'current_page': _('Stages')

                   }
        return render(request, f'{BACKEND_TEMPLATES}/sport/stages/admin.html', context)


##########################  Group ################################
@authenticated_staf
@staff_only
def AdminGroupList(request):
    groups = Group.objects.all()

    if request.method == "POST":
        groups_form = AdminGroupForm(request.POST or None, request.FILES or None)

        if groups_form:
            name = request.POST.get('name')
            league = request.POST.get('league')
            season = request.POST.get('season')
            starting_at = request.POST.get('starting_at')
            ending_at = request.POST.get('ending_at')
            is_current = request.POST.get('is_current')


            if is_current == None or is_current == '' or is_current == 'None' or is_current == 'No':
                is_current = False
            else:
                is_current = True

            if league == None or league == '':
                league = None
            else:
                league = Leagues.objects.get(id=league)

            if season == None or season == '':
                season = None
            else:
                season = Season.objects.get(id=season)

            group_object = Group(name=name,sport=league.sport, league=league, season=season, starting_at=starting_at,
                                        ending_at=ending_at, is_current=is_current,
                                        status='Active')

            group_object.save()
            messages.success(request, _("Group Add Successfully"), extra_tags='Group')

            return HttpResponseRedirect(reverse_lazy('sport:AdminGroupList'))
        else:

                messages.error(request, _("Group Not Add , Please Try Again"), extra_tags='Group')

    else:
        context = {'groups': groups, 'groups_form': AdminGroupForm(), 'current_page': _('Groups')

                   }
        return render(request, f'{BACKEND_TEMPLATES}/sport/group/admin.html', context)



@authenticated_staf
@staff_only
def AdminGroupUpdate(request, slug):
    group = Group.objects.get(slug=slug)

    if request.method == "POST":
        groups_form = AdminGroupForm(request.POST or None, request.FILES or None, instance=group)

        if groups_form:
            name = request.POST.get('name')
            league = request.POST.get('league')
            season = request.POST.get('season')
            starting_at = request.POST.get('starting_at')
            ending_at = request.POST.get('ending_at')
            is_current = request.POST.get('is_current')
            status = request.POST.get('status')

            if league == None or league == '':
                league = None
            else:
                league = Leagues.objects.get(id=league)

            if season == None or season == '':
                season = None
            else:
                season = Season.objects.get(id=season)

            group_object = Group.objects.get(slug=slug)
            group_object.name = name
            group_object.league = league
            group_object.season = season

            group_object.starting_at = starting_at
            group_object.ending_at = ending_at
            group_object.is_current = is_current

            group_object.status = status
            group_object.save()

            messages.success(request, _("Group Update Successfully"), extra_tags='Group')

            return HttpResponseRedirect(reverse_lazy('sport:AdminGroupList'))
        else:

            messages.error(request, _("Group Not Update , Please Try Again"), extra_tags='Group')

    else:
        context = {'group': group, 'groups_form': AdminGroupForm(instance=group), 'current_page': _('Update'),
                   'prev_Page': _('Groups'), }
        return render(request, f'{BACKEND_TEMPLATES}/sport/group/update.html', context)
    context = {'group': group, 'groups_form': AdminGroupForm(instance=group), 'current_page': _('Update'),
               'prev_Page': _('Groups'), }
    return render(request, f'{BACKEND_TEMPLATES}/sport/group/update.html', context)


@authenticated_staf
@staff_only
def AdminGroupArchive(request, slug):
    group = Group.objects.get(slug=slug)
    if request.method == 'POST':
        group.status = 'Archive'
        group.save()
        messages.success(request, _("Group Archive Successfully"), extra_tags='Group')
        return HttpResponseRedirect(reverse_lazy('sport:AdminGroupList'))
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminGroupList'))


@authenticated_staf
@staff_only
def AdminGroupDelete(request, slug):
    group = Group.objects.get(slug=slug)

    if request.method == "POST":
        group.delete()

        messages.success(request, _("Group Delete Successfully"), extra_tags='Group')

        return HttpResponseRedirect(reverse_lazy('sport:AdminGroupList'))
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminGroupList'))

########################### Round ################################
@authenticated_staf
@staff_only
def AdminRoundList(request):
    rounds = Round.objects.all()

    if request.method == "POST":
        rounds_form = AdminRoundForm(request.POST or None, request.FILES or None)

        if rounds_form:
            name = request.POST.get('name')
            league = request.POST.get('league')
            group = request.POST.get('group')
            season = request.POST.get('season')
            starting_at = request.POST.get('starting_at')
            ending_at = request.POST.get('ending_at')


            if league == None or league == '':
                league = None
            else:
                league = Leagues.objects.get(id=league)

            if group == None or group == '':
                group = None
            else:
                group = Group.objects.get(id=group)

            if season == None or season == '':
                season = None
            else:
                season = Season.objects.get(id=season)

            try:
                round_object = Round.objects.get(name=name, sport=league.sport, league=league,group=group, season=season,
                                                    starting_at=starting_at, ending_at=ending_at)
                messages.error(request, _("Round Already Exist"), extra_tags='Round')
            except Round.DoesNotExist:
                round_object = Round(name=name, sport=league.sport, league=league,group=group, season=season, starting_at=starting_at,
                                        ending_at=ending_at,  status='Active')
                round_object.save()
                messages.success(request, _("Round Add Successfully"), extra_tags='Round')

            return HttpResponseRedirect(reverse_lazy('sport:AdminRoundList'))
        else:

                messages.error(request, _("Round Not Add , Please Try Again"), extra_tags='Round')

    else:
        context = {'rounds': rounds, 'rounds_form': AdminRoundForm(), 'current_page': _('Rounds')

                   }
        return render(request, f'{BACKEND_TEMPLATES}/sport/round/admin.html', context)


@authenticated_staf
@staff_only
def AdminRoundUpdate(request, slug):
    round = Round.objects.get(slug=slug)

    if request.method == "POST":
        rounds_form = AdminRoundForm(request.POST or None, request.FILES or None, instance=round)

        if rounds_form:
            name = request.POST.get('name')
            league = request.POST.get('league')
            season = request.POST.get('season')
            starting_at = request.POST.get('starting_at')
            ending_at = request.POST.get('ending_at')
            is_current = request.POST.get('is_current')
            status = request.POST.get('status')

            if league == None or league == '':
                league = None
            else:
                league = Leagues.objects.get(id=league)


            if season == None or season == '':
                season = None
            else:
                season = Season.objects.get(id=season)

            round_object = Round.objects.get(slug=slug)
            round_object.name = name
            round_object.sport = league.sport
            round_object.league = league
            round_object.season = season
            round_object.starting_at = starting_at
            round_object.ending_at = ending_at
            round_object.is_current = is_current
            round_object.status = status
            round_object.save()

            messages.success(request, _("Round Update Successfully"), extra_tags='Round')

            return HttpResponseRedirect(reverse_lazy('sport:AdminRoundList'))
        else:

            messages.error(request, _("Round Not Update , Please Try Again"), extra_tags='Round')

    else:
        context = {'round': round, 'rounds_form': AdminRoundForm(instance=round), 'current_page': _('Update'),
                   'prev_Page': _('Rounds'), }
        return render(request, f'{BACKEND_TEMPLATES}/sport/round/update.html', context)
    context = {'round': round, 'rounds_form': AdminRoundForm(instance=round), 'current_page': _('Update'),
               'prev_Page': _('Rounds'), }
    return render(request, f'{BACKEND_TEMPLATES}/sport/round/update.html', context)



@authenticated_staf
@staff_only
def AdminRoundArchive(request, slug):
    round = Round.objects.get(slug=slug)
    if request.method == 'POST':
        round.status = 'Archive'
        round.save()
        messages.success(request, _("Round Archive Successfully"), extra_tags='Round')
        return HttpResponseRedirect(reverse_lazy('sport:AdminRoundList'))
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminRoundList'))


@authenticated_staf
@staff_only
def AdminRoundDelete(request, slug):
    round = Round.objects.get(slug=slug)

    if request.method == "POST":
        round.delete()

        messages.success(request, _("Round Delete Successfully"), extra_tags='Round')

        return HttpResponseRedirect(reverse_lazy('sport:AdminRoundList'))
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminRoundList'))
##########  League Sport Season Table  #########

@authenticated_staf
@staff_only
def AdminSeasonLeagueTableList(request):
    table = LeagueSeasonTable.objects.all()

    if request.method == "POST":
        table_form = AdminSeasonLeagueTableForm(request.POST or None, request.FILES or None)

        if table_form:
            league = request.POST.get('league')
            group = request.POST.get('group')
            sort = request.POST.get('sort')

            league = Leagues.objects.get(id=league)
            group = Group.objects.get(id=group)
            season_table_object = LeagueSeasonTable(
                league=league,group=group, season=group.season, sport=league.sport,sort=sort, status='Active')
            season_table_object.save()
            messages.success(request, _("Season Table Add Successfully"), extra_tags='Season Table')

            return HttpResponseRedirect(reverse_lazy('sport:AdminSeasonLeagueTableList'))
        else:

            messages.error(request, _("Season Table Not Add , Please Try Again"), extra_tags='Season Table')

    else:
        context = {'table': table, 'table_form': AdminSeasonLeagueTableForm(), 'current_page': _('Season Table')
                   }
        return render(request, f'{BACKEND_TEMPLATES}/sport/league_table/admin.html', context)



@authenticated_staf
@staff_only
def AdminSeasonLeagueTableUpdate(request, slug):
    table = LeagueSeasonTable.objects.get(slug=slug)

    if request.method == "POST":
        season_table_form = AdminSeasonLeagueTableForm(request.POST or None, request.FILES or None, )
        if season_table_form:

            league = request.POST.get('league')
            group = request.POST.get('group')
            order = request.POST.get('order')
            sort = request.POST.get('sort')
            status = request.POST.get('status')

            group = Group.objects.get(id=group)
            league = Leagues.objects.get(id=league)
            season_table_object = LeagueSeasonTable.objects.get(slug=slug)
            season_table_object.league = league
            season_table_object.group = group
            season_table_object.order = order
            season_table_object.sort = sort
            season_table_object.status = status
            season_table_object.save()

            messages.success(request, _("Season Table Update Successfully"), extra_tags='Season Table')

            return HttpResponseRedirect(reverse_lazy('sport:AdminSeasonLeagueTableList'))
        else:

            messages.error(request, _("Season Table Not Update , Please Try Again"), extra_tags='Season Table')

    else:
        context = {'table': table, 'table_form': AdminSeasonLeagueTableForm(instance=table), 'current_page': _('Update'),
                   'prev_Page': _('Season Table'), }
        return render(request, f'{BACKEND_TEMPLATES}/sport/league_table/update.html', context)
    context = {'table': table, 'table_form': AdminSeasonLeagueTableForm(instance=table), 'current_page': _('Update'),
               'prev_Page': _('Season Table'), }
    return render(request, f'{BACKEND_TEMPLATES}/sport/league_table/update.html', context)



@authenticated_staf
@staff_only
def AdminSeasonLeagueTableArchive(request, slug):
    season_table = LeagueSeasonTable.objects.get(slug=slug)
    if request.method == 'POST':
        season_table.status = 'Archive'
        season_table.save()
        messages.success(request, _("Season Table Archive Successfully"), extra_tags='Season Table')
        return HttpResponseRedirect(reverse_lazy('sport:AdminSeasonLeagueTableList'))
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminSeasonLeagueTableList'))


@authenticated_staf
@staff_only
def AdminSeasonLeagueTableDelete(request, slug):
    season_table = LeagueSeasonTable.objects.get(slug=slug)

    if request.method == "POST":
        season_table.delete()

        messages.success(request, _("Season Table Delete Successfully"), extra_tags='Season Table')

        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect(request.META.get('HTTP_REFERER'))




##################### Season Table ##############################

@authenticated_staf
@staff_only
def AdminSeasonTeamTableList(request,slug):
    table = LeagueSeasonTable.objects.get(slug=slug)
    team_table = TeamSeasonTable.objects.filter(table=table,).order_by('position')

    if request.method == "POST":
        season_table_form = AdminSeasonTeamTableForm(request.POST or None, request.FILES or None)
        if season_table_form:


            team = request.POST.get('team')
            played = request.POST.get('played')
            win = request.POST.get('win')
            draw = request.POST.get('draw')
            lose = request.POST.get('lose')
            goal_for = request.POST.get('goal_for')
            goal_against = request.POST.get('goal_against')
            goal_difference = request.POST.get('goal_difference')
            points = request.POST.get('points')
            status = request.POST.get('status')


            team = Teams.objects.get(id=team)

            season_table_object = TeamSeasonTable(table=table,
                season=table.season,league=table.league,team=team,played=played,win=win,draw=draw,lose=lose,
                goal_for=goal_for,goal_against=goal_against,goal_difference=goal_difference,points=points,
                status=status
            )
            season_table_object.save()
            messages.success(request, _("Season Table Add Successfully"), extra_tags='Season Table')
            return HttpResponseRedirect(reverse_lazy('sport:AdminSeasonTableList'))
        else:
            messages.error(request, _("Season Table Not Add , Please Try Again"), extra_tags='Season Table')
    else:
        context = {'table':table,'team_table': team_table, 'table_form': AdminSeasonTeamTableForm(), 'current_page': _('Season Table')}
        return render(request, f'{BACKEND_TEMPLATES}/sport/team_table/admin.html', context)


@authenticated_staf
@staff_only
def AdminSeasonTeamTableCreate(request,slug):
    table = LeagueSeasonTable.objects.get(slug=slug)

    teams = Teams.objects.filter(sport=table.sport)
    team_table = TeamSeasonTable.objects.all()

    if request.method == "POST":
        season_table_form = AdminSeasonTeamTableForm(request.POST or None, request.FILES or None)
        if season_table_form:
            team = request.POST.get('team')
            points= request.POST.get('points')
            position = request.POST.get('position')
            order = request.POST.get('order')
            played = request.POST.get('played')
            win = request.POST.get('win')
            draw = request.POST.get('draw')
            lose = request.POST.get('lose')
            remaining = request.POST.get('remaining')
            goals_for = request.POST.get('goals_for')
            goals_against = request.POST.get('goals_against')
            goals_difference = request.POST.get('goals_difference')
            goals_for_run = request.POST.get('goals_for_run')
            goals_against_run = request.POST.get('goals_against_run')
            goals_difference_run = request.POST.get('goals_difference_run')

            team = Teams.objects.get(id=team)
            try:
                team_table_object = TeamSeasonTable.objects.get(table=table,team=team)
                team_table_object.points = points
                team_table_object.position = position
                team_table_object.order = order
                team_table_object.played = played
                team_table_object.win = win
                team_table_object.draw = draw
                team_table_object.lose = lose
                team_table_object.remaining = remaining
                team_table_object.goals_for = goals_for
                team_table_object.goals_against = goals_against
                team_table_object.goals_difference = goals_difference
                team_table_object.goals_for_run = goals_for_run
                team_table_object.goals_against_run = goals_against_run
                team_table_object.goals_difference_run = goals_difference_run
                team_table_object.save()
            except:
                team_table_object = TeamSeasonTable(
                    table=table,
                    league=table.league,team=team,points=points,position=position,order=order,played=played,win=win,draw=draw,
                    lose=lose,
                    remaining=remaining,goals_for=goals_for,goals_against=goals_against,goals_difference=goals_difference,
                    goals_for_run=goals_for_run,goals_against_run=goals_against_run,goals_difference_run=goals_difference_run,
                )
                team_table_object.save()
            messages.success(request, _("Season Table Add Successfully"), extra_tags='Season Table')
            return HttpResponseRedirect(
                reverse_lazy('sport:AdminSeasonTeamTableCreate', kwargs={'slug': slug, }))
        else:
            messages.error(request, _("Season Table Not Add , Please Try Again"), extra_tags='Season Table')
    else:
        context = {'table':table,'teams':teams,
                   'team_table': team_table, 'season_table_form': AdminSeasonTeamTableForm(),
                   'current_page': _('Season Table')}
        return render(request, f'{BACKEND_TEMPLATES}/sport/team_table/add.html',context)




@authenticated_staf
@staff_only
def AdminSeasonTableDetails(request, slug):
    season_table = TeamSeasonTable.objects.get(slug=slug)
    context = {'season_table': season_table, 'current_page': _('Season Table')}
    return render(request, f'{BACKEND_TEMPLATES}/sport/season_table/details.html', context)

@authenticated_staf
@staff_only
def AdminSeasonTeamTableUpdate(request, slug):
    tam_table = TeamSeasonTable.objects.get(slug=slug)
    team = Teams.objects.get(id=tam_table.team.id)


    if request.method == "POST":
        table_form = AdminSeasonTeamTableForm(request.POST or None, request.FILES or None, instance=tam_table)
        if table_form:

            points = request.POST.get('points')
            order = request.POST.get('order')
            position = request.POST.get('position')
            played = request.POST.get('played')
            win = request.POST.get('win')
            draw = request.POST.get('draw')
            lose = request.POST.get('lose')
            remaining = request.POST.get('remaining')
            goals_for = request.POST.get('goals_for')
            goals_against = request.POST.get('goals_against')
            goals_difference = request.POST.get('goals_difference')
            goals_for_run = request.POST.get('goals_for_run')
            goals_against_run = request.POST.get('goals_against_run')
            goals_difference_run = request.POST.get('goals_difference_run')


            tam_table_object = TeamSeasonTable.objects.get(slug=slug)
            tam_table_object.points = points
            tam_table_object.order = order
            tam_table_object.position = position
            tam_table_object.played = played
            tam_table_object.win = win
            tam_table_object.draw = draw
            tam_table_object.lose = request.POST.get('lose')
            tam_table_object.remaining = remaining
            tam_table_object.goals_for = goals_for
            tam_table_object.goals_against = goals_against
            tam_table_object.goals_difference = goals_difference
            tam_table_object.goals_for_run = goals_for_run
            tam_table_object.goals_against_run = goals_against_run
            tam_table_object.goals_difference_run = goals_difference_run
            tam_table_object.save()

            messages.success(request, _("Season Table Update Successfully"), extra_tags='Season Table')
            return HttpResponseRedirect(reverse_lazy('sport:AdminSeasonTeamTableList', kwargs={'slug': tam_table.table.slug, }))
        else:
            messages.error(request, _("Season Table Not Update , Please Try Again"), extra_tags='Season Table')

    context = {'tam_table': tam_table, 'table_form': AdminSeasonTeamTableForm(instance=tam_table), 'current_page': _('Update'),
                'prev_Page': _('Season Table'), }
    return render(request, f'{BACKEND_TEMPLATES}/sport/team_table/update.html', context)


@authenticated_staf
@staff_only
def AdminSeasonTableDelete(request, slug):
    season_table = TeamSeasonTable.objects.get(slug=slug)


    if request.method == "POST":
        season_table.delete()

        messages.success(request, _("Season Table Delete Successfully"), extra_tags='Season Table')

        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect(request.META.get('HTTP_REFERER'))



##########################  Clubs ################################

@authenticated_staf
@staff_only
def AdminClubsList(request):
    clubs = Clubs.objects.all()

    if request.method == "POST":
        clubs_form = AdminClubsForm(request.POST or None, request.FILES or None)
        if clubs_form:
            name = request.POST.get('name')
            keyword = request.POST.get('keyword')
            country = request.POST.get('country')
            founded = request.POST.get('founded')
            country_image = request.FILES.get('country_image')
            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')



            clubs_object = Clubs(name=name, keyword=keyword, country=country,founded=founded,country_image=country_image, image=image,
                                    image_path=image_path, status='Active')

            clubs_object.save()
            messages.success(request, _("Clubs Add Successfully"), extra_tags='Clubs')
            return HttpResponseRedirect(reverse_lazy('sport:AdminClubsList'))
        else:
            messages.error(request, _("Clubs Not Add , Please Try Again"), extra_tags='Clubs')
    else:
        context = {'clubs': clubs, 'clubs_form': AdminClubsForm(), 'current_page': _('Clubs')}
        return render(request, f'{BACKEND_TEMPLATES}/sport/clubs/admin.html', context)


@authenticated_staf
@staff_only
def AdminClubsUpdate(request, slug):
    club = Clubs.objects.get(slug=slug)

    if request.method == "POST":
        name = request.POST.get('name')
        keyword = request.POST.get('keyword')
        country = request.POST.get('country')
        founded = request.POST.get('founded')
        country_image = request.FILES.get('country_image')
        image = request.FILES.get('image')
        image_path = request.POST.get('image_path')
        status = request.POST.get('status')



        clubs_object = Clubs.objects.get(slug=slug)
        clubs_object.name = name
        clubs_object.keyword = keyword

        clubs_object.country = country
        clubs_object.founded = founded
        if country_image:
            clubs_object.country_image = country_image
        if image:
            clubs_object.image = image
        clubs_object.image_path = image_path
        clubs_object.status = status
        clubs_object.save()

        messages.success(request, _("Clubs Update Successfully"), extra_tags='Clubs')

        return HttpResponseRedirect(reverse_lazy('sport:AdminClubsList'))
    else:
        messages.error(request, _("Clubs Not Update , Please Try Again"), extra_tags='Clubs')
    context = {'club': club, 'clubs_form': AdminClubsForm(instance=club), 'current_page': _('Update'),
                'prev_Page': _('Clubs'), }
    return render(request, f'{BACKEND_TEMPLATES}/sport/clubs/update.html', context)


@authenticated_staf
@staff_only
def AdminClubsArchive(request, slug):
    club = Clubs.objects.get(slug=slug)
    if request.method == 'POST':
        club.status = 'Archive'
        club.save()
        messages.success(request, _("Clubs Archive Successfully"), extra_tags='Clubs')
        return HttpResponseRedirect(reverse_lazy('sport:AdminClubsList'))
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminClubsList'))


@authenticated_staf
@staff_only
def AdminClubsDelete(request, slug):
    club = Clubs.objects.get(slug=slug)

    if request.method == "POST":
        club.delete()

        messages.success(request, _("Clubs Delete Successfully"), extra_tags='Clubs')

        return HttpResponseRedirect(reverse_lazy('sport:AdminClubsList'))
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminClubsList'))


##########################  Venues ################################

@authenticated_staf
@staff_only
def AdminVenuesList(request):
    venues = Venues.objects.all()

    if request.method == "POST":
        venues_form = AdminVenuesForm(request.POST or None, request.FILES or None)

        if venues_form:
            name = request.POST.get('name')
            keyword = request.POST.get('keyword')
            country = request.POST.get('country')
            city = request.POST.get('city')
            short_code = request.POST.get('short_code')
            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')

            venues_object = Venues(name=name, keyword=keyword, country=country, city=city, short_code=short_code,
                                   image=image, image_path=image_path, status='Active')

            venues_object.save()
            messages.success(request, _("Venues Add Successfully"), extra_tags='Venues')

            return HttpResponseRedirect(reverse_lazy('sport:AdminVenuesList'))
        else:

            messages.error(request, _("Venues Not Add , Please Try Again"), extra_tags='Venues')

    else:
        context = {'venues': venues, 'venues_form': AdminVenuesForm(), 'current_page': _('Venues')

                   }
        return render(request, f'{BACKEND_TEMPLATES}/sport/venues/admin.html', context)


@authenticated_staf
@staff_only
def AdminVenuesUpdate(request, slug):
    venue = Venues.objects.get(slug=slug)

    if request.method == "POST":
        name = request.POST.get('name')
        keyword = request.POST.get('keyword')
        country = request.POST.get('country')
        city = request.POST.get('city')
        short_code = request.POST.get('short_code')
        image = request.FILES.get('image')
        image_path = request.POST.get('image_path')
        status = request.POST.get('status')

        venues_object = Venues.objects.get(slug=slug)
        venues_object.name = name
        venues_object.keyword = keyword
        venues_object.country = country
        venues_object.city = city
        venues_object.short_code = short_code
        venues_object.image = image
        venues_object.image_path = image_path
        venues_object.status = status
        venues_object.save()

        messages.success(request, _("Venues Update Successfully"), extra_tags='Venues')

        return HttpResponseRedirect(reverse_lazy('sport:AdminVenuesList'))
    else:

            messages.error(request, _("Venues Not Update , Please Try Again"), extra_tags='Venues')

    context = {'venue': venue, 'venues_form': AdminVenuesForm(instance=venue), 'current_page': _('Update'),
                'prev_Page': _('Venues'), }
    return render(request, f'{BACKEND_TEMPLATES}/sport/venues/update.html', context)


@authenticated_staf
@staff_only
def AdminVenuesArchive(request, slug):
    venue = Venues.objects.get(slug=slug)
    if request.method == 'POST':
        venue.status = 'Archive'
        venue.save()
        messages.success(request, _("Venues Archive Successfully"), extra_tags='Venues')
        return HttpResponseRedirect(reverse_lazy('sport:AdminVenuesList'))
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminVenuesList'))


@authenticated_staf
@staff_only
def AdminVenuesDelete(request, slug):
    venue = Venues.objects.get(slug=slug)

    if request.method == "POST":
        venue.delete()

        messages.success(request, _("Venues Delete Successfully"), extra_tags='Venues')

        return HttpResponseRedirect(reverse_lazy('sport:AdminVenuesList'))
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminVenuesList'))






##########################  Teams ################################
@authenticated_staf
@staff_only
def AdminTeamsList(request):
    # The POST logic for adding a new team remains the same.
    if request.method == "POST":
        teams_form = AdminTeamsForm(request.POST or None, request.FILES or None)

        if teams_form.is_valid():  # It's good practice to check if the form is valid
            name = request.POST.get('name')
            sport_id = request.POST.get('sport')

            # Prevent creating a team with the same name in the same sport
            if Teams.objects.filter(name=name, sport_id=sport_id).exists():
                messages.error(request, _("A team with this name already exists for the selected sport."),
                               extra_tags='Teams')
                return HttpResponseRedirect(reverse_lazy('sport:AdminTeamsList'))

            # Your existing POST logic...
            short_code = request.POST.get('short_code')
            club_id = request.POST.get('club')
            gender = request.POST.get('gender')
            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')

            club = Clubs.objects.get(id=club_id) if club_id else None
            sport = Sport.objects.get(id=sport_id) if sport_id else None

            teams_object = Teams(
                name=name, club=club, sport=sport,
                gender=gender, short_code=short_code, image=image,
                image_path=image_path, status='Active'
            )
            teams_object.save()
            messages.success(request, _("Team added successfully."), extra_tags='Teams')
            return HttpResponseRedirect(reverse_lazy('sport:AdminTeamsList'))
        else:
            messages.error(request, _("The form was not valid. Please try again."), extra_tags='Teams')
            # Fall through to the GET request logic to re-display the page with form errors

    # --- PAGINATION LOGIC FOR GET REQUEST ---
    teams_list = Teams.objects.all().order_by('name')

    # Create a Paginator instance, showing 25 teams per page.
    paginator = Paginator(teams_list, 25)

    # Get the current page number from the URL's 'page' parameter.
    page_number = request.GET.get('page')

    # Get the Page object for the requested page number.
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # If the page is not an integer, deliver the first page.
        page_obj = paginator.page(1)
    except EmptyPage:
        # If the page is out of range, deliver the last page of results.
        page_obj = paginator.page(paginator.num_pages)

    context = {
        'page_obj': page_obj,  # Pass the paginated object to the template
        'teams_form': AdminTeamsForm(),
        'current_page': _('Teams')
    }
    return render(request, f'{BACKEND_TEMPLATES}/sport/teams/admin.html', context)


@authenticated_staf
@staff_only
def AdminTeamsCreate(request,slug):
    sport = Sport.objects.get(slug=slug)
    if request.method == "POST":
        teams_form = AdminTeamsForm(request.POST or None, request.FILES or None)

        if teams_form:
            name = request.POST.get('name')
            short_code = request.POST.get('short_code')
            country = request.POST.get('country')
            club = request.POST.get('club')
            venue = request.POST.get('venue')
            gender = request.POST.get('gender')
            keyword = request.POST.get('keyword')
            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')
            status = 'Active'

            if club :
                club = Clubs.objects.get(id=club)
            else:
                club = None

            try:
                check_teams = Teams.objects.get(name=name,sport=sport)
                messages.error(request, _("Teams Already Exist , Please Try Again"), extra_tags='Teams')
                return HttpResponseRedirect(reverse_lazy('sport:AdminTeamsList'))
            except:
                teams_object = Teams(  name=name,country=country,club=club,sport=sport,venue=venue,
                                       short_code=short_code,gender=gender,keyword=keyword,image=image,image_path=image_path,status=status)
                teams_object.save()

            messages.success(request, _("Teams Add Successfully"), extra_tags='Teams')
            return redirect(request.META['HTTP_REFERER'])

    else:
        messages.error(request, _("Teams Not Add , Please Try Again"), extra_tags='Teams')

    context = { 'teams_form': AdminTeamsForm(), 'current_page': _('Teams')
                  }
    return render(request, f'{BACKEND_TEMPLATES}/sport/teams/admin.html', context)

@authenticated_staf
@staff_only
def AdminTeamSearch(request):
    if request.method == "POST":
        search = request.POST.get('search')
        teams = Teams.objects.filter(
            Q(name__icontains=search) | Q(country__icontains=search)
        )

        context = {'page_obj': teams, 'current_page': _('Teams')}
        return render(request, f'{BACKEND_TEMPLATES}/sport/teams/monks.html', context)
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminTeamsList'))

@authenticated_staf
@staff_only
def AdminTeamsUpdate(request, slug):
    team = Teams.objects.get(slug=slug)

    if request.method == "POST":
        teams_form = AdminTeamsForm(request.POST or None, request.FILES or None, instance=team)
        if teams_form:
            name = request.POST.get('name')
            name_tr = request.POST.get('name_tr')
            short_code = request.POST.get('short_code')
            country = request.POST.get('country')
            club = request.POST.get('club')
            sport = request.POST.get('sport')
            venue = request.POST.get('venue')
            gender = request.POST.get('gender')
            keyword = request.POST.get('keyword')
            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')
            country_image = request.FILES.get('country_image')
            status = 'Active'

            try:
                check_teams = Teams.objects.get(name=name,sport=sport).exclude(slug=slug)
                messages.error(request, _("Teams Already Exist , Please Try Again"), extra_tags='Teams')
                # return HttpResponseRedirect(reverse_lazy('sport:AdminTeamsList'))
            except:
                pass


            if venue == None or venue == '':
                venue = None
            else:
                venue = Venues.objects.get(id=venue)

            if club == None or club == '':
                club = None
            else:
                club = Clubs.objects.get(id=club)

            if sport == None or sport == '':
                sport = None
            else:
                sport = Sport.objects.get(id=sport)

            team_object = Teams.objects.get(slug=slug)
            team_object.name = name
            team_object.name_tr = name_tr
            team_object.short_code = short_code
            team_object.country = country
            team_object.club = club
            team_object.sport = sport
            team_object.venue = venue
            team_object.gender = gender
            team_object.keyword = keyword
            try:
                team_object.founded = team_object.club.founded
                team_object.country = team_object.club.country
                team_object.country_image = team_object.club.country_image
                if image == None or image == '':
                    team_object.image = team_object.club.image
                else:
                    team_object.image = image
            except:
                pass
            team_object.image_path = image_path
            team_object.status = status
            team_object.save()

            messages.success(request, _("Teams Update Successfully"), extra_tags='Teams')
            # return HttpResponseRedirect(reverse_lazy('sport:AdminTeamsList'))
            return redirect(request.META.get('HTTP_REFERER'))
        else:
                messages.error(request, _("Teams Not Update , Please Try Again"), extra_tags='Teams')
    context = {'team': team, 'teams_form': AdminTeamsForm(instance=team), 'current_page': _('Update'),
               'prev_Page': _('Teams'), }
    return render(request, f'{BACKEND_TEMPLATES}/sport/teams/update.html', context)


@authenticated_staf
@staff_only
def AdminTeamsArchive(request, slug):
    team = Teams.objects.get(slug=slug)
    if request.method == 'POST':
        team.status = 'Archive'
        team.save()
        messages.success(request, _("Teams Archive Successfully"), extra_tags='Teams')
        return HttpResponseRedirect(reverse_lazy('sport:AdminTeamsList'))
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminTeamsList'))


@authenticated_staf
@staff_only
def AdminTeamsDelete(request, slug):
    team = Teams.objects.get(slug=slug)

    if request.method == "POST":
        team.delete()

        messages.success(request, _("Teams Delete Successfully"), extra_tags='Teams')

        return HttpResponseRedirect(reverse_lazy('sport:AdminTeamsList'))
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminTeamsList'))


@authenticated_staf
@staff_only
def AdminTeamPlayerList(request, slug):
    team = Teams.objects.get(slug=slug)
    players = Players.objects.filter(team=team)
    if request.method == "POST":
        players_form = AdminPlayersForm(request.POST or None, request.FILES or None)
        if players_form:
            name = request.POST.get('name')
            position = request.POST.get('position')
            age = request.POST.get('age')
            height = request.POST.get('height')
            country = request.POST.get('country')
            country_image = request.FILES.get('country_image')
            # team = request.POST.get('team')
            # sport = request.POST.get('sport')
            # gender = request.POST.get('gender')
            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')
            keyword = request.POST.get('keyword')





            team = Teams.objects.get(id=team.id)
            sport = Sport.objects.get(id=team.sport.id)
            gender = team.gender
            in_team = 'Yes'

            player_object = Players(
                name=name, position=position, age=age, height=height, country=country,country_image=country_image,
                team=team, sport=sport,in_team=in_team,
                gender=gender, keyword=keyword, image=image, image_path=image_path,)
            player_object.save()
            team.player_count += 1
            team.save()
            # match_team_player_object = MatchTeamPlayer( team=team, player=player_object)
            # match_team_player_object.save()
            messages.success(request, _("Players Add Successfully"), extra_tags='Players')
            return HttpResponseRedirect(reverse_lazy('sport:AdminTeamPlayerList', kwargs={'slug': slug}))
        else:
            messages.error(request, _("Players Not Add , Please Try Again"), extra_tags='Players')

    context = {'team': team, 'players': players,
               'players_form': AdminPlayersForm(), 'transfer_form': AdminTransfersForm(),
               'current_page': _('Add Player'),
               'prev_Page': _('Teams'), }
    return render(request, f'{BACKEND_TEMPLATES}/sport/teams/players.html', context)
@authenticated_staf
@staff_only
def AdminTeamPlayerAdd(request, slug):
    team = Teams.objects.get(slug=slug)
    players = Players.objects.filter(in_team='No')


    if request.method == "POST":
        players_form = AdminPlayersForm(request.POST or None, request.FILES or None)
        transfer_form = AdminTransfersForm(request.POST or None, request.FILES or None)
        if players_form:
            team_player = request.POST.getlist('[team_player]')
            start_date = request.POST.getlist('[start_date]')
            team_position = request.POST.getlist('[team_position]')
            from_team = request.POST.getlist('[from_team]')
            to_team = request.POST.getlist('[to_team]')

           
            for player, date, position, f_team, t_team in zip(team_player, start_date, team_position, from_team, to_team):

                player_object = Players.objects.get(id=player)
                player_object.owner_model = ContentType.objects.get(model = 'Teams')
                player_object.owner_id = team.id
                player_object.in_team = 'Yes'
                player_object.save()
                if f_team == None or f_team == '':
                    f_team = None
                else:
                    f_team = Teams.objects.get(id=f_team)
                if t_team == None or t_team == '':
                    t_team = None
                else:
                    t_team = Teams.objects.get(id=t_team)
                transfer_object = Transfers(player=player_object, date=date, position=position,
                                            from_team=f_team, to_team=t_team)
                transfer_object.save()
                team_object = Teams.objects.get(slug=slug)
                team_object.player_count += 1
                team_object.save()


            messages.success(request, _("Player Add Successfully"), extra_tags='Teams')
            return HttpResponseRedirect(reverse_lazy('sport:AdminTeamsList'))


    else:
        messages.error(request, _("Player Not Add , Please Try Again"), extra_tags='Teams')
    context = {'team': team, 'players': players,
                 'players_form': AdminPlayersForm(), 'transfer_form': AdminTransfersForm(),
               'current_page': _('Add Player'),
               'prev_Page': _('Teams'), }
    return render(request, f'{BACKEND_TEMPLATES}/sport/teams/player.html', context)
@authenticated_staf
@staff_only
def AdminMatchTeamPlayerList(request,match_slug, slug):
    match = Match.objects.get(slug=match_slug)
    team = Teams.objects.get(slug=slug)
    players = Players.objects.filter(in_team='No')
    team_players = Players.objects.filter(team=team)
    match_players = MatchTeamPlayer.objects.filter(team=team)


    if request.method == "POST":
        match_team_player_form = AdminMatchTeamPlayerForm(request.POST or None, request.FILES or None)
        if match_team_player_form:
            team_player = request.POST.getlist('[team_player]')


            for player in zip(team_player):
                player_object = Players.objects.get(id=player)
                match_team_player_object = MatchTeamPlayer(match=match,team=team,player=player_object)
                match_team_player_object.save()
            messages.success(request, _("Player Add Successfully"), extra_tags='Match Team Player')
            return HttpResponseRedirect(reverse_lazy('sport:AdminMatchTeamPlayerList', kwargs={'match_slug': match_slug, 'slug': slug}))
        else:
            messages.error(request, _("Player Not Add , Please Try Again"), extra_tags='Match Team Player')

    context = {
                'match': match,
                'team': team,
                'team_players': team_players,
                'match_players': match_players,
                'players': players,
                'match_team_player_form': AdminMatchTeamPlayerForm(),
                'summary_form': AdminMatchSummaryForm(),
                'static_form': AdminMatchStaticsForm(),
                'current_page': _('Match Team Players')}
    return render(request, f'{BACKEND_TEMPLATES}/sport/match/player.html', context)


@authenticated_staf
@staff_only
def AdminTeamPlayerMatchAdd(request, slug):
    team = Teams.objects.get(slug=slug)
    players = Players.objects.filter(in_team='No')

    if request.method == "POST":
        players_form = AdminPlayersForm(request.POST or None, request.FILES or None)
        transfer_form = AdminTransfersForm(request.POST or None, request.FILES or None)
        if players_form:
            team_player = request.POST.getlist('[team_player]')


            for player in zip(team_player):

                player_object = Players.objects.get(id=player)
                player_object.owner_model = ContentType.objects.get(model = 'Teams')
                player_object.owner_id = team.id
                player_object.in_team = 'Yes'
                player_object.save()

                transfer_object = Transfers(player=player_object)
                transfer_object.save()
                team_object = Teams.objects.get(slug=slug)
                team_object.player_count += 1
                team_object.save()


            messages.success(request, _("Player Add Successfully"), extra_tags='Match Team Player')
            return redirect(request.META['HTTP_REFERER'])


    else:
        messages.error(request, _("Player Not Add , Please Try Again"), extra_tags='Match Team Player')
    context = {'team': team, 'players': players,
                 'players_form': AdminPlayersForm(), 'transfer_form': AdminTransfersForm(),
               'current_page': _('Add Player'),
               'prev_Page': _('Teams'), }
    return render(request, f'{BACKEND_TEMPLATES}/sport/teams/player.html', context)

@authenticated_staf
@staff_only
def AdminMatchPlayerStaticAdd(request, match_slug, slug):
    match = Match.objects.get(slug=match_slug)
    player = Players.objects.get(slug=slug)
    
    try:
        player_statics = MatchPlayerReport.objects.get(player=player, match=match)
    except:
        player_statics = None
    
    try:
        total_statics = PlayerStatics.objects.get(player=player)
    except:
        total_statics = None
    
    if request.method == "POST":
        static_form = AdminPlayerStaticsForm(request.POST or None, request.FILES or None)
        if static_form:
            set_ball = request.POST.get('set_ball', 0) or 0
            serve_ball = request.POST.get('serve_ball', 0) or 0
            cut_ball = request.POST.get('cut_ball', 0) or 0
            shot_ball = request.POST.get('shot_ball', 0) or 0
            score_ball = request.POST.get('score_ball', 0) or 0
            is_best_player = request.POST.get('is_best_player') == 'on'
            point_total = request.POST.get('point_total', '')
            serve_total = request.POST.get('serve_total', '')
            serve_err = request.POST.get('serve_err', '')
            serve_ace = request.POST.get('serve_ace', '')
            reception_total = request.POST.get('reception_total', '')
            reception_err = request.POST.get('reception_err', '')
            reception_exc = request.POST.get('reception_exc', '')
            attack_total = request.POST.get('attack_total', '')
            attack_err = request.POST.get('attack_err', '')
            attack_pts = request.POST.get('attack_pts', '')
            attack_att = request.POST.get('attack_att', '')
            block_pts = request.POST.get('block_pts', '')
            min_played = request.POST.get('min_played', '')
            pts = request.POST.get('pts', '')
            reb = request.POST.get('reb', '')
            ast = request.POST.get('ast', '')
            stl = request.POST.get('stl', '')
            blk = request.POST.get('blk', '')
            fg = request.POST.get('fg', '')
            three_pt = request.POST.get('three_pt', '')
            ft = request.POST.get('ft', '')
            Offensive_Rebounds = request.POST.get('Offensive_Rebounds', '')
            dr = request.POST.get('dr', '')
            to = request.POST.get('to', '')
            pf = request.POST.get('pf', '')
            pir = request.POST.get('pir', '')

            try:
                player_ms_object, created = MatchPlayerReport.objects.get_or_create(
                    player=player,
                    match=match,
                    defaults={
                        'set_ball': set_ball,'serve_ball': serve_ball,'cut_ball': cut_ball,'shot_ball': shot_ball,'score_ball': score_ball,'is_best_player': is_best_player,
                        'point_total': point_total,'serve_total': serve_total,'serve_err': serve_err,'serve_ace': serve_ace,'reception_total': reception_total,
                        'reception_err': reception_err,'reception_exc': reception_exc,'attack_total': attack_total,'attack_err': attack_err,'attack_pts': attack_pts,
                        'attack_att': attack_att,'block_pts': block_pts,'min_played': min_played,'pts': pts,'reb': reb,'ast': ast,'stl': stl,'blk': blk,
                        'fg': fg,'three_pt': three_pt,'ft': ft,'Offensive_Rebounds': Offensive_Rebounds,'dr': dr,'to': to,'pf': pf,'pir': pir,
                        'static_type': 'General'
                    }
                )
                
                if not created:
                    player_ms_object.set_ball = set_ball
                    player_ms_object.serve_ball = serve_ball
                    player_ms_object.cut_ball = cut_ball
                    player_ms_object.shot_ball = shot_ball
                    player_ms_object.score_ball = score_ball
                    player_ms_object.is_best_player = is_best_player
                    player_ms_object.point_total = point_total
                    player_ms_object.serve_total = serve_total
                    player_ms_object.serve_err = serve_err
                    player_ms_object.serve_ace = serve_ace
                    player_ms_object.reception_total = reception_total
                    player_ms_object.reception_err = reception_err
                    player_ms_object.reception_exc = reception_exc
                    player_ms_object.attack_total = attack_total
                    player_ms_object.attack_err = attack_err
                    player_ms_object.attack_pts = attack_pts
                    player_ms_object.attack_att = attack_att
                    player_ms_object.block_pts = block_pts
                    player_ms_object.min_played = min_played
                    player_ms_object.pts = pts
                    player_ms_object.reb = reb
                    player_ms_object.ast = ast
                    player_ms_object.stl = stl
                    player_ms_object.blk = blk
                    player_ms_object.fg = fg
                    player_ms_object.three_pt = three_pt
                    player_ms_object.ft = ft
                    player_ms_object.Offensive_Rebounds = Offensive_Rebounds
                    player_ms_object.dr = dr
                    player_ms_object.to = to
                    player_ms_object.pf = pf
                    player_ms_object.pir = pir
                    player_ms_object.static_type = 'General'
                    player_ms_object.save()

                if is_best_player:
                    MatchPlayerReport.objects.filter(match=match).exclude(player=player).update(is_best_player=False)
                    
            except Exception as e:
                messages.error(request, f"Error saving match report: {str(e)}", extra_tags='Players')
                return HttpResponseRedirect(reverse_lazy('sport:AdminMatchTeamPlayerList', kwargs={'match_slug': match_slug, 'slug': player.team.slug}))

            try:
                player_ts_object, created = PlayerStatics.objects.get_or_create(
                    player=player,
                    defaults={
                        'set_ball': set_ball,'serve_ball': serve_ball,'cut_ball': cut_ball,'shot_ball': shot_ball,'score_ball': score_ball,'point_total': point_total,
                        'serve_total': serve_total,'serve_err': serve_err,'serve_ace': serve_ace,'reception_total': reception_total,'reception_err': reception_err,'reception_exc': reception_exc,
                        'attack_total': attack_total,'attack_err': attack_err,'attack_pts': attack_pts,'attack_att': attack_att,'block_pts': block_pts,'min_played': min_played,
                        'pts': pts,'reb': reb,'ast': ast,'stl': stl,'blk': blk,'fg': fg,'three_pt': three_pt,'ft': ft,'Offensive_Rebounds': Offensive_Rebounds,
                        'dr': dr,'to': to,'pf': pf,'pir': pir,
                        'static_type': 'General'
                    }
                )
                
                if not created:
                    player_ts_object.set_ball = set_ball
                    player_ts_object.serve_ball = serve_ball
                    player_ts_object.cut_ball = cut_ball
                    player_ts_object.shot_ball = shot_ball
                    player_ts_object.score_ball = score_ball
                    player_ts_object.point_total = point_total
                    player_ts_object.serve_total = serve_total
                    player_ts_object.serve_err = serve_err
                    player_ts_object.serve_ace = serve_ace
                    player_ts_object.reception_total = reception_total
                    player_ts_object.reception_err = reception_err
                    player_ts_object.reception_exc = reception_exc
                    player_ts_object.attack_total = attack_total
                    player_ts_object.attack_err = attack_err
                    player_ts_object.attack_pts = attack_pts
                    player_ts_object.attack_att = attack_att
                    player_ts_object.block_pts = block_pts
                    player_ts_object.min_played = min_played
                    player_ts_object.pts = pts
                    player_ts_object.reb = reb
                    player_ts_object.ast = ast
                    player_ts_object.stl = stl
                    player_ts_object.blk = blk
                    player_ts_object.fg = fg
                    player_ts_object.three_pt = three_pt
                    player_ts_object.ft = ft
                    player_ts_object.Offensive_Rebounds = Offensive_Rebounds
                    player_ts_object.dr = dr
                    player_ts_object.to = to
                    player_ts_object.pf = pf
                    player_ts_object.pir = pir
                    
                    player_ts_object.save()
                    
            except Exception as e:
                messages.error(request, f"Error saving total statics: {str(e)}", extra_tags='Players')
                return HttpResponseRedirect(reverse_lazy('sport:AdminMatchTeamPlayerList', kwargs={'match_slug': match_slug, 'slug': player.team.slug}))

            messages.success(request, _("Player Statics Add Successfully"), extra_tags='Players')
            return HttpResponseRedirect(reverse_lazy('sport:AdminMatchTeamPlayerList', kwargs={'match_slug': match_slug, 'slug': player.team.slug}))
        else:
            messages.error(request, _("Player Statics Not Add , Please Try Again"), extra_tags='Players')

    context = {
        'match': match, 
        'player': player,
        'player_statics': player_statics,
        'total_statics': total_statics,
        'static_form': AdminPlayerStaticsForm(), 
        'current_page': _('Add Statics'),
        'prev_Page': _('Players'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/sport/match/statics.html', context)


@authenticated_staf
@staff_only
def AdminMatchPlayerStaticPdfUpload(request, match_slug):
    """
    Enhanced view to upload PDF, extract to JSON, preview data, and update player statistics.
    Features:
    - Shows JSON preview before saving
    - Real-time extraction progress
    - Detailed error reporting
    - Validation of data before database save
    """
    try:
        match = get_object_or_404(Match, slug=match_slug)
    except Match.DoesNotExist:
        messages.error(request, _("Match not found"), extra_tags='Players')
        return HttpResponseRedirect(reverse_lazy('sport:AdminMatchList'))

    extraction_data = None
    json_preview = None

    # Check if we're in the save step (confirm_save=true)
    confirm_save = request.POST.get('confirm_save', False)

    if confirm_save and 'pdf_extraction_data' in request.session:
        # Second step: Load extraction data from session for saving
        extraction_data = request.session.get('pdf_extraction_data')
        json_preview = json.dumps(extraction_data, indent=2, ensure_ascii=False)
    elif request.method == "POST" and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']

        # Create temporary file
        import tempfile
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, pdf_file.name)

        try:
            # Save uploaded file
            with open(temp_path, 'wb+') as destination:
                for chunk in pdf_file.chunks():
                    destination.write(chunk)

            # Import and use improved PDF extractor
            from apps.sport.utils.pdf_extractor_final import VolleyballPDFExtractor

            # Extract data from PDF to JSON
            extractor = VolleyballPDFExtractor()
            extraction_data = extractor.extract(temp_path)

            # Check for extraction errors
            if 'error' in extraction_data:
                messages.error(
                    request,
                    _("PDF Extraction Error: ") + extraction_data['error'],
                    extra_tags='Players'
                )
                context = {
                    'match': match,
                    'current_page': _('Upload PDF Statistics'),
                    'error': extraction_data['error'],
                    'log': extraction_data.get('log', [])
                }
                return render(request, f'{BACKEND_TEMPLATES}/sport/match/statics_pdf.html', context)

            # Check if data was extracted
            if not extraction_data.get('teams'):
                messages.warning(
                    request,
                    _("No players found in PDF. Please verify the PDF format and try again."),
                    extra_tags='Players'
                )
                context = {
                    'match': match,
                    'current_page': _('Upload PDF Statistics'),
                    'error': 'No data extracted',
                    'log': extraction_data.get('log', [])
                }
                return render(request, f'{BACKEND_TEMPLATES}/sport/match/statics_pdf.html', context)

            # Generate JSON preview
            json_preview = json.dumps(extraction_data, indent=2, ensure_ascii=False)

            # Save to session for the second form submission (save confirmation)
            request.session['pdf_extraction_data'] = extraction_data
            request.session.modified = True

            # Check if user wants to confirm and save
            confirm_save = request.POST.get('confirm_save', False)

            if not confirm_save:
                # Show preview without saving
                messages.info(
                    request,
                    _(f"Preview: Found {extraction_data['total_players']} players in {len(extraction_data['teams'])} team(s). Review the data and confirm to save."),
                    extra_tags='Players'
                )
                context = {
                    'match': match,
                    'current_page': _('Upload PDF Statistics'),
                    'extraction_data': extraction_data,
                    'json_preview': json_preview,
                    'teams_count': len(extraction_data['teams']),
                    'players_count': extraction_data.get('total_players', 0),
                    'log': extraction_data.get('log', [])
                }
                return render(request, f'{BACKEND_TEMPLATES}/sport/match/statics_pdf.html', context)

            # Proceed with saving data to database
            from django.db import transaction
            import logging
            logger = logging.getLogger(__name__)

            updated_count = 0
            skipped_players = []
            errors = []

            # Log match info
            logger.info(f"Saving stats for match: {match}")
            logger.info(f"Home team: {match.home_team} (ID: {match.home_team.id if match.home_team else 'None'})")
            logger.info(f"Away team: {match.away_team} (ID: {match.away_team.id if match.away_team else 'None'})")

            with transaction.atomic():
                for team_data in extraction_data['teams']:
                    for player_data in team_data['players']:
                        try:
                            player_name = player_data.get('player_name', '').strip()
                            player_number = player_data.get('player_number', '').strip()
                            stats = player_data.get('stats', {})

                            if not player_name:
                                continue

                            logger.debug(f"Processing player: {player_name} (#{player_number})")

                            # Strategy 1: Search by exact name match in match teams (case-insensitive)
                            player = Players.objects.filter(
                                name__iexact=player_name,
                                team__in=[match.home_team, match.away_team]
                            ).first()
                            if player:
                                logger.debug(f"  Found via exact name match: {player}")

                            # Strategy 2: Search by partial name match in match teams
                            if not player:
                                player = Players.objects.filter(
                                    name__icontains=player_name,
                                    team__in=[match.home_team, match.away_team]
                                ).first()
                                if player:
                                    logger.debug(f"  Found via partial name match: {player}")

                            # Strategy 3: Try matching by number (in match teams)
                            if not player and player_number:
                                try:
                                    # Try exact number match first
                                    player = Players.objects.filter(
                                        number=player_number,
                                        team__in=[match.home_team, match.away_team]
                                    ).first()
                                    if player:
                                        logger.debug(f"  Found via number match (string): {player}")

                                    # If not found, try as integer
                                    if not player and player_number.isdigit():
                                        player = Players.objects.filter(
                                            number=int(player_number),
                                            team__in=[match.home_team, match.away_team]
                                        ).first()
                                        if player:
                                            logger.debug(f"  Found via number match (int): {player}")
                                except (ValueError, TypeError):
                                    pass

                            # Strategy 4: Try last name matching in match teams
                            if not player and ' ' in player_name:
                                last_name = player_name.split()[-1]
                                player = Players.objects.filter(
                                    name__icontains=last_name,
                                    team__in=[match.home_team, match.away_team]
                                ).first()
                                if player:
                                    logger.debug(f"  Found via last name match: {player}")

                            # Strategy 5: Fallback - search across all players (not just match teams)
                            if not player:
                                player = Players.objects.filter(
                                    name__icontains=player_name
                                ).first()
                                if player:
                                    logger.warning(f"  Found outside match teams: {player} (team: {player.team})")

                            if not player:
                                logger.warning(f"  NOT FOUND: {player_name} (#{player_number})")
                                skipped_players.append({
                                    'name': player_name,
                                    'number': player_number,
                                    'reason': 'Player not found in database or not in match teams'
                                })
                                continue

                            # Prepare stats for database - convert to strings (model uses CharField)
                            defaults = {
                                'point_total': str(stats.get('pts', 0)),
                                'serve_total': str(stats.get('serve_total', 0)),
                                'serve_err': str(stats.get('serve_err', 0)),
                                'serve_ace': str(stats.get('serve_ace', 0)),
                                'reception_total': str(stats.get('reception_total', 0)),
                                'reception_err': str(stats.get('reception_err', 0)),
                                'reception_exc': str(stats.get('reception_exc', 0)),
                                'attack_total': str(stats.get('attack_total', 0)),
                                'attack_err': str(stats.get('attack_err', 0)),
                                'attack_pts': str(stats.get('attack_pts', 0)),
                                'block_pts': str(stats.get('block_pts', 0)),
                                'static_type': 'General'
                            }

                            logger.debug(f"  Saving stats: {defaults}")

                            # Update MatchPlayerReport
                            mpr, created = MatchPlayerReport.objects.update_or_create(
                                player=player,
                                match=match,
                                defaults=defaults
                            )
                            logger.info(f"  MatchPlayerReport {'created' if created else 'updated'}: {player.name}")

                            # Update PlayerStatics (overall cumulative stats)
                            ps, created = PlayerStatics.objects.update_or_create(
                                player=player,
                                defaults=defaults
                            )
                            logger.info(f"  PlayerStatics {'created' if created else 'updated'}: {player.name}")

                            updated_count += 1

                        except Exception as e:
                            logger.error(f"Error saving {player_name}: {str(e)}", exc_info=True)
                            errors.append({
                                'player': player_name,
                                'error': str(e)
                            })
                            continue



            # Build result message
            msg = _(f"✓ Successfully updated statistics for {updated_count} players")

            if skipped_players:
                msg += _(f"\n⚠ Skipped {len(skipped_players)} players not found in database:")
                for p in skipped_players[:5]:
                    msg += f"\n  • {p['name']} (#{p['number']})"
                if len(skipped_players) > 5:
                    msg += f"\n  ... and {len(skipped_players) - 5} more"

            if errors:
                msg += _(f"\n✕ {len(errors)} errors during processing")
                for e in errors[:3]:
                    msg += f"\n  • {e['player']}: {e['error']}"

            if updated_count > 0:
                messages.success(request, msg, extra_tags='Players')
            else:
                messages.warning(request, msg, extra_tags='Players')

            # Clear cached extraction data once save attempt finished
            if 'pdf_extraction_data' in request.session:
                try:
                    del request.session['pdf_extraction_data']
                    request.session.modified = True
                except Exception:
                    pass

            # Render the same page with save results so the user can see what happened
            context = {
                'match': match,
                'current_page': _('Upload PDF Statistics'),
                'extraction_data': extraction_data,
                'json_preview': json_preview,
                'teams_count': len(extraction_data['teams']) if extraction_data else 0,
                'players_count': extraction_data.get('total_players', 0) if extraction_data else 0,
                'log': extraction_data.get('log', []) if extraction_data else [],
                'save_results': {
                    'updated_count': updated_count,
                    'skipped_players': skipped_players,
                    'errors': errors,
                }
            }
            return render(request, f'{BACKEND_TEMPLATES}/sport/match/statics_pdf.html', context)
        except Exception as e:
            pass
    # GET request - show upload form
    context = {
        'match': match,
        'current_page': _('Upload PDF Statistics'),
        'extraction_data': extraction_data,
        'json_preview': json_preview,
    }
    return render(request, f'{BACKEND_TEMPLATES}/sport/match/statics_pdf.html', context)

##########################  Players ################################
@authenticated_staf
@staff_only
def AdminPlayersList(request):
    teams = Teams.objects.all()
    players_list = Players.objects.all()

    query = request.GET.get('q')
    if query:
        players_list = players_list.filter(
            Q(name__icontains=query) | 
            Q(code__icontains=query)
        )

    sort_by = request.GET.get('sort')
    
    if sort_by == 'code':
        players_list = players_list.order_by('code')
    elif sort_by == '-code':
        players_list = players_list.order_by('-code')

    elif sort_by == 'sport':
        players_list = players_list.order_by('sport__name') 
    elif sort_by == '-sport':
        players_list = players_list.order_by('-sport__name')

    else:
        players_list = players_list.order_by('-id')
    paginator = Paginator(players_list, 25) 
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    if request.method == "POST":
        players_form = AdminPlayersForm(request.POST or None, request.FILES or None)
        if players_form:
            name = request.POST.get('name')
            name_tr = request.POST.get('name_tr')
            position = request.POST.get('position')
            age = request.POST.get('age')
            birthdate = request.POST.get('birthdate')
            status = request.POST.get('status')
            height = request.POST.get('height')
            country = request.POST.get('country')
            team = request.POST.get('team')
            leagues = request.POST.getlist('leagues')
            sport = request.POST.get('sport')
            gender = request.POST.get('gender')
            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')
            keyword = request.POST.get('keyword')
            nationality = request.POST.get('nationality') 
            nationality_flag = request.POST.get('nationality_flag') 

            if sport == None or sport == '':
                sport = None
            else:
                sport = Sport.objects.get(id=sport)

            if team == None or team == '':
                team = None
                in_team = 'No'
            else:
                team = Teams.objects.get(id=team)
                in_team = 'Yes'

            player_object = Players(
                name=name,name_tr=name_tr,position=position,age=age,height=height,country=country,team=team,sport=sport,in_team=in_team,
                gender=gender,keyword=keyword,image=image,image_path=image_path,nationality=nationality, nationality_flag=nationality_flag,)
            player_object.save()
            
            for league in leagues:
                try:
                    league_object = Leagues.objects.get(id=league)
                    player_object.league.add(league_object)
                    player_object.save()
                except:
                    pass
            try:
               team.player_count += 1
               team.save()
            except:
               pass

            messages.success(request, _("Players Add Successfully"), extra_tags='Players')
            return HttpResponseRedirect(reverse_lazy('sport:AdminPlayersList'))
        else:
            messages.error(request, _("Players Not Add , Please Try Again"), extra_tags='Players')
    
    else:
        context = {
            'page_obj': page_obj, 
            'players': page_obj.object_list,
            'players_form': AdminPlayersForm(),
            'current_page': _('Players'),
            'teams': teams,
        }

        return render(request, f'{BACKEND_TEMPLATES}/sport/players/multi_source_admin.html', context)
    

@authenticated_staf
@staff_only
def AdminPlayersDetails(request, slug):
    """
    Display player details and optionally fetch TransferMarket data for single player.
    This allows recovery if bulk fetch failed, by fetching data on-demand when viewing player.
    Supports:
    - Fetching basic TransferMarket data
    - Updating TransferMarket URL manually
    - Fetching complete data (profile + transfers + market value history)
    """
    player = Players.objects.get(slug=slug)
    fetch_tm_message = None
    fetch_tm_success = False
    transfers_data = None
    tm_url = None

    # Import the update functions
    from .update_players_transfermarket import (
        get_transfermarket_data_for_player,
        update_player_with_transfermarket_data,
        update_player_transfermarket_url,
        fetch_and_update_player_complete_data,
        get_transfermarket_url_for_player,
        fetch_player_transfers,
        save_player_transfers,
    )

    # Generate TransferMarket URL for display
    tm_url = get_transfermarket_url_for_player(player)

    # Handle POST requests
    if request.method == "POST":
        action = request.POST.get('action')

        # Action 1: Fetch basic TransferMarket data
        if action == 'fetch_transfermarket':
            try:
                # Fetch TransferMarket data for this single player
                tm_data = get_transfermarket_data_for_player(player)

                if tm_data:
                    # Update player with TransferMarket data
                    update_player_with_transfermarket_data(player, tm_data)
                    fetch_tm_success = True
                    fetch_tm_message = f"✓ TransferMarket data updated successfully for {player.name}"
                    # Refresh player from database to get updated data
                    player.refresh_from_db()
                    # Regenerate URL
                    tm_url = get_transfermarket_url_for_player(player)
                else:
                    fetch_tm_message = f"⚠ No TransferMarket data found for {player.name}. Try updating the TransferMarket URL manually below."

            except Exception as e:
                fetch_tm_message = f"✗ Error fetching TransferMarket data: {str(e)}"
                import traceback
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error fetching TM data for player {player.id}: {traceback.format_exc()}")

        # Action 2: Update TransferMarket URL manually
        elif action == 'update_tm_url':
            new_tm_url = request.POST.get('transfermarket_url', '').strip()
            new_tm_id = request.POST.get('transfermarket_id', '').strip()

            if new_tm_url or new_tm_id:
                try:
                    success, message = update_player_transfermarket_url(
                        player,
                        transfermarkt_url=new_tm_url if new_tm_url else None,
                        transfermarkt_id=new_tm_id if new_tm_id else None
                    )
                    if success:
                        fetch_tm_success = True
                        fetch_tm_message = f"✓ {message}"
                        # Refresh player and regenerate URL
                        player.refresh_from_db()
                        tm_url = get_transfermarket_url_for_player(player)
                    else:
                        fetch_tm_message = f"⚠ {message}"
                except Exception as e:
                    fetch_tm_message = f"✗ Error updating TransferMarket URL: {str(e)}"
            else:
                fetch_tm_message = "⚠ Please provide either a TransferMarket URL or ID"

        # Action 3: Fetch complete data (profile + transfers + market value)
        elif action == 'fetch_complete_data':
            try:
                results = fetch_and_update_player_complete_data(player, force_refresh=True)

                messages_list = []
                if results['profile']['success']:
                    messages_list.append(f"Profile: ✓ {results['profile']['message']}")
                else:
                    messages_list.append(f"Profile: ⚠ {results['profile']['message']}")

                if results['transfers']['success']:
                    messages_list.append(f"Transfers: ✓ {results['transfers']['message']}")
                else:
                    messages_list.append(f"Transfers: ⚠ {results['transfers']['message']}")

                if results['market_value_history']['success']:
                    messages_list.append(f"Market Value History: ✓ {results['market_value_history']['message']}")
                else:
                    messages_list.append(f"Market Value History: ⚠ {results['market_value_history']['message']}")

                fetch_tm_success = results['profile']['success']
                fetch_tm_message = " | ".join(messages_list)

                # Refresh player from database
                player.refresh_from_db()
                tm_url = get_transfermarket_url_for_player(player)

            except Exception as e:
                fetch_tm_message = f"✗ Error fetching complete data: {str(e)}"
                import traceback
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error fetching complete TM data for player {player.id}: {traceback.format_exc()}")

        # Action 4: Fetch transfers only
        elif action == 'fetch_transfers':
            try:
                if player.transfermarkt_id:
                    transfers = fetch_player_transfers(player.transfermarkt_id)
                    if transfers:
                        added, updated, failed = save_player_transfers(player, transfers)
                        fetch_tm_success = True
                        fetch_tm_message = f"✓ Transfers updated: Added={added}, Updated={updated}, Failed={failed}"
                    else:
                        fetch_tm_message = "⚠ No transfers found for this player"
                else:
                    fetch_tm_message = "⚠ Player has no TransferMarket ID. Please fetch TransferMarket data first."
            except Exception as e:
                fetch_tm_message = f"✗ Error fetching transfers: {str(e)}"

    # Get player transfers for display (Transfers is already imported via models.models import)
    player_transfers = Transfers.objects.filter(player=player).select_related('from_team', 'to_team').order_by('-date')[:20]

    # Parse market value history from player keyword if available
    market_value_history = []
    try:
        import json
        if player.keyword:
            keyword_data = json.loads(player.keyword)
            if isinstance(keyword_data, dict) and 'market_value_history' in keyword_data:
                market_value_history = keyword_data['market_value_history']
    except (json.JSONDecodeError, TypeError):
        pass

    teams = Teams.objects.all()
    context = {
        'player': player,
        'teams': teams,
        'players_form': AdminPlayersForm(instance=player),
        'transfer_form': AdminTransfersForm(),
        'current_page': _('Detail'),
        'prev_Page': _('Players'),
        # TransferMarket fetch status
        'fetch_tm_message': fetch_tm_message,
        'fetch_tm_success': fetch_tm_success,
        'has_transfermarket_id': bool(player.transfermarkt_id),
        'transfermarket_url': tm_url,
        'player_transfers': player_transfers,
        'market_value_history': market_value_history,
    }
    return render(request, f'{BACKEND_TEMPLATES}/sport/players/details.html', context)

@authenticated_staf
@staff_only
def AdminPlayersUpdate(request, slug):
    player = Players.objects.get(slug=slug)
    player_transform = Transfers.objects.filter(player=player)
    teams = Teams.objects.all()

    if request.method == "POST":
        players_form = AdminPlayersForm(request.POST or None, request.FILES or None, instance=player)
        transfer_form = AdminTransfersForm(request.POST or None, request.FILES or None)

        if players_form:
            name = request.POST.get('name')
            name_tr = request.POST.get('name_tr')
            short_code = request.POST.get('short_code')
            age = request.POST.get('age')
            birthdate = request.POST.get('birthdate')
            status = request.POST.get('status')
            height = request.POST.get('height')
            position = request.POST.get('position')
            country = request.POST.get('country')
            leagues = request.POST.getlist('leagues')
            sport_id = request.POST.get('sport')
            gender = request.POST.get('gender')
            nationality = request.POST.get('nationality')
            nationality_flag = request.POST.get('nationality_flag') 
            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')
            country_image = request.FILES.get('country_image')
            keyword = request.POST.get('keyword')

            team_id = request.POST.get('team') 
            
            t_team = None 
            in_team = 'No'

            if team_id and team_id != '':
                try:
                    t_team = Teams.objects.get(id=team_id)
                    in_team = 'Yes'
                except Teams.DoesNotExist:
                    t_team = None
            sport_obj = None
            if sport_id and sport_id != '':
                try:
                    sport_obj = Sport.objects.get(id=sport_id)
                except Sport.DoesNotExist:
                    sport_obj = None

            player_object = Players.objects.get(slug=slug)
            player_object.name = name
            player_object.name_tr = name_tr
            player_object.short_code = short_code
            player_object.birthdate = birthdate
            player_object.status = status
            player_object.age = age
            player_object.height = height
            player_object.sport = sport_obj
            player_object.country = country
            player_object.team = t_team 
            player_object.in_team = in_team

            player_object.nationality = nationality
            player_object.nationality_flag = nationality_flag

            if image:
                player_object.image = image
            if country_image:
                player_object.country_image = country_image
            player_object.image_path = image_path
            player_object.gender = gender
            player_object.keyword = keyword
            player_object.position = position
            player_object.save()

            try:
                player_object.league.clear() 
                for league_id in leagues:
                    try:
                        league_object = Leagues.objects.get(id=league_id)
                        player_object.league.add(league_object)
                    except Leagues.DoesNotExist:
                        pass
                player_object.save()
            except Exception as e:
                print(f"Error updating leagues: {e}")

            if t_team: 
                try:
                    date = datetime.now()
                    transfer_object = Transfers(
                        player=player_object, 
                        date=date, 
                        position=position,
                        to_team=t_team
                    )
                    transfer_object.save()
                    t_team.player_count += 1
                    t_team.save()
                except Exception as e:
                    print(f"Error creating transfer: {e}")

            messages.success(request, _("Players Update Successfully"), extra_tags='Players')
            return HttpResponseRedirect(reverse_lazy('sport:AdminPlayersList'))
        else:
            messages.error(request, _("Players Not Update , Please Try Again"), extra_tags='Players')
    else:
        pass

    context = {
        'player': player, 
        'player_transform': player_transform,
        'teams': teams,
        'players_form': AdminPlayersForm(instance=player), 
        'transfer_form': AdminTransfersForm(),
        'current_page': _('Update'),
        'prev_Page': _('Players'), 
    }
    return render(request, f'{BACKEND_TEMPLATES}/sport/players/update.html', context)


@authenticated_staf
@staff_only
def AdminPlayersArchive(request, slug):
    player = Players.objects.get(slug=slug)
    if request.method == 'POST':
        player.status = 'Archive'
        player.save()
        messages.success(request, _("Players Archive Successfully"), extra_tags='Players')
        return HttpResponseRedirect(reverse_lazy('sport:AdminPlayersList'))
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminPlayersList'))


@authenticated_staf
@staff_only
def AdminPlayersDelete(request, slug):
    player = Players.objects.get(slug=slug)

    if request.method == "POST":
        player.delete()

        messages.success(request, _("Players Delete Successfully"), extra_tags='Players')

        return HttpResponseRedirect(reverse_lazy('sport:AdminPlayersList'))
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminPlayersList'))


@authenticated_staf
@staff_only
def AdminPlayerStaticAdd(request, slug):
    player = Players.objects.get(slug=slug)
    try:
        player_statics = PlayerStatics.objects.get(player=player)
    except:
        player_statics = None

    if request.method == "POST":
        static_form = AdminPlayerStaticsForm(request.POST or None, request.FILES or None)
        if static_form:

            cut_ball= request.POST.get('cut_ball')
            shot_ball = request.POST.get('shot_ball')
            score_ball = request.POST.get('score_ball')
            set1 = request.POST.get('set1')
            set2 = request.POST.get('set2')
            set3 = request.POST.get('set3')
            set4 = request.POST.get('set4')
            set5 = request.POST.get('set5')
            vote =  request.POST.get('vote')
            point_total = request.POST.get('point_total')
            position = request.POST.get('position')
            point_bp = request.POST.get('point_bp')
            point_wl = request.POST.get('point_wl')
            serve_total = request.POST.get('serve_total')
            serve_err = request.POST.get('serve_err')
            serve_pts = request.POST.get('serve_pts')
            reception_total = request.POST.get('reception_total')
            reception_err = request.POST.get('reception_err')
            reception_pos = request.POST.get('reception_pos')
            reception_exc = request.POST.get('reception_exc')
            attack_total = request.POST.get('attack_total')
            attack_err = request.POST.get('attack_err')
            attack_pos = request.POST.get('attack_pos')
            attack_exc = request.POST.get('attack_exc')
            block_pts = request.POST.get('block_pts')
            static_type = request.POST.get('static_type')

            try:
                player_statics_object = PlayerStatics.objects.get(player=player)
                player_statics_object.cut_ball = cut_ball
                player_statics_object.shot_ball = shot_ball
                player_statics_object.score_ball = score_ball
                player_statics_object.set1 = set1
                player_statics_object.set2 = set2
                player_statics_object.set3 = set3
                player_statics_object.set4 = set4
                player_statics_object.set5 = set5
                player_statics_object.vote = vote
                player_statics_object.point_total = point_total
                player_statics_object.position = position
                player_statics_object.point_bp = point_bp
                player_statics_object.point_wl = point_wl
                player_statics_object.serve_total = serve_total
                player_statics_object.serve_err = serve_err
                player_statics_object.serve_pts = serve_pts
                player_statics_object.reception_total = reception_total
                player_statics_object.reception_err = reception_err
                player_statics_object.reception_pos = reception_pos
                player_statics_object.reception_exc = reception_exc
                player_statics_object.attack_total = attack_total
                player_statics_object.attack_err = attack_err
                player_statics_object.attack_pos = attack_pos
                player_statics_object.attack_exc = attack_exc
                player_statics_object.block_pts = block_pts
                player_statics_object.static_type = 'General'
                player_statics_object.save()
            except:

                player_statics_object = PlayerStatics(player=player,cut_ball=cut_ball,shot_ball=shot_ball,score_ball=score_ball,set1=set1,set2=set2,set3=set3,set4=set4,set5=set5,
                                                 vote=vote,point_total=point_total,position=position,
                                                      point_bp=point_bp,point_wl=point_wl,serve_total=serve_total,
                                                 serve_err=serve_err,serve_pts=serve_pts,reception_total=reception_total,reception_err=reception_err,
                                                 reception_pos=reception_pos,reception_exc=reception_exc,attack_total=attack_total,attack_err=attack_err,
                                                 attack_pos=attack_pos,attack_exc=attack_exc,block_pts=block_pts,static_type='General')
            player_statics_object.save()
            messages.success(request, _("Player Statics Add Successfully"), extra_tags='Players')
            return HttpResponseRedirect(reverse_lazy('sport:AdminPlayersList'))
        else:
            messages.error(request, _("Player Statics Not Add , Please Try Again"), extra_tags='Players')

    context = {'player': player,
               'player_statics': player_statics, 'static_form': AdminPlayerStaticsForm(), 'current_page': _('Add Statics'),

                'prev_Page': _('Players'), }
    return render(request, f'{BACKEND_TEMPLATES}/sport/players/statics.html', context)

##########################  Match ################################
# @authenticated_staf
# @staff_only
# def AdminMatchList(request):
#     # The POST logic for adding a new match remains the same.
#     if request.method == "POST":
#         matches_form = AdminMatchForm(request.POST or None, request.FILES or None)
#         if matches_form.is_valid():  # Added form validation check
#             home_team_id = request.POST.get('home_team')
#             away_team_id = request.POST.get('away_team')

#             if home_team_id == away_team_id:
#                 messages.error(request, _("Home Team and Away Team Can't Be Same"), extra_tags='Match')
#                 return HttpResponseRedirect(reverse_lazy('sport:AdminMatchList'))

#             # Your existing POST logic continues here...
#             round_id = request.POST.get('round')
#             venues_id = request.POST.get('venues')
#             played = request.POST.get('played')
#             start_time = request.POST.get('start_time')

#             home_team = Teams.objects.get(id=home_team_id)
#             away_team = Teams.objects.get(id=away_team_id)
#             round_obj = Round.objects.get(id=round_id)

#             if home_team.sport != round_obj.sport or away_team.sport != round_obj.sport:
#                 messages.error(request, _("Home Team and Away Team Sport Not Match with Round Sport"), extra_tags='Match')
#                 return HttpResponseRedirect(reverse_lazy('sport:AdminMatchList'))

#             name = home_team.name + ' vs ' + away_team.name
#             venues = Venues.objects.get(id=venues_id) if venues_id else None

#             match_object = Match(
#                 name=name,
#                 home_team=home_team,
#                 away_team=away_team,
#                 round=round_obj,
#                 group=round_obj.group,
#                 league=round_obj.league,
#                 season=round_obj.season,
#                 sport=round_obj.sport,
#                 played=played,
#                 venues=venues,
#                 start_time=start_time,
#             )
#             match_object.save()
#             messages.success(request, _("Match Add Successfully"), extra_tags='Match')
#             return HttpResponseRedirect(reverse_lazy('sport:AdminMatchList'))
#         else:
#             messages.error(request, _("Match Not Add , Please Try Again"), extra_tags='Match')

#     # --- PAGINATION LOGIC FOR GET REQUEST ---

#     # 1. Get the full list of fixtures
#     fixtures_list = Fixtures.objects.all().order_by('starting_at')

#     # 2. Create a Paginator object (e.g., 25 items per page)
#     paginator = Paginator(fixtures_list, 25)

#     # 3. Get the page number from the URL query parameter
#     page_number = request.GET.get('page')

#     # 4. Get the corresponding page object
#     try:
#         page_obj = paginator.page(page_number)
#     except PageNotAnInteger:
#         # If page is not an integer, deliver first page.
#         page_obj = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range (e.g. 9999), deliver last page of results.
#         page_obj = paginator.page(paginator.num_pages)

#     # Get dropdown data for Add Fixture modal
#     sports_data = list(Sport.objects.values('id', 'name'))
#     leagues_data = list(Leagues.objects.values('id', 'name'))
#     seasons_data = list(Season.objects.values('id', 'name'))
#     venues_data = list(Venues.objects.values('id', 'name'))
#     teams_data = list(Teams.objects.filter(status='Active').values('id', 'name'))


#     context = {
#         'page_obj': page_obj,
#         'matches_form': AdminMatchForm(),
#         'current_page': _('Match'),
#         'sports': json.dumps(sports_data),
#         'leagues': json.dumps(leagues_data),
#         'seasons': json.dumps(seasons_data),
#         'venues': json.dumps(venues_data),
#         'teams': json.dumps(teams_data),
#     }
#     return render(request, f'{BACKEND_TEMPLATES}/sport/fixtures/admin.html', context)


# def get_periods_count_by_sport(sport_name):
#     periods_config = {
#         'volleyball': 5,
#         'basketball': 4, 
#         'handball': 2,
#         'football' :2,
#     }
#     sport_name_lower = sport_name.lower() if sport_name else ''
#     for sport_key, periods in periods_config.items():
#         if sport_key in sport_name_lower:
#             return periods
#     return 2


@authenticated_staf
@staff_only
def AdminMatchList(request):
    matches = Match.objects.all().order_by('-id')
    if request.method == "POST":
        matches_form = AdminMatchForm(request.POST or None, request.FILES or None)
        if matches_form:
            home_team = request.POST.get('home_team')
            away_team = request.POST.get('away_team')
            round = request.POST.get('round')
            venues = request.POST.get('venues')
            played = request.POST.get('played')
            start_time = request.POST.get('start_time')
            home_team = Teams.objects.get(id=home_team)
            away_team = Teams.objects.get(id=away_team)
            round = Round.objects.get(id=round)
            if home_team == away_team:
                messages.error(request, _("Home Team and Away Team Can't Be Same"), extra_tags='Match')
                return HttpResponseRedirect(reverse_lazy('sport:AdminMatchList'))
            if home_team.sport != round.sport or away_team.sport != round.sport:
                messages.error(request, _("Home Team and Away Team Sport Not Match with Round Sport"), extra_tags='Match')
                return HttpResponseRedirect(reverse_lazy('sport:AdminMatchList'))
            name = home_team.name + ' vs ' + away_team.name
            if venues == None or venues == '':
                venues = None
            else:
                venues = Venues.objects.get(id=venues)
            match_object = Match(name=name,home_team=home_team,away_team=away_team,
                                    round=round,group=round.group,league=round.league,season=round.season,
                                    sport=round.sport,played=played,venues=venues,start_time=start_time,)
            match_object.save()
            messages.success(request, _("Match Add Successfully"), extra_tags='Match')
            return HttpResponseRedirect(reverse_lazy('sport:AdminMatchList'))
        else:
            messages.error(request, _("Match Not Add , Please Try Again"), extra_tags='Match')
    else:
        context = {'matches': matches, 'matches_form': AdminMatchForm(), 'current_page': _('Match')}
        return render(request, f'{BACKEND_TEMPLATES}/sport/match/admin.html', context)

@authenticated_staf
@staff_only
def AdminMatchUpdate(request, slug):
    match = Match.objects.get(slug=slug)

    if request.method == "POST":
        matches_form = AdminMatchForm(request.POST or None, request.FILES or None, instance=match)
        if matches_form:
            home_team = request.POST.get('home_team')
            away_team = request.POST.get('away_team')
            location = request.POST.get('location')
            round = request.POST.get('round')
            played = request.POST.get('played')
            start_time = request.POST.get('start_time')

            home_team = Teams.objects.get(id=home_team)
            away_team = Teams.objects.get(id=away_team)
            round = Round.objects.get(id=round)

            if home_team == away_team:
                messages.error(request, _("Home Team and Away Team Can't Be Same"), extra_tags='Match')
                return HttpResponseRedirect(reverse_lazy('sport:AdminMatchUpdate', kwargs={'slug': slug}))
            if home_team.sport != round.sport or away_team.sport != round.sport:
                messages.error(request, _("Home Team and Away Team Sport Not Match with Round Sport"), extra_tags='Match')
                return HttpResponseRedirect(reverse_lazy('sport:AdminMatchUpdate', kwargs={'slug': slug}))

            if start_time == None or start_time == '':
                start_time = match.start_time
            else:
                start_time = start_time



            match_object = Match.objects.get(slug=slug)
            match_object.home_team = home_team
            match_object.away_team = away_team
            match_object.location = location
            match_object.round = round
            match_object.played = played
            match_object.start_time = start_time
            match_object.save()

            messages.success(request, _("Match Update Successfully"), extra_tags='Match')
            return redirect(request.META['HTTP_REFERER'])
        else:
            messages.error(request, _("Match Not Update , Please Try Again"), extra_tags='Match')
    context = {'match': match, 'matches_form': AdminMatchForm(instance=match), 'current_page': _('Update'),
                'prev_Page': _('Match'), }
    return render(request, f'{BACKEND_TEMPLATES}/sport/match/update.html', context)


# @authenticated_staf
# @staff_only
# def AdminFixtureAdd(request):
#     if request.method == "POST":
#         try:
#             # Get required fields
#             name = request.POST.get('name')
#             short_name = request.POST.get('short_name')
#             home_team_id = request.POST.get('home_team')
#             away_team_id = request.POST.get('away_team')
#             sport_id = request.POST.get('sport')
            
#             if not name or not short_name:
#                 return JsonResponse({
#                     'type': 'Error', 
#                     'message': 'Name and Short Name are required.'
#                 }, status=400)
            
#             # Create fixture object
#             fixture = Fixtures()
#             fixture.name = name
#             fixture.short_name = short_name
#             is_finished = request.POST.get('is_finished') == 'true'
            
#             if is_finished:
#                 fixture.state_data = {
#                     "id": 5,
#                     "name": "Full Time",
#                     "state": "FT",
#                     "short_name": "FT",
#                     "developer_name": "FT"
#                 }
#             else:
#                 fixture.state_data = {
#                     "id": 1, 
#                     "name": "Not Started",
#                     "state": "NS",
#                     "short_name": "NS",
#                     "developer_name": "NS"
#                 }
#             # Optional fields
#             sport_id = request.POST.get('sport')
#             if sport_id:
#                 try:
#                     fixture.sport = Sport.objects.get(id=sport_id)
#                 except Sport.DoesNotExist:
#                     fixture.sport = None

#             league_id = request.POST.get('league')
#             if league_id:
#                 try:
#                     fixture.league = Leagues.objects.get(id=league_id)
#                 except Leagues.DoesNotExist:
#                     fixture.league = None

#             season_id = request.POST.get('season')
#             if season_id:
#                 try:
#                     fixture.season = Season.objects.get(id=season_id)
#                 except Season.DoesNotExist:
#                     fixture.season = None

#             venue_id = request.POST.get('venue')
#             if venue_id:
#                 try:
#                     fixture.venue = Venues.objects.get(id=venue_id)
#                 except Venues.DoesNotExist:
#                     fixture.venue = None

#             starting_at = request.POST.get('starting_at')
#             if starting_at:
#                 fixture.starting_at = starting_at
            
#             details = request.POST.get('details')
#             if details:
#                 fixture.details = details
            
#             # Get teams
#             home_team_id = request.POST.get('home_team')
#             away_team_id = request.POST.get('away_team')

#             if not home_team_id or not away_team_id:
#                 return JsonResponse({
#                     'type': 'Error',
#                     'message': _("Both Home Team and Away Team are required")
#                 }, status=400)

#             if home_team_id == away_team_id:
#                 return JsonResponse({
#                     'type': 'Error',
#                     'message': _("Home Team and Away Team cannot be the same")
#                 }, status=400)

#             try:
#                 home_team = Teams.objects.get(id=home_team_id)
#                 away_team = Teams.objects.get(id=away_team_id)
#             except Teams.DoesNotExist:
#                 return JsonResponse({
#                     'type': 'Error',
#                     'message': _("Selected team not found")
#                 }, status=400)
            
#             # Update is_finished state
#             is_finished = request.POST.get('is_finished') == 'true'

#             if is_finished:
#                 # Match is finished - update state and scores
#                 fixture.state_data = {
#                     "id": 5,
#                     "name": "Full Time",
#                     "state": "FT",
#                     "short_name": "FT",
#                     "developer_name": "FT"
#                 }

#                 # Process periods if exists
#                 periods_data = []
#                 total_home_goals = 0
#                 total_away_goals = 0
                
#                 sport_name = fixture.sport.name if fixture.sport else ''
#                 periods_count = get_periods_count_by_sport(sport_name)
                
#                 if periods_count > 0:
#                     # Get periods data from POST
#                     for i in range(1, periods_count + 1):
#                         home_goals_key = f'period_{i}_home'
#                         away_goals_key = f'period_{i}_away'

#                         home_goals = request.POST.get(home_goals_key, '0')
#                         away_goals = request.POST.get(away_goals_key, '0')

#                         try:
#                             home_goals_int = int(home_goals) if home_goals else 0
#                             away_goals_int = int(away_goals) if away_goals else 0

#                             if home_goals_int < 0 or away_goals_int < 0:
#                                 return JsonResponse({
#                                     'type': 'Error',
#                                     'message': f'Goals cannot be negative in period {i}'
#                                 }, status=400)

#                             period_data = {
#                                 "period_number": i,
#                                 "home_goals": home_goals_int,
#                                 "away_goals": away_goals_int,
#                                 "period_name": f"Set {i}" if sport_name.lower() == 'volleyball' else f"Period {i}"
#                             }
#                             periods_data.append(period_data)

#                             # Calculate total based on sport type
#                             if sport_name.lower() == 'volleyball':
#                                 if home_goals_int > away_goals_int:
#                                     total_home_goals += 1
#                                 elif away_goals_int > home_goals_int:
#                                     total_away_goals += 1
#                             else:
#                                 total_home_goals += home_goals_int
#                                 total_away_goals += away_goals_int

#                         except ValueError:
#                             return JsonResponse({
#                                 'type': 'Error',
#                                 'message': f'Invalid goals value in period {i}. Please enter valid numbers.'
#                             }, status=400)

#                 fixture.periods = periods_data
                
#                 fixture.scores = [
#                     {
#                         "id": home_team.id,
#                         "score": {
#                             "goals": total_home_goals,
#                             "participant_name": home_team.name,
#                             "meta_location": "home"
#                         }
#                     },
#                     {
#                         "id": away_team.id,
#                         "score": {
#                             "goals": total_away_goals,
#                             "participant_name": away_team.name,
#                             "meta_location": "away"
#                         }
#                     }
#                 ]
                
#             else:
#                 # Match not finished - clear scores and set state to Not Started
#                 fixture.state_data = {
#                     "id": 1,
#                     "name": "Not Started",
#                     "state": "NS",
#                     "short_name": "NS",
#                     "developer_name": "NS"
#                 }
#                 fixture.scores = None
#                 fixture.periods = None

#             # Save fixture
#             fixture.save()

#             # Update participants
#             # Delete old participants
#             FixtureParticipant.objects.filter(fixture=fixture).delete()

#             # Create new participants
#             FixtureParticipant.objects.create(
#                 fixture=fixture,
#                 team=home_team,
#                 meta_location='home'
#             )

#             FixtureParticipant.objects.create(
#                 fixture=fixture,
#                 team=away_team,
#                 meta_location='away'
#             )

#             return JsonResponse({
#                 'type': 'Success',
#                 'message': _("Fixture updated successfully")
#             })

#         except Exception as e:
#             return JsonResponse({
#                 'type': 'Error',
#                 'message': f"Error updating fixture: {str(e)}"
#             }, status=400)
    
#     return JsonResponse({'type': 'Error', 'message': 'Invalid request method.'}, status=400)


@authenticated_staf
@staff_only
def AdminMatchBySeason(request, slug):
    season = Season.objects.get(slug=slug)
    matches = Match.objects.filter(season=season)
    teams = Teams.objects.all()
    # teams = Teams.objects.filter(sport=season.sport.id, country=season.league.country)
    season_table = TeamSeasonTable.objects.filter(league=season.league, )
    if season_table.count()>0:
        table_exist = 'True'
    else:
        table_exist = 'False'

    if request.method == "POST":
        matches_form = AdminMatchForm(request.POST or None, request.FILES or None)
        if matches_form:
            home_team = request.POST.get('home_team')
            away_team = request.POST.get('away_team')
            round = request.POST.get('round')
            venues = request.POST.get('venues')
            played = request.POST.get('played')
            start_time = request.POST.get('start_time')

            home_team = Teams.objects.get(id=home_team)
            away_team = Teams.objects.get(id=away_team)
            round = Round.objects.get(id=round)

            if home_team == away_team:
                messages.error(request, _("Home Team and Away Team Can't Be Same"), extra_tags='Match')
                return HttpResponseRedirect(reverse_lazy('sport:AdminMatchList'))
            if home_team.sport != round.sport or away_team.sport != round.sport:
                messages.error(request, _("Home Team and Away Team Sport Not Match with Round Sport"),
                               extra_tags='Match')
                return HttpResponseRedirect(reverse_lazy('sport:AdminMatchList'))

            name = home_team.name + ' vs ' + away_team.name
            if venues == None or venues == '':
                venues = None
            else:
                venues = Venues.objects.get(id=venues)

            match_object = Match(name=name,
                                 home_team=home_team, away_team=away_team, round=round, group=round.group,
                                 league=round.league, season=round.season, sport=round.sport,

                                 played=played, venues=venues, start_time=start_time, )
            match_object.save()
            messages.success(request, _("Match Add Successfully"), extra_tags='Match')
            return HttpResponseRedirect(reverse_lazy('sport:AdminMatchBySeason', kwargs={'slug': slug}))
        else:
            messages.error(request, _("Match Not Add , Please Try Again"), extra_tags='Match')
    else:
        context = {'season':season,'matches': matches,'teams': teams,'season_table':season_table,'table_exist':table_exist,
                   'matches_form': AdminMatchForm(),'teams_form':AdminTeamsForm(), 'current_page': _('Match')}
        return render(request, f'{BACKEND_TEMPLATES}/sport/season/match.html', context)


@authenticated_staf
@staff_only
def AdminMatchDetails(request, slug):
    match = Match.objects.get(slug=slug)
    summary = MatchSummary.objects.filter(match=match,)
    summary_goal = MatchSummary.objects.filter(match=match)
    home_team = Teams.objects.get(id=match.home_team.id)
    away_team = Teams.objects.get(id=match.away_team.id)
    home_players = MatchTeamPlayer.objects.filter(match=match,team=home_team.id)
    away_players = MatchTeamPlayer.objects.filter(match=match, team=away_team.id)
    match_goal = MatchGoals.objects.filter(match=match)
    home_summary = MatchSummary.objects.filter(match=match,team=home_team)
    away_summary = MatchSummary.objects.filter(match=match, team=away_team)
    last_summary = MatchSummary.objects.filter(match=match).last()
    match_statics = MatchStatics.objects.filter(match=match)
    last_statics = MatchStatics.objects.filter(match=match).last()



    context = {
        'match':match,'summary':summary,'summary_goal':summary_goal,
        'home_team':home_team,
        'away_team':away_team,'home_players':home_players,
        'away_players':away_players, 'match_goal':match_goal,
        'home_summary':home_summary,'away_summary':away_summary,
        'last_summary':last_summary,
        'summary_form': AdminMatchSummaryForm(),
        'static_form': AdminMatchStaticsForm(),
        'match_statics':match_statics,
        'last_statics':last_statics,
        'match_form': AdminMatchForm(instance=match),
        'current_page': _('Details')}
    return render(request, f'{BACKEND_TEMPLATES}/sport/match/details.html', context)




# @authenticated_staf
# @staff_only
# def AdminMatchUpdate(request, slug):
    try:
        fixture = Fixtures.objects.get(slug=slug)
    except Fixtures.DoesNotExist:
        messages.error(request, _("Fixture not found"), extra_tags='Fixture')
        return redirect('sport:AdminMatchList')

    # Get current participants
    participants = FixtureParticipant.objects.filter(fixture=fixture)
    home_participant = participants.filter(meta_location='home').first()
    away_participant = participants.filter(meta_location='away').first()

    if request.method == "POST":
        try:
            # Update basic fixture data
            fixture.name = request.POST.get('name')
            fixture.short_name = request.POST.get('short_name')

            # Update optional fields
            sport_id = request.POST.get('sport')
            if sport_id:
                try:
                    fixture.sport = Sport.objects.get(id=sport_id)
                except Sport.DoesNotExist:
                    fixture.sport = None
            else:
                fixture.sport = None

            league_id = request.POST.get('league')
            if league_id:
                try:
                    fixture.league = Leagues.objects.get(id=league_id)
                except Leagues.DoesNotExist:
                    fixture.league = None
            else:
                fixture.league = None

            season_id = request.POST.get('season')
            if season_id:
                try:
                    fixture.season = Season.objects.get(id=season_id)
                except Season.DoesNotExist:
                    fixture.season = None
            else:
                fixture.season = None

            venue_id = request.POST.get('venue')
            if venue_id:
                try:
                    fixture.venue = Venues.objects.get(id=venue_id)
                except Venues.DoesNotExist:
                    fixture.venue = None
            else:
                fixture.venue = None

            # Update starting_at
            starting_at = request.POST.get('starting_at')
            if starting_at:
                fixture.starting_at = starting_at
            else:
                fixture.starting_at = None

            # Update details
            details = request.POST.get('details')
            fixture.details = details if details else None

            # Get teams
            home_team_id = request.POST.get('home_team')
            away_team_id = request.POST.get('away_team')

            if not home_team_id or not away_team_id:
                return JsonResponse({
                    'type': 'Error',
                    'message': _("Both Home Team and Away Team are required")
                }, status=400)

            if home_team_id == away_team_id:
                return JsonResponse({
                    'type': 'Error',
                    'message': _("Home Team and Away Team cannot be the same")
                }, status=400)

            try:
                home_team = Teams.objects.get(id=home_team_id)
                away_team = Teams.objects.get(id=away_team_id)
            except Teams.DoesNotExist:
                return JsonResponse({
                    'type': 'Error',
                    'message': _("Selected team not found")
                }, status=400)

            # Update is_finished state
            is_finished = request.POST.get('is_finished') == 'true'

            if is_finished:
                # Match is finished - update state and scores
                fixture.state_data = {
                    "id": 5,
                    "name": "Full Time",
                    "state": "FT",
                    "short_name": "FT",
                    "developer_name": "FT"
                }

                # Process periods if exists
                periods_data = []
                total_home_goals = 0
                total_away_goals = 0

                sport_name = fixture.sport.name if fixture.sport else ''
                periods_count = get_periods_count_by_sport(sport_name)

                if periods_count > 0:
                    # Get periods data from POST
                    for i in range(1, periods_count + 1):
                        home_goals_key = f'period_{i}_home'
                        away_goals_key = f'period_{i}_away'

                        home_goals = request.POST.get(home_goals_key, '0')
                        away_goals = request.POST.get(away_goals_key, '0')

                        try:
                            home_goals_int = int(home_goals) if home_goals else 0
                            away_goals_int = int(away_goals) if away_goals else 0

                            if home_goals_int < 0 or away_goals_int < 0:
                                return JsonResponse({
                                    'type': 'Error',
                                    'message': f'Goals cannot be negative in period {i}'
                                }, status=400)

                            period_data = {
                                "period_number": i,
                                "home_goals": home_goals_int,
                                "away_goals": away_goals_int,
                                "period_name": f"Set {i}" if sport_name.lower() == 'volleyball' else f"Period {i}"
                            }
                            periods_data.append(period_data)

                            # Calculate total based on sport type
                            if sport_name.lower() == 'volleyball':
                                if home_goals_int > away_goals_int:
                                    total_home_goals += 1
                                elif away_goals_int > home_goals_int:
                                    total_away_goals += 1
                            else:
                                total_home_goals += home_goals_int
                                total_away_goals += away_goals_int

                        except ValueError:
                            return JsonResponse({
                                'type': 'Error',
                                'message': f'Invalid goals value in period {i}. Please enter valid numbers.'
                            }, status=400)

                    fixture.periods = periods_data
                else:
                    # No periods - use direct goals input
                    home_goals = request.POST.get('home_goals')
                    away_goals = request.POST.get('away_goals')

                    if home_goals is None or away_goals is None or home_goals == '' or away_goals == '':
                        return JsonResponse({
                            'type': 'Error',
                            'message': _("Please provide scores for both teams when match is finished")
                        }, status=400)

                    try:
                        total_home_goals = int(home_goals)
                        total_away_goals = int(away_goals)

                        if total_home_goals < 0 or total_away_goals < 0:
                            return JsonResponse({
                                'type': 'Error',
                                'message': _("Goals cannot be negative")
                            }, status=400)
                    except ValueError:
                        return JsonResponse({
                            'type': 'Error',
                            'message': _("Invalid goal values. Please enter valid numbers")
                        }, status=400)

                    fixture.periods = None

                # Update scores
                fixture.scores = [
                    {
                        "id": home_team.id,
                        "score": {
                            "goals": total_home_goals,
                            "participant_name": home_team.name,
                            "meta_location": "home"
                        }
                    },
                    {
                        "id": away_team.id,
                        "score": {
                            "goals": total_away_goals,
                            "participant_name": away_team.name,
                            "meta_location": "away"
                        }
                    }
                ]
            else:
                # Match not finished - clear scores and set state to Not Started
                fixture.state_data = {
                    "id": 1,
                    "name": "Not Started",
                    "state": "NS",
                    "short_name": "NS",
                    "developer_name": "NS"
                }
                fixture.scores = None
                fixture.periods = None

            # Save fixture
            fixture.save()

            # Update participants
            # Delete old participants
            FixtureParticipant.objects.filter(fixture=fixture).delete()

            # Create new participants
            FixtureParticipant.objects.create(
                fixture=fixture,
                team=home_team,
                meta_location='home'
            )

            FixtureParticipant.objects.create(
                fixture=fixture,
                team=away_team,
                meta_location='away'
            )

            return JsonResponse({
                'type': 'Success',
                'message': _("Fixture updated successfully")
            })

        except Exception as e:
            return JsonResponse({
                'type': 'Error',
                'message': f"Error updating fixture: {str(e)}"
            }, status=400)

    # GET request - display form
    # Get dropdown data
    sports = Sport.objects.all()
    leagues = Leagues.objects.all()
    seasons = Season.objects.all()
    venues = Venues.objects.all()
    teams = Teams.objects.all()

    # Serialize dropdown data for Vue.js
    sports_data = [{'id': s.id, 'name': s.name} for s in sports]
    leagues_data = [{'id': l.id, 'name': l.name} for l in leagues]
    seasons_data = [{'id': s.id, 'name': s.name} for s in seasons]
    venues_data = [{'id': v.id, 'name': v.name} for v in venues]
    teams_data = [{'id': t.id, 'name': t.name} for t in teams]

    # Get current scores and periods if match is finished
    current_scores = {
        'home_goals': 0,
        'away_goals': 0,
        'is_finished': False
    }

    current_periods = []

    if fixture.state_data and fixture.state_data.get('state') == 'FT':
        current_scores['is_finished'] = True

        # Get scores
        if fixture.scores:
            for score_data in fixture.scores:
                if score_data.get('score', {}).get('meta_location') == 'home':
                    current_scores['home_goals'] = score_data.get('score', {}).get('goals', 0)
                elif score_data.get('score', {}).get('meta_location') == 'away':
                    current_scores['away_goals'] = score_data.get('score', {}).get('goals', 0)

        # Get periods
        if fixture.periods:
            for period in fixture.periods:
                current_periods.append({
                    'home': period.get('home_goals', 0),
                    'away': period.get('away_goals', 0)
                })

    context = {
        'fixture': fixture,
        'home_team': home_participant.team if home_participant else None,
        'away_team': away_participant.team if away_participant else None,
        'current_scores': current_scores,
        'current_periods': json.dumps(current_periods),
        'sports': json.dumps(sports_data),
        'leagues': json.dumps(leagues_data),
        'seasons': json.dumps(seasons_data),
        'venues': json.dumps(venues_data),
        'teams': json.dumps(teams_data),
        'current_page': _('Update Fixture'),
        'prev_Page': _('Fixtures'),
        'prev_Page_link': reverse_lazy('sport:AdminMatchList'),
    }

    return render(request, f'{BACKEND_TEMPLATES}/sport/fixtures/update.html', context)


@authenticated_staf
@staff_only
def AdminMatchArchive(request, slug):
    match = Match.objects.get(slug=slug)
    if request.method == 'POST':
        match.status = 'Archive'
        match.save()
        messages.success(request, _("Match Archive Successfully"), extra_tags='Match')
        return HttpResponseRedirect(reverse_lazy('sport:AdminMatchList'))
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminMatchList'))


@authenticated_staf
@staff_only
def AdminMatchDelete(request, slug):
    try:
        try:
            fixture = Fixtures.objects.get(slug=slug)
            fixture_name = fixture.name
            
            Match.objects.filter(fixture=fixture).delete()
            
            fixture.delete()
            
            messages.success(request, _(f"Fixture '{fixture_name}' deleted successfully"), extra_tags='Fixture')
            return redirect('sport:AdminMatchList')
            
        except Fixtures.DoesNotExist:
            match = Match.objects.get(slug=slug)
            match_name = match.name
            match.delete()
            messages.success(request, _(f"Match '{match_name}' deleted successfully"), extra_tags='Match')
            return redirect('sport:AdminMatchList')
            
    except Match.DoesNotExist:
        messages.error(request, _("Item not found"), extra_tags='Error')
        return redirect('sport:AdminMatchList')
    except Exception as e:
        messages.error(request, _(f"Error deleting item: {str(e)}"), extra_tags='Error')
        return redirect('sport:AdminMatchList')

@authenticated_staf
@staff_only
def AdminMatchControl(request, slug):

    if request.method == 'POST':
        match_object = Match.objects.get(slug=slug)
        # if request.POST.get('start_time') == None or request.POST.get('start_time') == '':
        #     match_object.start_time = match_object.start_time
        # else:
        #     match_object.start_time = request.POST.get('start_time')
        match_object.current_minute = request.POST.get('current_minute')
        match_object.current_half = request.POST.get('current_half')
        match_object.played = request.POST.get('played')
        match_object.is_live = request.POST.get('is_live')
        match_object.save()
        messages.success(request, _("Match Control Successfully"), extra_tags='Match')
        return HttpResponseRedirect(reverse_lazy('sport:AdminMatchDetails' , kwargs={'slug': slug}))
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminMatchDetails' , kwargs={'slug': slug}))


@authenticated_staf
@staff_only
def AdminMatchSummaryAdd(request, slug):
    match = Match.objects.get(slug=slug)
    home_team = Teams.objects.get(id=match.home_team.id)
    away_team = Teams.objects.get(id=match.away_team.id)
    home_players = MatchTeamPlayer.objects.filter(match=match, team=home_team)
    away_players = MatchTeamPlayer.objects.filter(match=match, team=away_team)
    home_summary = MatchSummary.objects.filter(match=match, team=home_team)
    away_summary = MatchSummary.objects.filter(match=match, team=away_team)

    if request.method == "POST":
        summary_form = AdminMatchSummaryForm(request.POST or None, request.FILES or None)
        if summary_form:
            event_player = request.POST.get('event_player')
            event_type = request.POST.get('event_type')
            event_half = request.POST.get('event_half')
            event_time = request.POST.get('event_time')
            event_set = request.POST.get('event_set')
            event_goal = request.POST.get('event_goal')
            event_team = request.POST.get('event_team')

            if match.sport.name == 'football':
                try:
                    match_goal = MatchGoals.objects.get(match=match)
                except:
                    match_goal = MatchGoals(match=match, home_team=home_team, away_team=away_team,
                                            home_score=0, away_score=0)
                    match_goal.save()
                player = Players.objects.get(slug=event_player)
                event_team = Teams.objects.get(id=player.owner_id)
                match_summary_object = MatchSummary(
                    match=match,team=event_team,player=player,type=event_type,half=event_half,time=event_time)
                match_summary_object.save()
                if event_type == 'Goal':
                    event_team = Teams.objects.get(id=player.owner_id)
                    if event_team == home_team:
                        match_goal.home_score += 1
                        match_goal.save()
                        match.home_score += 1
                        match.save()
                    else:
                        match_goal.away_score += 1
                        match_goal.save()
                        match.away_score += 1
                        match.save()
                match.score = str(match_goal.home_score) + ' - ' + str(match_goal.away_score)
                match.save()

            elif match.sport.name == 'volleyball' or match.sport.name == 'handball' or match.sport.name == 'basketball':
                current_event_time = event_time
                if not current_event_time:
                    current_event_time = match.current_minute
                team = None
                match_goal = None
                event_team_obj = Teams.objects.get(id=event_team)
                event_type = 'Goal'

                try:
                    match_goal = MatchGoals.objects.get(match=match,  set=event_set)
                except:
                    match_goal = MatchGoals(match=match, home_team=home_team,away_team=away_team, home_score=0,
                                            away_score=0, set=event_set)
                    match_goal.save()

                try:
                    match_summary_object = MatchSummary.objects.get(
                        match=match,team=event_team_obj,type=event_type,set=event_set)
                except:
                    match_summary_object = MatchSummary(
                        match=match, 
                        team=event_team_obj, 
                        type=event_type, 
                        time=current_event_time,
                        set=event_set
                    )
                    match_summary_object.save()
                
                if event_team_obj == home_team:
                    match_goal.home_score = event_goal
                    match_goal.save()
                else:
                    match_goal.away_score = event_goal
                    match_goal.save()
            
            messages.success(request, _("Match Event Add Successfully"), extra_tags='Match')
            return HttpResponseRedirect(reverse_lazy('sport:AdminMatchDetails', kwargs={'slug': slug}))
        
        else:
            messages.error(request, _("Match Event Not Add , Please Try Again"), extra_tags='Match')
    
    context = {'match': match,'home_team':home_team,'away_team':away_team,'home_players':home_players,'away_players':away_players,
                'home_summary':home_summary,'away_summary':away_summary,
                'summary_form': AdminMatchSummaryForm(), 'current_page': _('Match Event')}
    return render(request, f'{BACKEND_TEMPLATES}/sport/match/details.html', context)

@authenticated_staf
@staff_only
def AdminMatchStaticAdd(request, slug):
    match = Match.objects.get(slug=slug)
    summary = MatchSummary.objects.filter(match=match, )
    home_team = Teams.objects.get(id=match.home_team.id)
    away_team = Teams.objects.get(id=match.away_team.id)
    home_players = MatchTeamPlayer.objects.filter(match=match, team=home_team.id)
    away_players = MatchTeamPlayer.objects.filter(match=match, team=away_team.id)
    match_goal = MatchSummary.objects.filter(match=match)
    home_summary = MatchSummary.objects.filter(match=match, team=home_team)
    away_summary = MatchSummary.objects.filter(match=match, team=away_team)
    last_summary = MatchSummary.objects.filter(match=match).last()
    match_statics = MatchStatics.objects.filter(match=match)
    last_statics = MatchStatics.objects.filter(match=match).last()


    if request.method == "POST":
        static_form = AdminMatchStaticsForm(request.POST or None, request.FILES or None)
        if static_form:
            home_percent = request.POST.get('home_percent')
            away_percent = request.POST.get('away_percent')
            static_type = request.POST.get('static_type')

            match_static_object = MatchStatics(
                match=match,home_team=home_team,away_team=away_team,home=home_percent,
                away=away_percent,type=static_type)
            match_static_object.save()


            messages.success(request, _("Match Event Add Successfully"), extra_tags='Match')
            return HttpResponseRedirect(reverse_lazy('sport:AdminMatchDetails', kwargs={'slug': slug}))
        else:
            messages.error(request, _("Match Event Not Add , Please Try Again"), extra_tags='Match')
    else:
        context = {
            'match': match, 'summary': summary, 'home_team': home_team,
            'away_team': away_team, 'home_players': home_players,
            'away_players': away_players, 'match_goal': match_goal,
            'home_summary': home_summary, 'away_summary': away_summary,
            'last_summary': last_summary,
            'summary_form': AdminMatchSummaryForm(),
            'static_form': AdminMatchStaticsForm(),
            'match_statics': match_statics,
            'last_statics': last_statics,
            'current_page': _('Details')}
        return render(request, f'{BACKEND_TEMPLATES}/sport/match/details.html', context)


@authenticated_staf
@staff_only
def AdminMatchGoalsAdd(request, slug):
    match = Match.objects.get(slug=slug)
    home_team = Teams.objects.get(id=match.home_team.id)
    away_team = Teams.objects.get(id=match.away_team.id)
    match_goal = MatchSummary.objects.filter(match=match)
    last_goal = MatchSummary.objects.filter(match=match).last()

    if request.method == "POST":
        math_form = AdminMatchForm(request.POST or None, request.FILES or None)
        if math_form:
            home_score = request.POST.get('home_score')
            away_score = request.POST.get('away_score')


            match.home_score = home_score
            match.away_score = away_score
            match.score = str(home_score) + ' - ' + str(away_score)
            match.save()
            messages.success(request, _("Match Event Add Successfully"), extra_tags='Match')
            return HttpResponseRedirect(reverse_lazy('sport:AdminMatchDetails', kwargs={'slug': slug}))
        else:
            messages.error(request, _("Match Event Not Add , Please Try Again"), extra_tags='Match')
    else:
        context = {
            'match': match, 'home_team': home_team,
            'away_team': away_team, 'match_goal': match_goal,
            'last_goal': last_goal,

            'current_page': _('Details')}
        return render(request, f'{BACKEND_TEMPLATES}/sport/match/details.html', context)


##########################  Match Result ################################


@authenticated_staf
@staff_only
def AdminMatchDetailsByTeam(request,slug,team_slug):
    match = Match.objects.get(slug=slug)
    team = Teams.objects.get(slug=team_slug)
    transfer_player = Players.objects.filter(sport=match.sport,in_team='No')
    players = Players.objects.filter(owner_model=ContentType.objects.get(model='Teams'), owner_id=team.id)
    match_players = MatchTeamPlayer.objects.filter(match=match,team=team)
    match_summary = MatchSummary.objects.filter(match=match,team=team)


    context = {'match': match, 'team': team, 'transfer_player': transfer_player,
               'players': players,
                 'match_players': match_players,
               'match_summary':match_summary,
               'players_form': AdminPlayersForm(),
               'match_team_player_form': AdminMatchTeamPlayerForm(),
               'summary_form': AdminMatchSummaryForm(),
               'current_page': _('Match Team Players')}
    return render(request, f'{BACKEND_TEMPLATES}/sport/match/teams.html', context)


@authenticated_staf
@staff_only
def AdminMatchTeamPlayerAdd(request,slug,team_slug):
    match = Match.objects.get(slug=slug)
    team = Teams.objects.get(slug=team_slug)
    players = Players.objects.filter(owner_model=ContentType.objects.get(model='Teams'), owner_id=team.id)
    match_team_players = MatchTeamPlayer.objects.filter(match=match, team=team)
    if request.method == "POST":
        players_form = AdminPlayersForm(request.POST or None, request.FILES or None)
        match_team_player_form = AdminMatchTeamPlayerForm(request.POST or None, request.FILES or None)
        if match_team_player_form:
            team_player = request.POST.getlist('[team_player]')
            team_position = request.POST.getlist('[team_position]')

            for player,position in zip(team_player,team_position ):
                player = Players.objects.get(id=player)
                match_team_player_object = MatchTeamPlayer(
                    match=match,team=team,player=player,position=position
                )
                match_team_player_object.save()
            messages.success(request, _("Match Team Player Add Successfully"), extra_tags='Match Team Player')
            return HttpResponseRedirect(reverse_lazy('sport:AdminMatchDetailsByTeam',kwargs={'slug':slug,'team_slug':team_slug}))
        else:
            messages.error(request, _("Match Team Player Not Add , Please Try Again"), extra_tags='Match Team Player')
    else:
        context = {'match': match,'team':team,'players':players,'match_players':match_team_players,
                   'players_form': AdminPlayersForm(),
                   'match_team_player_form': AdminMatchTeamPlayerForm(), 'current_page': _('Match Team Player')}
        return render(request, f'{BACKEND_TEMPLATES}/sport/match/details.html', context)


@authenticated_staf
@staff_only
def AdminMatchTeamEventAdd(request,slug,team_slug):
    match = Match.objects.get(slug=slug)
    team = Teams.objects.get(slug=team_slug)
    players = Players.objects.filter(owner_model=ContentType.objects.get(model='Teams'), owner_id=team.id)
    match_team_players = MatchTeamPlayer.objects.filter(match=match, team=team)
    if request.method == "POST":
        summary_form = AdminMatchSummaryForm(request.POST or None, request.FILES or None)
        match_team_player_form = AdminMatchTeamPlayerForm(request.POST or None, request.FILES or None)
        if match_team_player_form:
            event_player = request.POST.get('event_player')
            event_type = request.POST.get('event_type')
            event_half = request.POST.get('event_half')
            event_time = request.POST.get('event_time')



            player = Players.objects.get(id=event_player)
            match_summary_object = MatchSummary(
                match=match,team=team,player=player,type=event_type,half=event_half,time=event_time)
            match_summary_object.save()
            messages.success(request, _("Match Team Event Add Successfully"), extra_tags='Match Team Event')
            return HttpResponseRedirect(reverse_lazy('sport:AdminMatchDetailsByTeam',kwargs={'slug':slug,'team_slug':team_slug}))
        else:
            messages.error(request, _("Match Team Event Not Add , Please Try Again"), extra_tags='Match Team Event')
    else:
        context = {'match': match,'team':team,'players':players,'match_players':match_team_players,

                   'summary_form': AdminMatchSummaryForm(),
                   'match_team_player_form': AdminMatchTeamPlayerForm(), 'current_page': _('Match Team Event')}
        return render(request, f'{BACKEND_TEMPLATES}/sport/match/details.html', context)

