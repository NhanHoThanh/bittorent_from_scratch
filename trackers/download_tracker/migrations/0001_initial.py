# Generated by Django 5.1.2 on 2024-10-31 15:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('file_id', models.AutoField(primary_key=True, serialize=False)),
                ('hash_code', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Peer',
            fields=[
                ('peer_id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('ip_address', models.GenericIPAddressField()),
                ('port', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('last_seen', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tracker',
            fields=[
                ('tracker_id', models.AutoField(primary_key=True, serialize=False)),
                ('ip_address', models.GenericIPAddressField()),
                ('port', models.IntegerField()),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], max_length=10)),
                ('last_sync', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='PeerAuth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('session_id', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], max_length=10)),
                ('login_time', models.DateTimeField(blank=True, null=True)),
                ('logout_time', models.DateTimeField(blank=True, null=True)),
                ('peer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='download_tracker.peer')),
            ],
        ),
        migrations.CreateModel(
            name='PeerFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('peer_type', models.CharField(choices=[('leecher', 'seeder')], max_length=10)),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='download_tracker.file')),
                ('peer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='download_tracker.peer')),
            ],
        ),
    ]