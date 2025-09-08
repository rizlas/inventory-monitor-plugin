# Generated manually for renaming field and related names

from django.db import migrations, models


class Migration(migrations.Migration):
    
    dependencies = [
        ('inventory_monitor', '0042_rename_abra_to_external_inventory'),
    ]

    operations = [
        # Step 1: Rename the field abra_id to external_id
        migrations.RenameField(
            model_name='externalinventory',
            old_name='abra_id',
            new_name='external_id',
        ),
        
        # Step 2: Update the related_name for the ManyToMany field
        migrations.AlterField(
            model_name='externalinventory',
            name='assets',
            field=models.ManyToManyField(
                blank=True,
                help_text='Associated internal asset records',
                related_name='external_inventory_items',
                to='inventory_monitor.asset',
                verbose_name='Assets'
            ),
        ),
    ]
