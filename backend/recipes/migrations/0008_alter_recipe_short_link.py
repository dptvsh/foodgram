# Generated by Django 3.2 on 2025-03-15 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20250315_2217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='short_link',
            field=models.CharField(max_length=3, null=True, unique=True, verbose_name='Короткая ссылка на рецепт'),
        ),
    ]
