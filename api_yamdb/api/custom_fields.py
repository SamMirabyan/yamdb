from rest_framework.fields import CurrentUserDefault


class CurrentTitleDefault(CurrentUserDefault):
    '''
    Класс для получения id текущего тайтла.
    '''
    def __call__(self, serializer_field):
        return serializer_field.context['view'].kwargs['title_id']
