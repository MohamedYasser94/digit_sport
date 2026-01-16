"""
Django management command to test PDF extraction.

Usage:
    python manage.py test_pdf_upload <pdf_path>
    python manage.py test_pdf_upload <pdf_path> --match=<match_slug> --apply
"""

from django.core.management.base import BaseCommand, CommandError
from apps.sport.utils.pdf_parser import parse_match_report
from apps.sport.models.models import Match, Players
from apps.sport.models.operations import MatchPlayerReport, PlayerStatics
import re
import os


class Command(BaseCommand):
    help = 'Test PDF extraction and optionally save to database'

    def add_arguments(self, parser):
        parser.add_argument('pdf_path', type=str, help='Path to PDF file')
        parser.add_argument('--match', type=str, help='Match slug to apply statistics to')
        parser.add_argument('--apply', action='store_true', help='Actually save to database')
        parser.add_argument('--verbose', action='store_true', help='Show detailed output')

    def handle(self, *args, **options):
        pdf_path = options['pdf_path']
        match_slug = options.get('match')
        apply_changes = options.get('apply', False)
        verbose = options.get('verbose', False)

        # Validate file
        if not os.path.exists(pdf_path):
            raise CommandError(f'PDF file not found: {pdf_path}')

        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('PDF Extraction Test'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))

        # Parse PDF
        self.stdout.write('📄 Parsing PDF...')
        parsed_stats = parse_match_report(pdf_path)

        if not parsed_stats:
            raise CommandError('No statistics found in PDF')

        self.stdout.write(self.style.SUCCESS(f'✅ Found {len(parsed_stats)} players\n'))

        # Display extracted data
        self.stdout.write(self.style.SUCCESS('Extracted Data:'))
        self.stdout.write('-' * 70)

        for idx, stat in enumerate(parsed_stats, 1):
            self.stdout.write(f'\n[{idx}] #{stat["player_number"]} - {stat["player_name"]}')
            if verbose:
                for key, value in stat.items():
                    if key not in ['player_name', 'player_number']:
                        self.stdout.write(f'    {key}: {value}')

        # Database matching
        self.stdout.write('\n' + '='*70)
        self.stdout.write('Database Matching:')
        self.stdout.write('-' * 70 + '\n')

        matched_count = 0
        unmatched = []

        for stat in parsed_stats:
            player = Players.objects.filter(
                name__icontains=stat['player_name']
            ).first()

            if player:
                matched_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'✅ {stat["player_name"]} → {player.name} (ID: {player.id})'
                ))
            else:
                unmatched.append(stat)
                self.stdout.write(self.style.WARNING(
                    f'⚠️  {stat["player_name"]} - NOT FOUND'
                ))

        # Summary
        self.stdout.write('\n' + '='*70)
        self.stdout.write('Summary:')
        self.stdout.write('-' * 70)
        self.stdout.write(f'Total in PDF: {len(parsed_stats)}')
        self.stdout.write(self.style.SUCCESS(f'Matched: {matched_count}'))
        self.stdout.write(self.style.WARNING(f'Unmatched: {len(unmatched)}'))

        if unmatched:
            self.stdout.write('\nUnmatched players:')
            for p in unmatched:
                self.stdout.write(f'  • {p["player_number"]} - {p["player_name"]}')

        # Apply if requested
        if apply_changes and match_slug:
            try:
                match = Match.objects.get(slug=match_slug)
            except Match.DoesNotExist:
                raise CommandError(f'Match not found: {match_slug}')

            self.stdout.write('\n' + '='*70)
            self.stdout.write('Saving to Database:')
            self.stdout.write('-' * 70 + '\n')

            updated_count = 0
            error_count = 0

            def clean_num(val):
                if not val:
                    return 0
                cleaned = re.sub(r'[^\d]', '', str(val))
                return int(cleaned) if cleaned else 0

            for stat in parsed_stats:
                try:
                    player = Players.objects.filter(
                        name__icontains=stat['player_name']
                    ).first()

                    if not player:
                        self.stdout.write(self.style.WARNING(
                            f'⏭️  Skipping (not found): {stat["player_name"]}'
                        ))
                        continue

                    # Create defaults dict
                    defaults = {
                        'point_total': str(clean_num(stat.get('pts', 0))),
                        'serve_total': str(clean_num(stat.get('serve_total', 0))),
                        'serve_err': str(clean_num(stat.get('serve_err', 0))),
                        'serve_ace': str(clean_num(stat.get('serve_ace', 0))),
                        'reception_total': str(clean_num(stat.get('reception_total', 0))),
                        'reception_err': str(clean_num(stat.get('reception_err', 0))),
                        'reception_exc': str(clean_num(stat.get('reception_exc', 0))),
                        'attack_total': str(clean_num(stat.get('attack_total', 0))),
                        'attack_err': str(clean_num(stat.get('attack_err', 0))),
                        'attack_att': str(clean_num(stat.get('attack_att', 0))),
                        'attack_pts': str(clean_num(stat.get('attack_pts', 0))),
                        'block_pts': str(clean_num(stat.get('block_pts', 0))),
                        'static_type': 'General'
                    }

                    # Save to MatchPlayerReport
                    MatchPlayerReport.objects.update_or_create(
                        player=player,
                        match=match,
                        defaults=defaults
                    )

                    # Save to PlayerStatics
                    PlayerStatics.objects.update_or_create(
                        player=player,
                        defaults=defaults
                    )

                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'✅ Saved: {player.name}'
                    ))

                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(
                        f'❌ Error saving {stat["player_name"]}: {e}'
                    ))

            self.stdout.write('\n' + '='*70)
            self.stdout.write(self.style.SUCCESS(f'Successfully saved {updated_count} records'))
            if error_count:
                self.stdout.write(self.style.WARNING(f'Errors: {error_count}'))

        else:
            if not apply_changes:
                self.stdout.write(self.style.WARNING(
                    '\n⚠️  DRY RUN: Use --apply flag to save to database'
                ))
            if not match_slug:
                self.stdout.write(self.style.WARNING(
                    '⚠️  Use --match=<slug> to specify which match to update'
                ))

        self.stdout.write('\n' + '='*70 + '\n')

