# Generated by Django 3.2 on 2023-08-01 16:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_favorite_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'verbose_name': 'Избранное', 'verbose_name_plural': 'Избранное'},
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'verbose_name': 'Корзина', 'verbose_name_plural': 'Корзина'},
        ),
        migrations.RemoveConstraint(
            model_name='favorite',
            name='unique_favorite',
        ),
        migrations.RemoveConstraint(
            model_name='shoppingcart',
            name='unique_shop_cart',
        ),
    ]
