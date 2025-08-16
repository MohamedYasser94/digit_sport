from datetime import datetime
from datetime import timezone as dt_timezone

import pytz
import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponse
# It's better to get these from settings
from django.utils import timezone as django_timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from ..models import Teams, Sport, Leagues, Players, FixtureParticipant, Fixtures, Season, Venues
from ..models.monks import MonkCountry

# Assuming your models, forms, and settings are correctly imported
api_key = settings.SPORT_MONKS_TOKEN
base_url = settings.SPORT_MONKS_URL

def AdminMonksCountryList(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "GET":
        countries = MonkCountry.objects.all()
        data = [{'id': country.id, 'name': country.name} for country in countries]
        return JsonResponse(data, safe=False)

    return JsonResponse({'type': 'Error', 'message': 'Invalid request method.'})
# NOTE: This is the reference function. All other API functions now follow this pattern.
@csrf_exempt
def AdminMonksLeaguesGetData(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "POST":
        next_page_url = base_url + f'football/leagues?api_token={api_key}&include=country;currentSeason'
        processed, added, updated = 0, 0, 0

        while next_page_url:
            try:
                response = requests.get(next_page_url)
                if response.status_code == 200:
                    data = response.json()
                    data_to_db = data.get('data', [])

                    for item in data_to_db:
                        last_played_aware = None
                        if item.get('last_played_at'):
                            try:
                                naive_dt = datetime.strptime(item['last_played_at'], '%Y-%m-%d %H:%M:%S')
                                last_played_aware = pytz.utc.localize(naive_dt)
                            except (ValueError, TypeError):
                                pass

                        country_info = item.get('country')
                        currentseason_info = item.get('currentseason')

                        defaults = {
                            'name': item.get('name'),
                            'name_tr': item.get('name'),
                            'sport': Sport.objects.get(name='football'),
                            'short_code': item.get('short_code'),
                            'api_country': item.get('country_id'),
                            'image_path': item.get('image_path'),
                            'api_active': item.get('active', False),
                            'type': item.get('type'),
                            'sub_type': item.get('sub_type'),
                            'api_category': item.get('category'),
                            'last_played_at': last_played_aware,
                            'has_jerseys': item.get('has_jerseys', False),
                            'country': country_info.get('name') if country_info else None,
                            'country_image': country_info.get('image_path') if country_info else None,
                            'currentseason': currentseason_info.get('id') if currentseason_info else None,
                            'keyword': item,
                        }

                        obj, created = Leagues.objects.update_or_create(api_id=item['id'], defaults=defaults)
                        processed += 1
                        if created:
                            added += 1
                        else:
                            updated += 1

                    pagination = data.get('pagination', {})
                    if pagination.get('has_more') and pagination.get('next_page'):
                        next_page_url = f"{pagination.get('next_page')}&api_token={api_key}"
                    else:
                        next_page_url = None
                else:
                    error_message = f'API request failed with status code {response.status_code} on page {next_page_url}'
                    return JsonResponse({'type': 'Error', 'message': error_message})

            except Exception as e:
                return JsonResponse({'type': 'Error', 'message': f'An error occurred: {str(e)}'})

        success_message = f'Data fetched successfully. Processed: {processed}, Added: {added}, Updated: {updated}.'
        return JsonResponse({'type': 'Success', 'message': success_message})

    return JsonResponse({'type': 'Error', 'message': 'Invalid request method.'})


@csrf_exempt
def AdminMonksCountryGetData(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "POST":
        next_page_url = base_url + f'core/countries?api_token={api_key}'
        processed, added, updated = 0, 0, 0

        while next_page_url:
            try:
                response = requests.get(next_page_url)
                if response.status_code == 200:
                    data = response.json()
                    data_to_db = data.get('data', [])

                    for item in data_to_db:
                        defaults = {
                            'name': item.get('name'),
                            'official_name': item.get('official_name'),
                            'fifa_name': item.get('fifa_name'),
                            'iso2': item.get('iso2'),
                            'iso3': item.get('iso3'),
                            'latitude': item.get('latitude'),
                            'longitude': item.get('longitude'),
                            'image_path': item.get('image_path'),
                            'borders': item.get('borders'),
                        }
                        obj, created = MonkCountry.objects.update_or_create(api_id=item['id'], defaults=defaults)
                        processed += 1
                        if created:
                            added += 1
                        else:
                            updated += 1

                    pagination = data.get('pagination', {})
                    if pagination.get('has_more') and pagination.get('next_page'):
                        next_page_url = f"{pagination.get('next_page')}&api_token={api_key}"
                    else:
                        next_page_url = None
                else:
                    return JsonResponse({'type': 'Error', 'message': f'API request failed: {response.status_code}'})
            except Exception as e:
                return JsonResponse({'type': 'Error', 'message': f'An error occurred: {str(e)}'})

        success_message = f'Data fetched successfully. Processed: {processed}, Added: {added}, Updated: {updated}.'
        return JsonResponse({'type': 'Success', 'message': success_message})

    return JsonResponse({'type': 'Error', 'message': 'Invalid request method.'})


@csrf_exempt
def AdminMonksTeamsGetData(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "POST":
        sport = request.POST.get('sport', 'football')  # Default to football if not provided
        next_page_url = base_url + f'{sport}/teams?api_token={api_key}&include=country'
        processed, added, updated = 0, 0, 0

        while next_page_url:
            try:
                response = requests.get(next_page_url)
                if response.status_code == 200:
                    data = response.json()
                    data_to_db = data.get('data', [])
                    sport_id = Sport.objects.get(name=sport)

                    for item in data_to_db:
                        last_played_aware = None
                        if item.get('last_played_at'):
                            try:
                                naive_dt = datetime.strptime(item['last_played_at'], '%Y-%m-%d %H:%M:%S')
                                last_played_aware = pytz.utc.localize(naive_dt)
                            except (ValueError, TypeError):
                                pass

                        country_info = item.get('country')

                        defaults = {
                            'name': item.get('name'),
                            'name_tr': item.get('name'),
                            'short_code': item.get('short_code'),
                            'api_country': item.get('country_id'),
                            'api_venue': item.get('venue_id'),
                            'sport': sport_id,
                            'gender': item.get('gender'),
                            'image_path': item.get('image_path'),
                            'founded': item.get('founded'),
                            'type': item.get('type'),
                            'placeholder': item.get('placeholder'),
                            'last_played_at': last_played_aware,
                            'country': country_info.get('name') if country_info else None,
                            'country_image': country_info.get('image_path') if country_info else None,
                            'keyword': item
                        }

                        obj, created = Teams.objects.update_or_create(api_id=item['id'], defaults=defaults)
                        processed += 1
                        if created:
                            added += 1
                        else:
                            updated += 1

                    pagination = data.get('pagination', {})
                    if pagination.get('has_more') and pagination.get('next_page'):
                        next_page_url = f"{pagination.get('next_page')}&api_token={api_key}"
                    else:
                        next_page_url = None
                else:
                    return JsonResponse({'type': 'Error', 'message': f'API request failed: {response.status_code}'})
            except Exception as e:
                return JsonResponse({'type': 'Error', 'message': f'An error occurred: {str(e)}'})

        success_message = f'Data fetched successfully. Processed: {processed}, Added: {added}, Updated: {updated}.'
        return JsonResponse({'type': 'Success', 'message': success_message})

    return JsonResponse({'type': 'Error', 'message': 'Invalid request method.'})

# Add other refactored functions (Seasons, Stages, Rounds, etc.) here following the same pattern...
# For brevity, only the most requested functions are fully written out.
# The pattern is identical for the remaining functions.


@csrf_exempt
def AdminMonksPlayersGetData(request):
    """
    Handles fetching players from the Sportmonks API with automatic pagination.
    """
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "POST":
        sport = request.POST.get('sport', 'football')
        processed, added, updated = 0, 0, 0

        try:
            sport_id = Sport.objects.get(name=sport)
        except Sport.DoesNotExist:
            return JsonResponse({'type': 'Error', 'message': f"Sport '{sport}' not found."})

        next_page_url = base_url + f'{sport}/players?api_token={api_key}'

        while next_page_url:
            try:
                response = requests.get(next_page_url)
                if response.status_code == 200:
                    data = response.json()
                    data_to_db = data.get('data', [])

                    for player_data in data_to_db:
                        birthdate_obj = None
                        if player_data.get('date_of_birth'):
                            try:
                                # Parse date string into a date object
                                birthdate_obj = datetime.strptime(player_data['date_of_birth'], '%Y-%m-%d').date()
                            except (ValueError, TypeError):
                                birthdate_obj = None

                        defaults = {
                            'sport': sport_id,
                            'api_country': player_data.get('country_id'),
                            'api_nationality': player_data.get('nationality_id'),
                            'api_city': player_data.get('city_id'),
                            'api_position': player_data.get('position_id'),
                            'api_detailed_position': player_data.get('detailed_position_id'),
                            'type': player_data.get('type_id'),
                            'common_name': player_data.get('common_name'),
                            'first_name': player_data.get('firstname'),
                            'last_name': player_data.get('lastname'),
                            'name': player_data.get('display_name'), # Use display_name as primary name
                            'image_path': player_data.get('image_path'),
                            'height': player_data.get('height'),
                            'weight': player_data.get('weight'),
                            'birthdate': birthdate_obj,
                            'gender': player_data.get('gender'),
                        }

                        obj, created = Players.objects.update_or_create(
                            api_id=player_data['id'],
                            defaults=defaults
                        )
                        processed += 1
                        if created: added += 1
                        else: updated += 1

                    pagination = data.get('pagination', {})
                    if pagination.get('has_more') and pagination.get('next_page'):
                        next_page_url = f"{pagination.get('next_page')}&api_token={api_key}"
                    else:
                        next_page_url = None
                else:
                    return JsonResponse({'type': 'Error', 'message': f'API request failed: {response.status_code}'})
            except Exception as e:
                return JsonResponse({'type': 'Error', 'message': f'An error occurred: {str(e)}'})

        success_message = f'Data fetched successfully. Processed: {processed}, Added: {added}, Updated: {updated}.'
        return JsonResponse({'type': 'Success', 'message': success_message})

    return JsonResponse({'type': 'Error', 'message': 'Invalid request method.'})


# In your monks.py file

@csrf_exempt
def AdminMonksFixturesGetData(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "POST":
        sport = 'football'
        fetch_date = request.POST.get('fetch_date')
        if not fetch_date:
            return JsonResponse({'type': 'Error', 'message': 'Date is required.'})

        processed, added, updated = 0, 0, 0

        # Define all the data points you want to include from the API
        includes = "league;season;coaches;venue;state;lineups;events;timeline;trends;statistics;participants;metadata;formations;sidelined"
        next_page_url = base_url + f'{sport}/fixtures/date/{fetch_date}?api_token={api_key}&include={includes}'

        while next_page_url:
            try:
                response = requests.get(next_page_url)
                if response.status_code == 200:
                    data = response.json()
                    data_to_db = data.get('data', [])

                    for fixture_data in data_to_db:
                        # Convert starting_at to timezone-aware datetime
                        starting_at_aware = None
                        if fixture_data.get('starting_at'):
                            try:
                                naive_dt = datetime.fromisoformat(fixture_data['starting_at'].replace('Z', '+00:00'))
                                starting_at_aware = naive_dt
                            except (ValueError, TypeError):
                                pass

                        # Get related objects or None if they don't exist
                        league = Leagues.objects.filter(api_id=fixture_data.get('league_id')).first()
                        season =Season.objects.filter(api_id=fixture_data.get('season_id')).first()
                        venue = Venues.objects.filter(api_id=fixture_data.get('venue_id')).first()
                        sport_obj = Sport.objects.get(name=sport)

                        defaults = {
                            'sport': sport_obj,
                            'league': league,
                            'season': season,
                            'venue': venue,
                            'name': fixture_data.get('name'),
                            'starting_at': starting_at_aware,
                            'result_info': fixture_data.get('result_info'),
                            'leg': fixture_data.get('leg'),
                            'details': fixture_data.get('details'),
                            'length': fixture_data.get('length'),
                            'placeholder': fixture_data.get('placeholder', False),
                            'statistics': fixture_data.get('statistics'),
                            'events': fixture_data.get('events'),
                            'lineups': fixture_data.get('lineups'),
                        }

                        fixture_obj, created = Fixtures.objects.update_or_create(
                            api_id=fixture_data['id'],
                            defaults=defaults
                        )

                        # Process and save participants (teams)
                        fixture_obj.participants.all().delete()  # Clear old participants
                        for participant_data in fixture_data.get('participants', []):
                            team = Teams.objects.filter(api_id=participant_data.get('id')).first()
                            if team:
                                FixtureParticipant.objects.create(
                                    fixture=fixture_obj,
                                    team=team,
                                    api_id=participant_data.get('id'),
                                    meta_location=participant_data.get('meta', {}).get('location')
                                )

                        processed += 1
                        if created:
                            added += 1
                        else:
                            updated += 1

                    pagination = data.get('pagination', {})
                    if pagination.get('has_more') and pagination.get('next_page'):
                        next_page_url = f"{pagination.get('next_page')}&api_token={api_key}"
                    else:
                        next_page_url = None
                else:
                    return JsonResponse({'type': 'Error', 'message': f'API request failed: {response.status_code}'})
            except Exception as e:
                return JsonResponse({'type': 'Error', 'message': f'An error occurred: {str(e)}'})

        success_message = f'Fixtures for {fetch_date} fetched. Processed: {processed}, Added: {added}, Updated: {updated}.'
        return JsonResponse({'type': 'Success', 'message': success_message})

    return JsonResponse({'type': 'Error', 'message': 'Invalid request method.'})


def _fetch_and_store_fixtures_from_source(sport: str, fetch_date_str: str):
    """
    Fetches fixtures and intelligently fetches any missing related data.
    FIXED: Now correctly handles timezone conversion.
    """
    includes = "league;season;participants;state"
    next_page_url = base_url + f'{sport}/fixtures/date/{fetch_date_str}?api_token={api_key}&include={includes}'

    try:
        sport_obj = Sport.objects.get(name__iexact=sport)
    except Sport.DoesNotExist:
        print(f"Sport '{sport}' not found in DB.")
        return False

    while next_page_url:
        try:
            response = requests.get(next_page_url)
            if response.status_code != 200:
                print(f"Sportmonks API request failed: {response.status_code}")
                return False

            data = response.json()
            data_to_db = data.get('data', [])

            for fixture_data in data_to_db:
                league_id = fixture_data.get('league_id')
                league = Leagues.objects.filter(api_id=league_id).first()
                if not league:
                    league = _fetch_and_store_single_league(league_id)
                    if not league: continue

                season_data = fixture_data.get('season')
                if not season_data: continue

                season_defaults = {'name': season_data.get('name'), 'league': league,
                                   'is_current': season_data.get('is_current', False),
                                   'starting_at': season_data.get('starting_at'),
                                   'ending_at': season_data.get('ending_at')}
                season, _ = Season.objects.update_or_create(api_id=season_data['id'], defaults=season_defaults)

                api_defaults = {'league': league, 'season': season, 'name': fixture_data.get('name'),
                                'leg': fixture_data.get('leg'), 'result_info': fixture_data.get('result_info'),
                                'state': fixture_data.get('state', {}).get('state')}

                # <<< FIX: Correctly parse and make datetime timezone-aware >>>
                dt_str = fixture_data.get('starting_at')
                if dt_str:
                    try:
                        # Parse the string into a naive datetime object first
                        naive_dt = datetime.fromisoformat(dt_str.replace('Z', ''))
                        # Make it timezone-aware, assuming the API provides UTC time
                        aware_dt = django_timezone.make_aware(naive_dt, dt_timezone.utc)
                        api_defaults['starting_at'] = aware_dt
                    except (ValueError, TypeError):
                        pass

                fixture_obj, _ = Fixtures.objects.update_or_create(api_id=fixture_data['id'], defaults=api_defaults)

                fixture_obj.participants.all().delete()
                for participant_data in fixture_data.get('participants', []):
                    team_id = participant_data.get('id')
                    team = Teams.objects.filter(api_id=team_id).first()
                    if not team:
                        team = _fetch_and_store_single_team(team_id, sport_obj)

                    if team:
                        FixtureParticipant.objects.create(fixture=fixture_obj, team=team, api_id=team_id,
                                                          meta_location=participant_data.get('meta', {}).get(
                                                              'location'))

            pagination = data.get('pagination', {})
            next_page_url = f"{pagination.get('next_page')}&api_token={api_key}" if pagination.get('has_more') else None

        except Exception as e:
            print(f"An error occurred during fixture processing: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    return True


def _fetch_and_store_single_league(league_api_id):
    """Fetches a single league by its ID from the API and stores it in the DB."""
    if not league_api_id:
        return None

    print(f"Fetching missing league with ID: {league_api_id}...")
    url = base_url + f'football/leagues/{league_api_id}?api_token={api_key}&include=country'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            item = response.json().get('data', {})
            if not item:
                return None

            country_info = item.get('country')
            defaults = {
                'name': item.get('name'),
                'sport': Sport.objects.get(name='football'),
                'image_path': item.get('image_path'),
                'country': country_info.get('name') if country_info else None,
            }
            league_obj, created = Leagues.objects.update_or_create(
                api_id=item['id'],
                defaults=defaults
            )
            if created:
                print(f"SUCCESS: Stored new league '{league_obj.name}'.")
            return league_obj
        return None
    except Exception as e:
        print(f"ERROR fetching single league {league_api_id}: {e}")
        return None


# <<< NEW HELPER FUNCTION 2 >>>
def _fetch_and_store_single_team(team_api_id, sport_obj):
    """Fetches a single team by its ID from the API and stores it in the DB."""
    if not team_api_id:
        return None

    print(f"Fetching missing team with ID: {team_api_id}...")
    url = base_url + f'{sport_obj.name.lower()}/teams/{team_api_id}?api_token={api_key}&include=country'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            item = response.json().get('data', {})
            if not item:
                return None

            country_info = item.get('country')
            defaults = {
                'name': item.get('name'),
                'sport': sport_obj,
                'short_code': item.get('short_code'),
                'image_path': item.get('image_path'),
                'country': country_info.get('name') if country_info else None,
            }
            team_obj, created = Teams.objects.update_or_create(
                api_id=item['id'],
                defaults=defaults
            )
            if created:
                print(f"SUCCESS: Stored new team '{team_obj.name}'.")
            return team_obj
        return None
    except Exception as e:
        print(f"ERROR fetching single team {team_api_id}: {e}")
        return None