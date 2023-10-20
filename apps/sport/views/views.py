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

            sport_object = Sport(title=title, category=category, keyword=keyword, image=image, image_url=image_url,
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
        status = request.POST.get('status')

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
                                     country=country, short_code=short_code, image=image, image_url=image_url,keyword=keyword )

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
        leagues_form = AdminLeaguesForm(request.POST or None, request.FILES or None, instance=league)
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


            if league == None or league == '':
                league = None
            else:
                league = Leagues.objects.get(id=league)

            season_object = Season(name=name, league=league, keyword=keyword, starting_at=starting_at,
                                        ending_at=ending_at, standings_recalculated_at=standings_recalculated_at,
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
            image_url = request.POST.get('image_url')

            if league == None or league == '':
                league = None
            else:
                league = Leagues.objects.get(id=league)

            clubs_object = Clubs(name=name, keyword=keyword, league=league, country=country,founded=founded, image=image,
                                    image_url=image_url, status='Active')

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
        image_url = request.POST.get('image_url')
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
        clubs_object.image_url = image_url
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
            image_url = request.POST.get('image_url')

            venues_object = Venues(name=name, keyword=keyword, country=country, city=city, short_code=short_code,
                                   image=image, image_url=image_url, status='Active')

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
        image_url = request.POST.get('image_url')
        status = request.POST.get('status')

        venues_object = Venues.objects.get(slug=slug)
        venues_object.name = name
        venues_object.keyword = keyword
        venues_object.country = country
        venues_object.city = city
        venues_object.short_code = short_code
        venues_object.image = image
        venues_object.image_url = image_url
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
            league = request.POST.get('league')
            club = request.POST.get('club')
            sport = request.POST.get('sport')
            venue = request.POST.get('venue')
            gender = request.POST.get('gender')
            keyword = request.POST.get('keyword')

            image = request.FILES.get('image')
            image_url = request.POST.get('image_url')
            status = request.POST.get('status')

            try:
                check_teams = Teams.objects.get(name=name)
                messages.error(request, _("Teams Already Exist , Please Try Again"), extra_tags='Teams')
                return HttpResponseRedirect(reverse_lazy('sport:AdminTeamsList'))
            except:
                pass

            if league == None or league == '':
                league = None
            else:
                league = Leagues.objects.get(id=league)

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




            teams_object = Teams(  name=name,league=league,club=club,sport=sport,venue=venue,
                                   gender=gender,keyword=keyword,short_code=short_code,image=image,
                                      image_url=image_url,status='Active')

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
            league = request.POST.get('league')
            club = request.POST.get('club')
            sport = request.POST.get('sport')
            venue = request.POST.get('venue')
            gender = request.POST.get('gender')
            keyword = request.POST.get('keyword')

            image = request.FILES.get('image')
            image_url = request.POST.get('image_url')
            status = request.POST.get('status')

            try:
                check_teams = Teams.objects.get(name=name)
                messages.error(request, _("Teams Already Exist , Please Try Again"), extra_tags='Teams')
                return HttpResponseRedirect(reverse_lazy('sport:AdminTeamsList'))
            except:
                pass

            if league == None or league == '':
                league = None
            else:
                league = Leagues.objects.get(id=league)

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
            team_object.league = league
            team_object.club = club
            team_object.sport = sport
            team_object.venue = venue
            team_object.gender = gender
            team_object.keyword = keyword
            if image == None or image == '':
                team_object.image = team.image
            else:
                team_object.image = image
            team_object.image_url = image_url
            team_object.status = status
            team_object.save()

            messages.success(request, _("Teams Update Successfully"), extra_tags='Teams')
            return HttpResponseRedirect(reverse_lazy('sport:AdminTeamsList'))
        else:
                messages.error(request, _("Teams Not Update , Please Try Again"), extra_tags='Teams')

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



##########################  Players ################################
@authenticated_staf
@staff_only
def AdminPlayersList(request):
    players = Players.objects.all()

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
            image_url = request.POST.get('image_url')
            keyword = request.POST.get('keyword')

            if sport == None or sport == '':
                sport = None
            else:
                sport = Sport.objects.get(id=sport)

            player_object = Players(
                name=name,short_code=short_code,country=country,
                sport=sport,gender=gender,nationality=nationality,image=image,
                image_url=image_url,keyword=keyword
            )
            player_object.save()
            messages.success(request, _("Players Add Successfully"), extra_tags='Players')
            return HttpResponseRedirect(reverse_lazy('sport:AdminPlayersList'))
        else:
            messages.error(request, _("Players Not Add , Please Try Again"), extra_tags='Players')
    else:
        context = {'players': players, 'players_form': AdminPlayersForm(), 'current_page': _('Players')}
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
            image_url = request.POST.get('image_url')
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
            player_object.image_url = image_url
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
            location = request.POST.get('location')
            start_time = request.POST.get('start_time')

            home_team = Teams.objects.get(id=home_team)
            away_team = Teams.objects.get(id=away_team)

            match_object = Match(
                home_team=home_team,away_team=away_team,location=location,start_time=start_time
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
def AdminMatchUpdate(request, slug):
    match = Match.objects.get(slug=slug)

    if request.method == "POST":
        matches_form = AdminMatchForm(request.POST or None, request.FILES or None, instance=match)
        if matches_form:
            home_team = request.POST.get('home_team')
            away_team = request.POST.get('away_team')
            location = request.POST.get('location')
            start_time = request.POST.get('start_time')

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










