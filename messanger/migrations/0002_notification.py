# Generated by Django 5.0.1 on 2024-06-02 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messanger', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=100)),
            ],
        ),
    ]
