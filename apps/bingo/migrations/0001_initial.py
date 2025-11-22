# Generated migration for bingo app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BingoPhrase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phrase_text', models.CharField(max_length=200)),
                ('category', models.CharField(blank=True, max_length=50)),
                ('difficulty_level', models.CharField(choices=[('classic', 'Classic'), ('advanced', 'Advanced'), ('technical', 'Technical')], max_length=20)),
                ('description', models.TextField(blank=True, help_text='Explanation of why this is a myth')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Bingo Phrase',
                'verbose_name_plural': 'Bingo Phrases',
                'db_table': 'bingo_phrases',
                'indexes': [
                    models.Index(fields=['difficulty_level'], name='bingo_phrases_difficulty_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='BingoCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('difficulty', models.CharField(choices=[('classic', 'Classic'), ('advanced', 'Advanced'), ('technical', 'Technical')], max_length=20)),
                ('completed', models.BooleanField(default=False)),
                ('completion_time', models.DateTimeField(blank=True, null=True)),
                ('generated_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bingo_cards', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Bingo Card',
                'verbose_name_plural': 'Bingo Cards',
                'db_table': 'bingo_cards',
                'ordering': ['-generated_at'],
                'indexes': [
                    models.Index(fields=['user'], name='bingo_cards_user_idx'),
                    models.Index(fields=['completed'], name='bingo_cards_completed_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='BingoSquare',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField(help_text='Position 0-24 in 5x5 grid')),
                ('marked', models.BooleanField(default=False)),
                ('marked_at', models.DateTimeField(blank=True, null=True)),
                ('auto_detected', models.BooleanField(default=False)),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='squares', to='bingo.bingocard')),
                ('phrase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bingo.bingophrase')),
            ],
            options={
                'verbose_name': 'Bingo Square',
                'verbose_name_plural': 'Bingo Squares',
                'db_table': 'bingo_squares',
                'ordering': ['position'],
                'indexes': [
                    models.Index(fields=['card'], name='bingo_squares_card_idx'),
                    models.Index(fields=['marked'], name='bingo_squares_marked_idx'),
                ],
            },
        ),
        migrations.AlterUniqueTogether(
            name='bingosquare',
            unique_together={('card', 'position')},
        ),
    ]
