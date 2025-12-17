"""
Migration utility to merge MultiSourcePlayers data into Players model
Run this once to migrate existing data
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.sport.models import Players, Sport
from apps.sport.models.multi_source_players import MultiSourcePlayers
from django.utils import timezone


class Command(BaseCommand):
    help = 'Migrate MultiSourcePlayers data to main Players model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually doing it',
        )
        parser.add_argument(
            '--sport',
            type=str,
            help='Only migrate players from specific sport (e.g., football)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        sport_filter = options.get('sport')

        self.stdout.write(self.style.WARNING(
            'Starting migration from MultiSourcePlayers to Players'
        ))

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be saved'))

        # Get all multi-source players
        multi_players = MultiSourcePlayers.objects.all()

        if sport_filter:
            sport = Sport.objects.filter(name__iexact=sport_filter).first()
            if sport:
                multi_players = multi_players.filter(sport=sport)
                self.stdout.write(f'Filtering for sport: {sport.name}')

        total = multi_players.count()
        self.stdout.write(f'Found {total} players to migrate')

        stats = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0,
        }

        for multi_player in multi_players:
            try:
                self.migrate_player(multi_player, dry_run, stats)
            except Exception as e:
                stats['errors'] += 1
                self.stdout.write(self.style.ERROR(
                    f'Error migrating {multi_player.name}: {str(e)}'
                ))

        # Print summary
        self.stdout.write(self.style.SUCCESS('\n=== Migration Summary ==='))
        self.stdout.write(f'Total processed: {total}')
        self.stdout.write(self.style.SUCCESS(f'Created: {stats["created"]}'))
        self.stdout.write(self.style.WARNING(f'Updated: {stats["updated"]}'))
        self.stdout.write(f'Skipped: {stats["skipped"]}')
        if stats['errors'] > 0:
            self.stdout.write(self.style.ERROR(f'Errors: {stats["errors"]}'))

        if dry_run:
            self.stdout.write(self.style.WARNING(
                '\nThis was a DRY RUN. Run without --dry-run to apply changes.'
            ))

    def migrate_player(self, multi_player, dry_run, stats):
        """Migrate a single MultiSourcePlayers instance to Players"""

        # Try to find existing player by sportmonks_api_id
        existing_player = None

        if multi_player.sportmonks_api_id:
            existing_player = Players.objects.filter(
                api_id=multi_player.sportmonks_api_id
            ).first()

        # If not found, try by transfermarkt_id
        if not existing_player and multi_player.transfermarkt_id:
            existing_player = Players.objects.filter(
                transfermarkt_id=multi_player.transfermarkt_id
            ).first()

        # If not found, try by name and team
        if not existing_player and multi_player.name and multi_player.team:
            existing_player = Players.objects.filter(
                name=multi_player.name,
                team=multi_player.team
            ).first()

        if existing_player:
            # Update existing player with MultiSource data
            action = 'updated'
            player = existing_player
            self.stdout.write(f'Updating existing player: {player.name}')
        else:
            # Create new player
            action = 'created'
            player = Players()
            self.stdout.write(self.style.SUCCESS(f'Creating new player: {multi_player.name}'))

        # Copy fields from MultiSourcePlayers to Players
        # Core fields
        if multi_player.sportmonks_api_id:
            player.api_id = multi_player.sportmonks_api_id

        player.team = multi_player.team
        player.sport = multi_player.sport

        # Name fields - preserve name_tr if it exists in Players
        if not player.name_tr and multi_player.name:
            # Don't overwrite existing name_tr
            pass

        player.common_name = multi_player.common_name or player.common_name
        player.first_name = multi_player.first_name or player.first_name
        player.middle_name = multi_player.middle_name or player.middle_name
        player.last_name = multi_player.last_name or player.last_name
        player.name = multi_player.name or player.name
        player.display_name = multi_player.display_name or player.display_name
        player.short_code = multi_player.short_code or player.short_code
        player.keyword = multi_player.keyword or player.keyword

        # Location fields
        player.country = multi_player.country or player.country
        player.api_country = multi_player.api_country or player.api_country
        player.api_nationality = multi_player.api_nationality or player.api_nationality
        player.nationality = multi_player.nationality or player.nationality
        player.citizenship = multi_player.citizenship or player.citizenship
        player.city = multi_player.city or player.city
        player.api_city = multi_player.api_city or player.api_city
        player.birthplace = multi_player.birthplace or player.birthplace
        player.place_of_birth_city = multi_player.place_of_birth_city or player.place_of_birth_city
        player.place_of_birth_country = multi_player.place_of_birth_country or player.place_of_birth_country

        # Position fields
        player.position = multi_player.position or player.position
        player.number = multi_player.number or player.number
        player.api_position = multi_player.api_position or player.api_position
        player.detailed_position = multi_player.detailed_position or player.detailed_position
        player.api_detailed_position = multi_player.api_detailed_position or player.api_detailed_position
        player.foot = multi_player.foot or player.foot

        # Physical attributes
        player.height = multi_player.height or player.height
        player.age = multi_player.age or player.age
        player.weight = multi_player.weight or player.weight

        # Handle birthdate - MultiSourcePlayers has DateField, Players has CharField
        if multi_player.birthdate:
            player.birthdate = str(multi_player.birthdate)

        player.gender = multi_player.gender or player.gender

        # Images
        if multi_player.image:
            player.image = multi_player.image
        player.image_path = multi_player.image_path or player.image_path
        player.image_url = multi_player.image_url or player.image_url
        player.url = multi_player.url or player.url

        # TransferMarket fields
        player.transfermarkt_id = multi_player.transfermarkt_id or player.transfermarkt_id
        player.current_market_value = multi_player.current_market_value or player.current_market_value
        player.highest_market_value = multi_player.highest_market_value or player.highest_market_value
        player.market_value_currency = multi_player.market_value_currency or player.market_value_currency
        player.market_value_numeric = multi_player.market_value_numeric or player.market_value_numeric
        player.market_value_last_updated = multi_player.market_value_last_updated or player.market_value_last_updated

        # Contract info
        player.joined = multi_player.joined or player.joined
        player.contract_expires = multi_player.contract_expires or player.contract_expires

        # Agent info
        player.player_agent_name = multi_player.player_agent_name or player.player_agent_name
        player.outfitter = multi_player.outfitter or player.outfitter

        # Career info
        player.type = multi_player.type or player.type
        player.ratings = multi_player.ratings or player.ratings
        player.in_team = multi_player.in_team or player.in_team

        # System fields
        player.status = multi_player.status or player.status
        player.code = multi_player.code or player.code

        if not dry_run:
            player.save()

            # Copy many-to-many relationships
            if multi_player.league.exists():
                player.league.set(multi_player.league.all())

        stats[action] += 1

