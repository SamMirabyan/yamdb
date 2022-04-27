import csv
from django.conf import settings

from ...models import Genre, Title

PATH = settings.STATIC_ROOT + '/fixtures/'
MODELS = ['user', 'genre', 'category', 'title', 'review', 'comment']


def add_genres():
    '''
    Add genres to titles.
    '''
    file_name = 'genre_title.csv'
    with open(PATH + file_name) as file_object:
        csv_file = csv.reader(file_object, delimiter=',')
        _ = next(csv_file)
        for row in csv_file:
            title = Title.objects.get(id=int(row[1]))
            genre = Genre.objects.get(id=int(row[2]))
            title.genre.add(genre)
