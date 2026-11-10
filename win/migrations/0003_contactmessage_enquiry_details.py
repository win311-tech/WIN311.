from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('win', '0002_contactmessage_name_email_ip_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactmessage',
            name='organisation',
            field=models.CharField(blank=True, max_length=180),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='division',
            field=models.CharField(default='general', max_length=40),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='category',
            field=models.CharField(blank=True, max_length=80),
        ),
    ]
