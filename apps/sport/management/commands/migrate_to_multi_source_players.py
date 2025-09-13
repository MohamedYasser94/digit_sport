from django.core.management.base import BaseCommand
from django.db import transaction
from apps.sport.models import Players, MultiSourcePlayers, DataSource, Sport, Teams
from datetime import datetime


class Command(BaseCommand):
    help = 'Migrate existing Players to MultiSourcePlayers model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually doing it',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of players to migrate (for testing)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']

        self.stdout.write(
            self.style.SUCCESS(f'Starting migration {"(DRY RUN)" if dry_run else ""}')
        )

        # Initialize data sources
        self.init_data_sources(dry_run)

        # Get existing players
        players_queryset = Players.objects.all()
        if limit:
            players_queryset = players_queryset[:limit]

        total_players = players_queryset.count()
        self.stdout.write(f'Found {total_players} players to migrate')

        migrated = 0
        errors = 0

        for old_player in players_queryset:
            try:
                with transaction.atomic():
                    success = self.migrate_player(old_player, dry_run)
                    if success:
                        migrated += 1
                    else:
                        errors += 1
                        
                # Progress indicator
                if (migrated + errors) % 100 == 0:
                    self.stdout.write(f'Processed {migrated + errors}/{total_players} players...')
                    
            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(f'Error migrating player {old_player.id}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Migration completed {"(DRY RUN)" if dry_run else ""}. '
                f'Migrated: {migrated}, Errors: {errors}'
            )
        )

    def init_data_sources(self, dry_run):
        """Initialize data sources if they don't exist"""
        sources_data = [
            {
                'name': 'Sportmonks',
                'slug': 'sportmonks',
                'priority': 90,
                'description': 'Migrated from original Sportmonks data'
            },
            {
                'name': 'Legacy Data',
                'slug': 'legacy',
                'priority': 50,
                'description': 'Migrated from original Players model'
            }
        ]

        if not dry_run:
            for source_data in sources_data:
                DataSource.objects.get_or_create(
                    slug=source_data['slug'],
                    defaults=source_data
                )
        
        self.stdout.write('Data sources initialized')

    def migrate_player(self, old_player, dry_run):
        """Migrate a single player"""
        try:
            # Check if already migrated
            if MultiSourcePlayers.objects.filter(
                sportmonks_api_id=old_player.api_id
            ).exists():
                return True

            if dry_run:
                self.stdout.write(f'Would migrate: {old_player.name} (ID: {old_player.api_id})')
                return True

            # Determine primary data source
            if old_player.api_id:
                primary_source = DataSource.objects.get(slug='sportmonks')
            else:
                primary_source = DataSource.objects.get(slug='legacy')

            # Parse birthdate
            birthdate_obj = None
            if old_player.birthdate:
                try:
                    if isinstance(old_player.birthdate, str):
                        birthdate_obj = datetime.strptime(old_player.birthdate, '%Y-%m-%d').date()
                    else:
                        birthdate_obj = old_player.birthdate
                except (ValueError, TypeError):
                    pass

            # Create new MultiSourcePlayers instance
            new_player = MultiSourcePlayers(
                # API IDs
                sportmonks_api_id=old_player.api_id if old_player.api_id else None,
                
                # Basic info
                name=old_player.name,
                display_name=old_player.display_name,
                common_name=old_player.common_name,
                first_name=old_player.first_name,
                middle_name=old_player.middle_name,
                last_name=old_player.last_name,
                short_code=old_player.short_code,
                keyword=old_player.keyword,
                
                # Relations
                sport=old_player.sport,
                team=old_player.team,
                
                # Location
                country=old_player.country,
                nationality=old_player.nationality,
                city=old_player.city,
                api_country=old_player.api_country,
                api_nationality=old_player.api_nationality,
                api_city=old_player.api_city,
                birthplace=old_player.birthplace,
                
                # Position
                position=old_player.position,
                detailed_position=old_player.detailed_position,
                api_position=old_player.api_position,
                api_detailed_position=old_player.api_detailed_position,
                number=old_player.number,
                
                # Physical
                height=old_player.height,
                weight=old_player.weight,
                age=old_player.age,
                birthdate=birthdate_obj,
                date_of_birth=old_player.birthdate if isinstance(old_player.birthdate, str) else None,
                gender=old_player.gender,
                
                # Images
                image=old_player.image,
                image_path=old_player.image_path,
                country_image=old_player.country_image,
                url=old_player.url,
                
                # Career
                type=old_player.type,
                ratings=old_player.ratings,
                in_team=old_player.in_team,
                
                # Data source tracking
                primary_data_source=primary_source,
                
                # System
                status=old_player.status,
                create_at=old_player.creat_at,  # Note: old model has typo
                update_at=old_player.update_at
            )
            
            new_player.save()
            
            # Add leagues (many-to-many)
            if old_player.league.exists():
                new_player.league.set(old_player.league.all())
            
            # Create data source info
            from apps.sport.models import PlayerDataSourceInfo
            PlayerDataSourceInfo.objects.create(
                player=new_player,
                data_source=primary_source,
                is_primary=True,
                raw_data={
                    'migrated_from_player_id': old_player.id,
                    'migration_date': datetime.now().isoformat(),
                    'original_api_id': old_player.api_id
                }
            )
            
            return True
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error migrating player {old_player.id}: {str(e)}')
            )
            return False

    def get_migration_stats(self):
        """Get statistics about the migration"""
        total_old = Players.objects.count()
        total_new = MultiSourcePlayers.objects.count()
        
        sportmonks_source = DataSource.objects.filter(slug='sportmonks').first()
        legacy_source = DataSource.objects.filter(slug='legacy').first()
        
        sportmonks_count = MultiSourcePlayers.objects.filter(primary_data_source=sportmonks_source).count() if sportmonks_source else 0
        legacy_count = MultiSourcePlayers.objects.filter(primary_data_source=legacy_source).count() if legacy_source else 0
        
        return {
            'total_old_players': total_old,
            'total_new_players': total_new,
            'sportmonks_migrated': sportmonks_count,
            'legacy_migrated': legacy_count
        }
