# Generated by Django 4.0.5 on 2022-07-15 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0002_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='recipeingredients',
            name='unique_recipe_ingredient',
        ),
        migrations.RenameField(
            model_name='recipeingredients',
            old_name='ingredient',
            new_name='ingredients',
        ),
        migrations.AddConstraint(
            model_name='recipeingredients',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredients'), name='unique_recipe_ingredients'),
        ),
    ]
