# Тестирование @_github actions_
#### на примере проекта yamdb_final

![yamdb_final workflow](https://github.com/sammirabyan/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

#### Что входит в процесс:
- проверка кода на соответствие стандарту PEP8
- проверка кода на соответствие локальным тестам
- сборка и доставка докер-образа для контейнера web на Docker Hub
- автоматический деплой проекта на боевой сервер
- отправка уведомления в Telegram о том, что процесс деплоя успешно завершился

#### Требования
- наличие аккаунта в Docker Hub
- наличие токена для бота в Telegram

