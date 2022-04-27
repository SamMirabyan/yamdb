import csv

from django.core.management.base import BaseCommand
from django.apps import apps

from ._common import add_genres, MODELS, PATH


class Command(BaseCommand):
    help = 'Populate DB models with test data from csv files.'

    def populate_model(self, model_name, *args, **options):
        '''
        Populate given model with test data.
        '''
        model = apps.get_model('reviews', model_name.title())
        file_name = model_name + '.csv'
        with open(PATH + file_name) as file_object:
            csv_file = csv.reader(file_object, delimiter=',')
            headers = next(csv_file)
            for row in csv_file:
                payload = {key: value for key, value in zip(headers, row)}
                model.objects.get_or_create(**payload)

    def populate_db(self, *args, **kwargs):
        '''
        Populate all models with test data.
        '''
        for model_name in MODELS:
            success_message = 'Model {} populated with test data successfully!'
            error_message = 'An error occured while populating model {}!'
            try:
                self.populate_model(model_name)
                self.stdout.write(self.style.SUCCESS(
                    success_message.format(model_name.title()))
                )
            except Exception as e:
                self.stderr.write(self.style.ERROR(
                    error_message.format(model_name.title()))
                )
                print(e)

    def add_genres_to_titles(self, *args, **kwargs):
        success_message = 'Genres added to titles successfully!'
        error_message = 'An error occured while adding genres to titles!'
        try:
            add_genres()
            self.stdout.write(self.style.SUCCESS(success_message))
        except Exception as e:
            self.stderr.write(self.style.ERROR(error_message))
            print(e)

    def add_arguments(self, parser):
        parser.add_argument(
            '--with_genres',
            action='store_true',
            default=True,
            help='Populate models and add genres to titles'
        )
        parser.add_argument(
            '--no_genres',
            action='store_true',
            help='Populate models without adding genres to titles'
        )
        parser.add_argument(
            '--genres_only',
            action='store_true',
            help='Only add genres to titles. Without populating models.'
        )

    def handle(self, *args, **options):
        if options['no_genres']:
            self.populate_db()
            self.stdout.write(self.style.WARNING(
                'Models were populated without genres being added to titles!')
            )
        elif options['genres_only']:
            self.add_genres_to_titles()
            self.stdout.write(self.style.WARNING(
                'No model was populated!')
            )
        else:
            self.populate_db()
            self.add_genres_to_titles()
