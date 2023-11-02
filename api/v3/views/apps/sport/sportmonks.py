import requests
from django.http import JsonResponse

from api.v3.serializers.sport.sport import *
from apps.sport.models.models import *
from digit_sport import settings

api_key = settings.SPORT_MONKS_TOKEN
base_url = settings.SPORT_MONKS_URL



def get_sportmonks_data(request, country, sport):
    """Gets data from the SportMonks API."""

    print('api_key',api_key)

    url = f'https://api.sportmonks.com/v3/football/teams?api_token={api_key}'
    # https: // api.sportmonks.com / v3 / football / fixtures / 18535517?api_token = YOUR_TOKEN & include = events

    # Make the API request.
    response = requests.get(
        url,
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": f"Bearer {api_key}",
        },
    )

    # Check if the request was successful.
    if response.status_code == 200:
        # Decode the JSON response.
        data = response.json()

        # Return the data as a JSON response.
        return JsonResponse(data)
    else:
        # Return an error response.
        return JsonResponse({"error": "Failed to get data from SportMonks API."})


kuwait_id = 21462

def SportWithMonkTeamsByCountryApiList(request, country,sport):
    print()
    if country == '' or country == None or country == 'all' or country == ':country':
        country = 'Kuwait'
    else:
        country = country
    if sport == '' or sport == None or sport == 'all' or sport == ':sport':
        sport = 'Volleyball'
    sport_list = Sport.objects.filter(name=sport, country=country)

    if sport_list.count() > 0:
        get_sport = Sport.objects.get(name=sport, country=country)
        teams_list = Teams.objects.filter(sport=get_sport.id, country=country)
        success = True
        message = f"Send From Django API mix {country}"
        sport_serializer = SportSerializer(sport_list, many=True)
        team_serializer = TeamsSerializer(teams_list, many=True)
        sport_data = {'country': country,
                      'sport': sport_serializer.data,
                        'team': team_serializer.data,
                      }
    else:
        success = False
        message = f"error in get data no data no data with this country {country} or sport {sport}"

        sport_data = {'country': country,
                      'sport': [],
                        'team': [],
                      }

    data = {'success': success, 'data': sport_data, 'message': message,

            }
    return JsonResponse(data, safe=False)