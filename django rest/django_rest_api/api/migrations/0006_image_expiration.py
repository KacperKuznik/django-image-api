# Generated by Django 4.0.6 on 2023-02-26 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_image_image_alter_image_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='expiration',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
