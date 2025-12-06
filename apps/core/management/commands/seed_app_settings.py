"""
Management command to create or update default AppSettings.
"""

from django.core.management.base import BaseCommand

from apps.core.models import AppSettings


class Command(BaseCommand):
    help = 'Create or update default AppSettings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--app-name',
            type=str,
            default='Altea',
            help='Application name'
        )
        parser.add_argument(
            '--hero-text',
            type=str,
            default='Break the Bad Habits',
            help='Hero tagline'
        )
        parser.add_argument(
            '--contact-email',
            type=str,
            default='support@altea.ch',
            help='Contact email'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Update existing settings with provided values'
        )

    def handle(self, *args, **options):
        settings, created = AppSettings.objects.get_or_create(pk=1)

        if created or options['force']:
            settings.app_name = options['app_name']
            settings.hero_text = options['hero_text']
            settings.contact_email = options['contact_email']
            settings.save()

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created AppSettings: {settings.app_name}')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Updated AppSettings: {settings.app_name}')
                )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'AppSettings already exists: {settings.app_name}. '
                    'Use --force to update.'
                )
            )
