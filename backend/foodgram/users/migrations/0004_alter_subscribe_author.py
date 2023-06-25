# Generated by Django 3.2 on 2023-06-25 09:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscribe',
            name='author',
            field=models.ForeignKey(help_text='Автор рецепта', on_delete=django.db.models.deletion.CASCADE, related_name='author', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
    ]
