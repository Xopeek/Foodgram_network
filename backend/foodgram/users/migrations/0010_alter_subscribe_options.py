# Generated by Django 3.2 on 2023-08-06 18:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20230731_2235'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscribe',
            options={'ordering': ('-author_id',), 'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
    ]