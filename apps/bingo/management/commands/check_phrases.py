"""
Management command to check the state of Bingo phrases in the database.
Run with: python manage.py check_phrases
"""
from django.core.management.base import BaseCommand
from apps.bingo.models import BingoPhrase


class Command(BaseCommand):
    help = 'Check the state of Bingo phrases in the database'

    def handle(self, *args, **options):
        self.stdout.write('\n=== Bingo Phrases Diagnostic ===\n')

        # Count total phrases
        total_count = BingoPhrase.objects.count()
        self.stdout.write(f'Total phrases in database: {total_count}')

        if total_count == 0:
            self.stdout.write(self.style.ERROR(
                '\n❌ No phrases found in database!\n'
                'Please run: python manage.py load_budget_phrases'
            ))
            return

        # Count by difficulty
        classic_count = BingoPhrase.objects.filter(difficulty_level='classic').count()
        advanced_count = BingoPhrase.objects.filter(difficulty_level='advanced').count()
        technical_count = BingoPhrase.objects.filter(difficulty_level='technical').count()

        self.stdout.write(f'\nPhrases by difficulty:')
        self.stdout.write(f'  Classic: {classic_count}')
        self.stdout.write(f'  Advanced: {advanced_count}')
        self.stdout.write(f'  Technical: {technical_count}')

        # Check if any phrases have NULL or unexpected difficulty_level values
        unaccounted = total_count - (classic_count + advanced_count + technical_count)
        if unaccounted > 0:
            self.stdout.write(self.style.WARNING(
                f'\n⚠️  {unaccounted} phrases have unexpected difficulty_level values!'
            ))
            # Show the unexpected values
            all_difficulties = BingoPhrase.objects.values_list('difficulty_level', flat=True).distinct()
            self.stdout.write(f'  All difficulty values found: {list(all_difficulties)}')

        # Check if we have enough for each difficulty
        self.stdout.write('\nCard generation feasibility:')
        for diff, count in [('classic', classic_count), ('advanced', advanced_count), ('technical', technical_count)]:
            if count >= 25:
                self.stdout.write(self.style.SUCCESS(f'  ✓ {diff.capitalize()}: {count} phrases (sufficient)'))
            else:
                self.stdout.write(self.style.ERROR(f'  ✗ {diff.capitalize()}: {count} phrases (need at least 25)'))

        # Show sample phrases
        self.stdout.write('\nSample phrases from each difficulty:')
        for diff in ['classic', 'advanced', 'technical']:
            sample = BingoPhrase.objects.filter(difficulty_level=diff).first()
            if sample:
                self.stdout.write(f'  {diff.capitalize()}: "{sample.phrase_text}"')
            else:
                self.stdout.write(f'  {diff.capitalize()}: (none found)')

        self.stdout.write(self.style.SUCCESS('\n✓ Diagnostic complete\n'))
