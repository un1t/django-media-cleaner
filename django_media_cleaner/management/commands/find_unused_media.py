import os
from django.core.management.base import BaseCommand
from django_media_cleaner.code import get_unused_media


class Command(BaseCommand):
    help = 'Search unused media files.'

    def add_arguments(self, parser):
        parser.add_argument('--delete', action='store_true')

    def handle(self, *args, **options):
        media = get_unused_media()

        if options['delete']:
            for path in media:
                self.stdout.write(path)
                os.unlink(path)
            self.stdout.write('Deleted: {}'.format(len(media)))
            return

        for path in media:
            self.stdout.write(path)
