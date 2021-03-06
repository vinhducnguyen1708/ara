# Generated by Django 2.2.7 on 2019-11-08 16:06

from django.db import migrations, models


def move_to_duration(apps, schema_editor):
    # We can't import the model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    duration_models = ['Playbook', 'Play', 'Task', 'Result']
    for duration_model in duration_models:
        model = apps.get_model('api', duration_model)
        for obj in model.objects.all():
            if obj.duration is not None:
                continue
            if obj.ended is not None:
                obj.duration = obj.ended - obj.started
            else:
                obj.duration = obj.updated - obj.started
            obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_add_missing_result_properties'),
    ]

    operations = [
        migrations.AddField(
            model_name='play',
            name='duration',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='playbook',
            name='duration',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='result',
            name='duration',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='duration',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.RunPython(move_to_duration)
    ]
