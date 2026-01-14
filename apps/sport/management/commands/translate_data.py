from django.core.management.base import BaseCommand
from apps.sport.models import Leagues, Teams, Players, PlayerAchievement, PlayerAward
from deep_translator import GoogleTranslator
import time


class Command(BaseCommand):
    help = 'Translates name fields to Arabic only if name_tr is empty or matches the original name.'

    def handle(self, *args, **options):
        translator = GoogleTranslator(source='auto', target='ar')

        models_to_translate = [
            # (Leagues, 'Leagues'),
            (Teams, 'Teams'),
            (Players, 'Players'),
            (PlayerAchievement, 'PlayerAchievement'),
            (PlayerAward, 'PlayerAward'),
        ]

        for model, model_name in models_to_translate:
            self.stdout.write(self.style.WARNING(f'Starting translation for {model_name}...'))

            # Get all records that have a name
            objects = model.objects.exclude(name__isnull=True).exclude(name='')

            total = objects.count()
            self.stdout.write(f'Checking {total} records in {model_name}...')

            count = 0
            for obj in objects:
                # Logic: Translate ONLY if:
                # 1. name_tr is None (NULL)
                # 2. name_tr is an empty string ('')
                # 3. name_tr is exactly the same as name (not yet translated)
                should_translate = (
                        not obj.name_tr or
                        obj.name_tr.strip() == "" or
                        obj.name_tr == obj.name
                )

                if should_translate:
                    try:
                        translated = translator.translate(obj.name)
                        obj.name_tr = translated
                        obj.save()

                        count += 1
                        if count % 10 == 0:
                            self.stdout.write(f'Progress: {count} translated in {model_name}...')

                        # Small delay to prevent API rate limiting
                        time.sleep(0.1)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error translating {obj.name} ({obj.pk}): {str(e)}'))

            self.stdout.write(self.style.SUCCESS(f'Finished {model_name}. Updated {count} records.'))

        self.stdout.write(self.style.SUCCESS('All specific translations completed successfully.'))