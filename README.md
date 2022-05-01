# Тестовый workflow @_github actions_
#### на примере проекта yamdb_final

![yamdb_final workflow](https://github.com/sammirabyan/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

#### Что входит в workflow:
- проверка кода на соответствие стандарту PEP8
- проверка кода на соответствие локальным тестам
- сборка и доставка докер-образа для контейнера web на Docker Hub
- автоматический деплой проекта на боевой сервер
- отправка уведомления в Telegram о том, что процесс деплоя успешно завершился

#### Требования
- наличие аккаунта в Docker Hub
- наличие токена для бота в Telegram

#### Установка
1. Сделайте форк этого репозитория.
2. В веб-интерфейсе _github_ перейдите во вкладку `Settings-> Secrets-> Actions` и добавьте следующие секретные ключи:
    ```
    (для работы с dockerhub)
    DOCKER_PASSWORD
    DOCKER_USERNAME

    (для удаленного покдлючения к серверу)
    HOST
    SSH_KEY
    USER

    (для работы с базой данных в контейнере)
    DB_ENGINE
    DB_HOST
    DB_NAME
    DB_PORT    
    POSTGRES_PASSWORD
    POSTGRES_USER
    
    (для отправки сообщений через телегам)
    TELEGRAM_TO
    TELEGRAM_TOKEN
    
    ```
3. Перенесите содержимое директории `infra/` в рабочую директорию вашего сервера.
4. Внесите изменения в любой из файлов проекта и сделайте пуш в ветку master.

#### Над проектом работали
[Sam Mirabyan](https://github.com/sammirabyan) по ТЗ __Yandex Practicum__