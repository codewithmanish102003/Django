from django.db.models.signals import (post_delete, post_save,  # type: ignore
                                      pre_delete, pre_save)
from django.dispatch import receiver  # type: ignore

from .models import Book


@receiver(post_save, sender=Book)
def book_created_handler(sender, instance, created, **kwargs):
    if created:
        print(f'New book added: {instance.title}')
    else:
        print(f'Book updated: {instance.title}')

@receiver(post_delete, sender=Book)
def book_deleted_handler(sender, instance, **kwargs):
    print(f'Book deleted: {instance.title}')

@receiver(pre_save, sender=Book)
def before_book_save_handler(sender, instance, **kwargs):
    print(f'About to save book: {instance.title}')

@receiver(pre_delete, sender=Book)
def before_book_delete_handler(sender, instance, **kwargs):
    print(f'About to delete book: {instance.title}')
