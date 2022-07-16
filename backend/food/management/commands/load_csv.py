import csv

from django.core.management.base import BaseCommand

from food.models import Ingredients


class Command(BaseCommand):
    help = 'Loading ingredients into the base'

    def handle(self, *args, **kwargs):
        ingredient_count = Ingredients.objects.count()
        reader = csv.DictReader(
            open('./data/ingredients.csv'),
            fieldnames=[
                'name',
                'measurement_unit'
            ]
        )
        Ingredients.objects.bulk_create(
            [Ingredients(**data) for data in reader]
        )
        if Ingredients.objects.count() > ingredient_count:
            self.stdout.write(self.style.SUCCESS('Loading is complete!'))
        else:
            self.stdout.write(self.style.ERROR('Loading is error!'))
