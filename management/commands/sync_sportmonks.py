# sports/management/commands/sync_sportmonks.py
#
# This file contains the powerful, scheduled tasks for fetching data from the SportMonks API.
# To run these commands:
#   - python manage.py sync_leagues
#   - python manage.py sync_teams
#   - python manage.py sync_fixtures --days_past=7 --days_future=14
#
# To schedule these to run automatically, you would use a cron job.

import requests
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

from apps.sport.models import Sport
from apps.sport.models.monks import *


# --- IMPORTANT ---
# You should store your API token in your project's settings.py file, not here.
# settings.py
# SPORTMONKS_API_TOKEN = 'YOUR_API_TOKEN_HERE'
# SPORTMONKS_BASE_URL = 'https://api.sportmonks.com/v3/'

class Command(BaseCommand):
    help = "Base command for syncing data from the SportMonks API."

    def get_api_data(self, endpoint: str, params: dict = None) -> dict:
        """
        A helper function to make requests to the SportMonks API.
        """
        base_url = getattr(settings, 'SPORT_MONKS_URL', 'https://api.sportmonks.com/v3/')
        api_token = getattr(settings, 'SPORT_MONKS_TOKEN', None)

        if not api_token:
            self.stdout.write(self.style.ERROR("SPORTMONKS_API_TOKEN is not configured in settings.py"))
            return None

        full_url = f"{base_url}{endpoint}"

        default_params = {'api_token': api_token}
        if params:
            default_params.update(params)

        try:
            response = requests.get(full_url, params=default_params)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"API request failed for {endpoint}: {e}"))
            return None

    def handle(self, *args, **kwargs):
        self.stdout.write("This is a base command and should not be run directly.")


class SyncLeaguesCommand(Command):
    help = "Syncs all football leagues from SportMonks."

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting league synchronization...")

        # Ensure the 'Football' sport exists
        football_sport, created = Sport.objects.get_or_create(
            name='Football',
            defaults={'slug': 'football'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created 'Football' sport entry."))

        endpoint = "football/leagues"
        data = self.get_api_data(endpoint)

        if not data or 'data' not in data:
            self.stdout.write(self.style.ERROR("Failed to fetch leagues or no data returned."))
            return

        leagues_data = data['data']
        synced_count = 0
        for league_data in leagues_data:
            # Use update_or_create for safe and efficient data syncing.
            # This finds a league with the given source_api and source_id,
            # and either updates it or creates a new one.
            obj, created = League.objects.update_or_create(
                source_api='sportmonks',
                source_id=league_data['id'],
                defaults={
                    'sport': football_sport,
                    'name': league_data['name'],
                    'logo_url': league_data.get('image_path'),
                    # IMPORTANT: We do NOT update 'custom_translation_name' here,
                    # so any manual edits are preserved.
                }
            )
            synced_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully synced {synced_count} leagues."))


class SyncTeamsCommand(Command):
    help = "Syncs all teams for a given league from SportMonks."

    def add_arguments(self, parser):
        parser.add_argument('--league_id', type=int, help='The SportMonks ID of the league to sync teams for.')

    def handle(self, *args, **kwargs):
        league_id = kwargs.get('league_id')
        if not league_id:
            self.stdout.write(self.style.ERROR("Please provide a --league_id."))
            return

        self.stdout.write(f"Starting team synchronization for league ID {league_id}...")

        try:
            league_obj = League.objects.get(source_api='sportmonks', source_id=str(league_id))
        except League.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"League with source_id {league_id} not found in the database. Sync leagues first."))
            return

        # The endpoint to get teams for a specific season (more reliable than by league)
        # You might need to get the current season ID first.
        # For simplicity, this example assumes a direct teams endpoint exists or you adapt it.
        # Let's assume we get teams by league for this example.
        # A better approach is to get seasons for the league, then teams for each season.

        # This is a simplified example. A full implementation would first fetch the current season for the league.
        endpoint = f"football/teams/leagues/{league_id}"  # This endpoint might need adjustment based on API v3 structure
        data = self.get_api_data(endpoint)

        if not data or 'data' not in data:
            self.stdout.write(self.style.ERROR(f"Failed to fetch teams for league {league_id}."))
            return

        teams_data = data['data']
        synced_count = 0
        for team_data in teams_data:
            Team.objects.update_or_create(
                source_api='sportmonks',
                source_id=team_data['id'],
                defaults={
                    'sport': league_obj.sport,
                    'name': team_data['name'],
                    'logo_url': team_data.get('image_path'),
                }
            )
            synced_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully synced {synced_count} teams for league {league_obj.name}."))


class SyncFixturesCommand(Command):
    """
    This is the main command you will run 3x per day.
    It fetches matches for a given date range.
    """
    help = "Syncs fixtures for a given date range from SportMonks."

    def add_arguments(self, parser):
        parser.add_argument('--days_past', type=int, default=7, help='Number of days in the past to sync.')
        parser.add_argument('--days_future', type=int, default=7, help='Number of days in the future to sync.')

    def handle(self, *args, **kwargs):
        days_past = kwargs['days_past']
        days_future = kwargs['days_future']

        start_date = (timezone.now() - timedelta(days=days_past)).strftime('%Y-%m-%d')
        end_date = (timezone.now() + timedelta(days=days_future)).strftime('%Y-%m-%d')

        self.stdout.write(f"Starting fixture synchronization from {start_date} to {end_date}...")

        endpoint = f"football/fixtures/between/{start_date}/{end_date}"
        # Include participants (teams) and league to get all data in one call
        params = {'include': 'league;participants'}
        data = self.get_api_data(endpoint, params=params)

        if not data or 'data' not in data:
            self.stdout.write(self.style.ERROR("Failed to fetch fixtures."))
            return

        fixtures_data = data['data']
        synced_count = 0
        for fixture_data in fixtures_data:
            try:
                # Find the related objects in our database
                league_obj = League.objects.get(source_api='sportmonks', source_id=fixture_data['league_id'])

                # Sportmonks uses 'participants' for the two teams in a fixture
                home_team_data = next(p for p in fixture_data['participants'] if p['meta']['location'] == 'home')
                away_team_data = next(p for p in fixture_data['participants'] if p['meta']['location'] == 'away')

                home_team_obj = Team.objects.get(source_api='sportmonks', source_id=home_team_data['id'])
                away_team_obj = Team.objects.get(source_api='sportmonks', source_id=away_team_data['id'])

                # Extract scores from the 'scores' array if available
                home_score = next((s['score']['goals'] for s in fixture_data.get('scores', []) if
                                   s['description'] == 'CURRENT' and s['participant_id'] == home_team_obj.source_id),
                                  None)
                away_score = next((s['score']['goals'] for s in fixture_data.get('scores', []) if
                                   s['description'] == 'CURRENT' and s['participant_id'] == away_team_obj.source_id),
                                  None)

                # The 'state' object contains the match status
                status = fixture_data['state']['state']

                Match.objects.update_or_create(
                    source_api='sportmonks',
                    source_id=fixture_data['id'],
                    defaults={
                        'league': league_obj,
                        'home_team': home_team_obj,
                        'away_team': away_team_obj,
                        'match_time': datetime.fromisoformat(fixture_data['starting_at'].replace("Z", "+00:00")),
                        'status': status,
                        'home_score': home_score,
                        'away_score': away_score,
                        # Store extra data as JSON for flexibility
                        'events_data': fixture_data.get('events'),
                        'statistics_data': fixture_data.get('statistics'),
                    }
                )
                synced_count += 1
            except League.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f"Skipping fixture {fixture_data['id']}: League {fixture_data['league_id']} not found."))
            except Team.DoesNotExist as e:
                self.stdout.write(
                    self.style.WARNING(f"Skipping fixture {fixture_data['id']}: A team was not found. {e}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"An error occurred processing fixture {fixture_data['id']}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully synced {synced_count} fixtures."))

