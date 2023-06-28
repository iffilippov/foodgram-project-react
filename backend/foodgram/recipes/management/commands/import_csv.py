import csv

from django.conf import settings
from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Скрипт импорта мок-данных из файла .csv в БД.
    Запуск производится командой python manage.py import_csv
    Заполнить базу можно только один раз.
    Для повторного запуска необходимо удалить файлы БД.
    """
    def handle(self, *args, **kwargs):
        model = Ingredient
        with open(
            f'{settings.BASE_DIR}/static/data/ingredients.csv',
            newline='',
            encoding='utf-8'
        ) as csv_file:
            reader = csv.reader(csv_file)
            count = 0
            for row in reader:
                name, unit = row
                model.objects.get_or_create(name=name,
                                            measurement_unit=unit)
                count += 1
                print(f'Обработано: {count} записей.')

        self.stdout.write(self.style.SUCCESS('Данные загружены'))
