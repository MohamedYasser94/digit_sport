from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from apps.sport.forms.forms import *
from apps.sport.models.models import *
from core.models.core import CommonTranslate
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
            country = request.POST.get('country')
            keyword = request.POST.get('keyword')
            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')



            sport_object = Sport(name=name, country=country, keyword=keyword, image=image, image_path=image_path,
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
            sport = request.POST.get('sport')
            category = request.POST.get('category')
            sub_category = request.POST.get('sub_category')
            country = request.POST.get('country')
            short_code = request.POST.get('short_code')
            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')
            type = request.POST.get('type')
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

            leagues_object = Leagues.objects.get(slug=slug)
            leagues_object.name = name
            leagues_object.sport = sport
            leagues_object.category = category
            leagues_object.sub_category = sub_category
            leagues_object.country = country
            leagues_object.short_code = short_code
            leagues_object.image = image
            leagues_object.image_path = image_path
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
            is_current = request.POST.get('is_current')

            if is_current == None or is_current == '' or is_current == 'None' or is_current == 'No':
                is_current = False
            else:
                is_current = True



            if league == None or league == '':
                league = None
            else:
                league = Leagues.objects.get(id=league)

            season_object = Season(name=name, league=league, keyword=keyword, starting_at=starting_at,
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

            season_object = Season(name=name, league=league,sport=league.sport, keyword=keyword,is_current=is_current, starting_at=starting_at,
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

            round_object = Round(name=name, league=league, keyword=keyword, starting_at=starting_at,
                                        ending_at=ending_at, is_current=is_current,
                                        status='Active')

            round_object.save()
            messages.success(request, _("Round Add Successfully"), extra_tags='Round')

            return HttpResponseRedirect(reverse_lazy('sport:AdminRoundList'))
        else:

                messages.error(request, _("Round Not Add , Please Try Again"), extra_tags='Round')

    else:
        context = {'rounds': rounds, 'rounds_form': AdminRoundForm(), 'current_page': _('Rounds')

                   }
        return render(request, f'{BACKEND_TEMPLATES}/sport/round/admin.html', context)




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
            league = request.POST.get('league')
            country = request.POST.get('country')
            founded = request.POST.get('founded')
            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')

            if league == None or league == '':
                league = None
            else:
                league = Leagues.objects.get(id=league)

            clubs_object = Clubs(name=name, keyword=keyword, league=league, country=country,founded=founded, image=image,
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
        league = request.POST.get('league')
        country = request.POST.get('country')
        founded = request.POST.get('founded')
        image = request.FILES.get('image')
        image_path = request.POST.get('image_path')
        status = request.POST.get('status')

        if league == None or league == '':
            league = None
        else:
            league = Leagues.objects.get(id=league)

        clubs_object = Clubs.objects.get(slug=slug)
        clubs_object.name = name
        clubs_object.keyword = keyword
        clubs_object.league = league
        clubs_object.country = country
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
    teams = Teams.objects.all()

    if request.method == "POST":
        teams_form = AdminTeamsForm(request.POST or None, request.FILES or None)

        if teams_form:
            name = request.POST.get('name')
            short_code = request.POST.get('short_code')
            country = request.POST.get('country')
            club = request.POST.get('club')
            sport = request.POST.get('sport')
            venue = request.POST.get('venue')
            gender = request.POST.get('gender')
            keyword = request.POST.get('keyword')

            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')
            status = 'Active'

            try:
                check_teams = Teams.objects.get(name=name)
                messages.error(request, _("Teams Already Exist , Please Try Again"), extra_tags='Teams')
                return HttpResponseRedirect(reverse_lazy('sport:AdminTeamsList'))
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




            teams_object = Teams(  name=name,country=country,club=club,sport=sport,venue=venue,
                                   gender=gender,keyword=keyword,short_code=short_code,image=image,
                                      image_path=image_path,status='Active')

            teams_object.save()
            messages.success(request, _("Teams Add Successfully"), extra_tags='Teams')

            return HttpResponseRedirect(reverse_lazy('sport:AdminTeamsList'))
        else:

            messages.error(request, _("Teams Not Add , Please Try Again"), extra_tags='Teams')

    else:
        context = {'teams': teams, 'teams_form': AdminTeamsForm(), 'current_page': _('Teams')

                   }
        return render(request, f'{BACKEND_TEMPLATES}/sport/teams/admin.html', context)


@authenticated_staf
@staff_only
def AdminTeamsUpdate(request, slug):
    team = Teams.objects.get(slug=slug)

    if request.method == "POST":
        teams_form = AdminTeamsForm(request.POST or None, request.FILES or None, instance=team)
        if teams_form:
            name = request.POST.get('name')
            short_code = request.POST.get('short_code')
            country = request.POST.get('country')
            club = request.POST.get('club')
            sport = request.POST.get('sport')
            venue = request.POST.get('venue')
            gender = request.POST.get('gender')
            keyword = request.POST.get('keyword')

            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')
            status = 'Active'

            print(request.POST)

            try:
                check_teams = Teams.objects.get(name=name).exclude(slug=slug)
                messages.error(request, _("Teams Already Exist , Please Try Again"), extra_tags='Teams')
                return HttpResponseRedirect(reverse_lazy('sport:AdminTeamsList'))
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
            team_object.short_code = short_code
            team_object.country = country
            team_object.club = club
            team_object.sport = sport
            team_object.venue = venue
            team_object.gender = gender
            team_object.keyword = keyword

            team_object.image_path = image_path
            print(status)
            team_object.status = status
            if image == None or image == '':
                team_object.image = team.image
            else:
                team_object.image = image
            team_object.save()

            messages.success(request, _("Teams Update Successfully"), extra_tags='Teams')
            return HttpResponseRedirect(reverse_lazy('sport:AdminTeamsList'))
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

            print(request.POST)
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



##########################  Players ################################
@authenticated_staf
@staff_only
def AdminPlayersList(request):
    players = Players.objects.all()
    paginator = Paginator(players, 10)  # Show 25 contacts per page.

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if request.method == "POST":
        players_form = AdminPlayersForm(request.POST or None, request.FILES or None)
        if players_form:
            name = request.POST.get('name')
            short_code = request.POST.get('short_code')
            country = request.POST.get('country')
            sport = request.POST.get('sport')
            gender = request.POST.get('gender')
            nationality = request.POST.get('nationality')
            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')
            keyword = request.POST.get('keyword')

            if sport == None or sport == '':
                sport = None
            else:
                sport = Sport.objects.get(id=sport)

            player_object = Players(
                name=name,short_code=short_code,country=country,
                sport=sport,gender=gender,nationality=nationality,image=image,
                image_path=image_path,keyword=keyword
            )
            player_object.save()
            messages.success(request, _("Players Add Successfully"), extra_tags='Players')
            return HttpResponseRedirect(reverse_lazy('sport:AdminPlayersList'))
        else:
            messages.error(request, _("Players Not Add , Please Try Again"), extra_tags='Players')
    else:
        context = {'players': page_obj, 'players_form': AdminPlayersForm(), 'current_page': _('Players')}
        return render(request, f'{BACKEND_TEMPLATES}/sport/players/admin.html', context)


@authenticated_staf
@staff_only
def AdminPlayersUpdate(request, slug):
    player = Players.objects.get(slug=slug)

    if request.method == "POST":
        players_form = AdminPlayersForm(request.POST or None, request.FILES or None, instance=player)
        if players_form:
            name = request.POST.get('name')
            short_code = request.POST.get('short_code')
            country = request.POST.get('country')
            sport = request.POST.get('sport')
            gender = request.POST.get('gender')
            nationality = request.POST.get('nationality')
            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')
            keyword = request.POST.get('keyword')

            if sport == None or sport == '':
                sport = None
            else:
                sport = Sport.objects.get(id=sport)

            player_object = Players.objects.get(slug=slug)
            player_object.name = name
            player_object.short_code = short_code
            player_object.sport = sport
            player_object.country = country
            player_object.nationality =nationality
            if image == None or image == '':
                player_object.image = player.image
            else:
                player_object.image = image
            player_object.image_path = image_path
            player_object.gender = gender
            player_object.keyword = keyword
            player_object.save()

            messages.success(request, _("Players Update Successfully"), extra_tags='Players')
            return HttpResponseRedirect(reverse_lazy('sport:AdminPlayersList'))
        else:
            messages.error(request, _("Players Not Update , Please Try Again"), extra_tags='Players')
    else:
        messages.error(request, _("Players Not Update , Please Try Again"), extra_tags='Players')
    context = {'player': player, 'players_form': AdminPlayersForm(instance=player), 'current_page': _('Update'),
                'prev_Page': _('Players'), }
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


##########################  Match ################################
@authenticated_staf
@staff_only
def AdminMatchList(request):
    matches = Match.objects.all()

    if request.method == "POST":
        matches_form = AdminMatchForm(request.POST or None, request.FILES or None)
        if matches_form:
            home_team = request.POST.get('home_team')
            away_team = request.POST.get('away_team')
            venues = request.POST.get('venues')
            start_time = request.POST.get('start_time')
            home_team = Teams.objects.get(id=home_team)
            away_team = Teams.objects.get(id=away_team)
            is_live = request.POST.get('is_live')

            name = home_team.name + ' vs ' + away_team.name

            if venues == None or venues == '':
                venues = None
            else:

                venues = Venues.objects.get(id=venues)

            match_object = Match(name=name,
                home_team=home_team,away_team=away_team,venues=venues,start_time=start_time,
                is_live=is_live
            )
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
def AdminMatchBySeason(request, slug):
    season = Season.objects.get(slug=slug)
    matches = Match.objects.filter(season=season)
    teams = Teams.objects.filter(sport=season.sport.id,country=season.league.country)

    if request.method == "POST":
        matches_form = AdminMatchForm(request.POST or None, request.FILES or None)
        if matches_form:
            home_team = request.POST.get('home_team')
            away_team = request.POST.get('away_team')
            venues = request.POST.get('venues')
            start_time = request.POST.get('start_time')
            home_team = Teams.objects.get(id=home_team)
            away_team = Teams.objects.get(id=away_team)
            is_live = request.POST.get('is_live')



            if home_team == away_team:
                messages.error(request, _("Home Team and Away Team Can't Be Same"), extra_tags='Match')
                return HttpResponseRedirect(reverse_lazy('sport:AdminMatchBySeason', kwargs={'slug': slug}))

            name = home_team.name + ' vs ' + away_team.name
            if venues == None or venues == '':
                venues = None
            else:
                venues = Venues.objects.get(id=venues)

            match_object = Match(name=name, sport=season.sport, season=season,league=season.league,
                home_team=home_team,away_team=away_team,venues=venues,start_time=start_time,
                is_live=is_live
            )
            match_object.save()
            messages.success(request, _("Match Add Successfully"), extra_tags='Match')
            return HttpResponseRedirect(reverse_lazy('sport:AdminMatchBySeason', kwargs={'slug': slug}))
        else:
            messages.error(request, _("Match Not Add , Please Try Again"), extra_tags='Match')
    else:
        context = {'season':season,'matches': matches,'teams': teams, 'matches_form': AdminMatchForm(), 'current_page': _('Match')}
        return render(request, f'{BACKEND_TEMPLATES}/sport/season/match.html', context)


@authenticated_staf
@staff_only
def AdminMatchDetails(request, slug):
    match = Match.objects.get(slug=slug)
    summary = MatchSummary.objects.filter(match=match,)
    home_team = Teams.objects.get(id=match.home_team.id)
    away_team = Teams.objects.get(id=match.away_team.id)
    home_players = MatchTeamPlayer.objects.filter(match=match,team=home_team.id)
    away_players = MatchTeamPlayer.objects.filter(match=match, team=away_team.id)
    match_goal = MatchSummary.objects.filter(match=match)
    home_summary = MatchSummary.objects.filter(match=match,team=home_team)
    away_summary = MatchSummary.objects.filter(match=match, team=away_team)
    last_summary = MatchSummary.objects.filter(match=match).last()
    match_statics = MatchStatics.objects.filter(match=match)
    last_statics = MatchStatics.objects.filter(match=match).last()



    context = {
        'match':match,'summary':summary,'home_team':home_team,
        'away_team':away_team,'home_players':home_players,
        'away_players':away_players, 'match_goal':match_goal,
        'home_summary':home_summary,'away_summary':away_summary,
        'last_summary':last_summary,
        'summary_form': AdminMatchSummaryForm(),
        'static_form': AdminMatchStaticsForm(),
        'match_statics':match_statics,
        'last_statics':last_statics,
        'current_page': _('Details')}
    return render(request, f'{BACKEND_TEMPLATES}/sport/match/details.html', context)




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
            start_time = request.POST.get('start_time')

            if home_team == away_team:
                messages.error(request, _("Home Team and Away Team Can't Be Same"), extra_tags='Match')
                return HttpResponseRedirect(reverse_lazy('sport:AdminMatchUpdate', kwargs={'slug': slug}))

            home_team = Teams.objects.get(id=home_team)
            away_team = Teams.objects.get(id=away_team)

            match_object = Match.objects.get(slug=slug)
            match_object.home_team = home_team
            match_object.away_team = away_team
            match_object.location = location
            match_object.start_time = start_time
            match_object.save()

            messages.success(request, _("Match Update Successfully"), extra_tags='Match')
            return HttpResponseRedirect(reverse_lazy('sport:AdminMatchList'))
        else:
            messages.error(request, _("Match Not Update , Please Try Again"), extra_tags='Match')
    else:
        messages.error(request, _("Match Not Update , Please Try Again"), extra_tags='Match')
    context = {'match': match, 'matches_form': AdminMatchForm(instance=match), 'current_page': _('Update'),
                'prev_Page': _('Match'), }
    return render(request, f'{BACKEND_TEMPLATES}/sport/match/update.html', context)


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
    match = Match.objects.get(slug=slug)

    if request.method == "POST":
        match.delete()

        messages.success(request, _("Match Delete Successfully"), extra_tags='Match')

        return HttpResponseRedirect(reverse_lazy('sport:AdminMatchList'))
    else:
        return HttpResponseRedirect(reverse_lazy('sport:AdminMatchList'))


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

            try:
                match_goal = MatchGoals.objects.get(match=match)
            except:
                match_goal = MatchGoals(match=match,home_team = home_team,away_team=away_team,
                                        home_scorer=0,away_scorer=0)
                match_goal.save()

            player = Players.objects.get(slug=event_player)
            event_team = Teams.objects.get(id=player.owner_id)
            match_summary_object = MatchSummary(
                match=match,team=event_team,player=player,type=event_type,half=event_half,time=event_time)
            match_summary_object.save()
            if event_type == 'Goal':
                event_team = Teams.objects.get(id=player.owner_id)
                if event_team == home_team:
                    match_goal.home_scorer += 1
                    match_goal.save()
                else:
                    match_goal.away_scorer += 1
                    match_goal.save()
            match.score = str(match_goal.home_scorer) + ' - ' + str(match_goal.away_scorer)
            match.save()

            messages.success(request, _("Match Event Add Successfully"), extra_tags='Match')
            return HttpResponseRedirect(reverse_lazy('sport:AdminMatchDetails', kwargs={'slug': slug}))
        else:
            messages.error(request, _("Match Event Not Add , Please Try Again"), extra_tags='Match')
    else:
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

##########################  Match Result ################################


@authenticated_staf
@staff_only
def AdminMatchDetailsByTeam(request,slug,team_slug):
    match = Match.objects.get(slug=slug)
    team = Teams.objects.get(slug=team_slug)
    players = Players.objects.filter(owner_model=ContentType.objects.get(model='Teams'), owner_id=team.id)
    match_players = MatchTeamPlayer.objects.filter(match=match,team=team)
    match_summary = MatchSummary.objects.filter(match=match,team=team)


    context = {'match': match, 'team': team, 'players': players,
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














