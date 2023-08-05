# Generated by Django 3.2 on 2023-08-02 17:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_alter_ingredientrecipe_ingredient'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='tag',
            new_name='tags',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='description',
            new_name='text',
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.ingredient', verbose_name='Ингредиент'),
        ),
    ]