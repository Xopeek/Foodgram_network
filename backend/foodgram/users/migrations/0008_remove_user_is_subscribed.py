# Generated by Django 3.2 on 2023-07-31 19:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_user_is_subscribed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_subscribed',
        ),
    ]
