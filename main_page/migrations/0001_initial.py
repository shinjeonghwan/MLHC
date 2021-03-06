# Generated by Django 3.2.3 on 2021-05-20 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AD_LIST',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ad_url', models.CharField(max_length=300)),
                ('ad_name', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('main_key_word', models.CharField(max_length=100)),
                ('tag1', models.CharField(max_length=100)),
                ('tag2', models.CharField(max_length=100)),
                ('tag3', models.CharField(max_length=100)),
                ('weight', models.FloatField(default=0)),
                ('call_count', models.IntegerField(default=0)),
                ('feedback_value', models.IntegerField(default=0)),
                ('pub_date', models.DateTimeField(verbose_name='date published')),
            ],
        ),
    ]
