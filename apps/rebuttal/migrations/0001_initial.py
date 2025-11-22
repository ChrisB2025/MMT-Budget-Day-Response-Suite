# Generated migration for rebuttal app

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Rebuttal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('version', models.CharField(default='1.0', max_length=10)),
                ('published', models.BooleanField(default=False)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Rebuttal',
                'verbose_name_plural': 'Rebuttals',
                'db_table': 'rebuttals',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['version'], name='rebuttals_version_idx'),
                    models.Index(fields=['published'], name='rebuttals_published_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='RebuttalSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('section_order', models.IntegerField()),
                ('rebuttal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='rebuttal.rebuttal')),
            ],
            options={
                'verbose_name': 'Rebuttal Section',
                'verbose_name_plural': 'Rebuttal Sections',
                'db_table': 'rebuttal_sections',
                'ordering': ['section_order'],
            },
        ),
    ]
