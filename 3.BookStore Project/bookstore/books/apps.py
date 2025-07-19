from django.apps import AppConfig # type: ignore


class BooksConfig(AppConfig):
    name = 'books'

    def ready(self):
        import books.signals  # noqa
