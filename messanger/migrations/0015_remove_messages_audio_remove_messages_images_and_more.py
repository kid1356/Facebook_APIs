# Generated by Django 5.0.1 on 2024-09-12 14:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messanger', '0014_remove_messages_vedio_messages_video'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='messages',
            name='audio',
        ),
        migrations.RemoveField(
            model_name='messages',
            name='images',
        ),
        migrations.RemoveField(
            model_name='messages',
            name='video',
        ),
    ]
