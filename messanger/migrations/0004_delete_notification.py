# Generated by Django 5.0.1 on 2024-06-02 18:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messanger', '0003_notification_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Notification',
        ),
    ]
