# Generated by Django 5.0.4 on 2024-12-16 22:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fileImageData', '0007_parentinvoice_alter_collectedproduct_invoice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectedproduct',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fileImageData.parentinvoice'),
        ),
    ]
