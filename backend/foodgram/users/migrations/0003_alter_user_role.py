# Generated by Django 3.2 on 2023-06-24 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_last_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('user', 'Пользователь'), ('admin', 'Администратор')], default='user', max_length=10, verbose_name='Роль'),
        ),
    ]
