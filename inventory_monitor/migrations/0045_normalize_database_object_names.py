# Generated migration to normalize database object names
# This migration renames old inconsistent names to match the clean squashed migration naming

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("inventory_monitor", "0044_remove_externalinventory_abra_id_idx_and_more"),
    ]

    operations = [
        # Rename sequences to match squashed migration naming
        migrations.RunSQL(
            "ALTER SEQUENCE inventory_monitor_component_id_seq RENAME TO inventory_monitor_asset_id_seq;",
            reverse_sql="ALTER SEQUENCE inventory_monitor_asset_id_seq RENAME TO inventory_monitor_component_id_seq;",
        ),
        migrations.RunSQL(
            "ALTER SEQUENCE inventory_monitor_abra_id_seq RENAME TO inventory_monitor_externalinventory_id_seq;",
            reverse_sql="ALTER SEQUENCE inventory_monitor_externalinventory_id_seq RENAME TO inventory_monitor_abra_id_seq;",
        ),
        migrations.RunSQL(
            "ALTER SEQUENCE inventory_monitor_abra_assets_id_seq RENAME TO inventory_monitor_externalinventory_assets_id_seq;",
            reverse_sql="ALTER SEQUENCE inventory_monitor_externalinventory_assets_id_seq RENAME TO inventory_monitor_abra_assets_id_seq;",
        ),
        # Rename constraints to match squashed migration naming
        migrations.RunSQL(
            "ALTER TABLE inventory_monitor_asset RENAME CONSTRAINT inventory_monitor_component_quantity_102892f6_check TO inventory_monitor_asset_quantity_check;",
            reverse_sql="ALTER TABLE inventory_monitor_asset RENAME CONSTRAINT inventory_monitor_asset_quantity_check TO inventory_monitor_component_quantity_102892f6_check;",
        ),
        # Rename indexes to match squashed migration naming
        migrations.RunSQL(
            "ALTER INDEX inventory_monitor_component_order_contract_id_74facfff RENAME TO inventory_monitor_asset_order_contract_id_a1244099;",
            reverse_sql="ALTER INDEX inventory_monitor_asset_order_contract_id_a1244099 RENAME TO inventory_monitor_component_order_contract_id_74facfff;",
        ),
        migrations.RunSQL(
            "ALTER INDEX inventory_monitor_componentservice_component_id_d6a32a90 RENAME TO inventory_monitor_assetservice_asset_id_1f531300;",
            reverse_sql="ALTER INDEX inventory_monitor_assetservice_asset_id_1f531300 RENAME TO inventory_monitor_componentservice_component_id_d6a32a90;",
        ),
        migrations.RunSQL(
            "ALTER INDEX inventory_monitor_componentservice_contract_id_844ccf4f RENAME TO inventory_monitor_assetservice_contract_id_c386bd16;",
            reverse_sql="ALTER INDEX inventory_monitor_assetservice_contract_id_c386bd16 RENAME TO inventory_monitor_componentservice_contract_id_844ccf4f;",
        ),
        migrations.RunSQL(
            "ALTER INDEX inventory_monitor_abra_assets_abra_id_c8294a93 RENAME TO inventory_monitor_external_externalinventory_id_c25af39d;",
            reverse_sql="ALTER INDEX inventory_monitor_external_externalinventory_id_c25af39d RENAME TO inventory_monitor_abra_assets_abra_id_c8294a93;",
        ),
        migrations.RunSQL(
            "ALTER INDEX inventory_monitor_abra_assets_asset_id_40c94ae5 RENAME TO inventory_monitor_externalinventory_assets_asset_id_30512e44;",
            reverse_sql="ALTER INDEX inventory_monitor_externalinventory_assets_asset_id_30512e44 RENAME TO inventory_monitor_abra_assets_asset_id_40c94ae5;",
        ),
        migrations.RunSQL(
            "ALTER INDEX inventory_monitor_abra_abra_id_ec838c69_like RENAME TO inventory_monitor_externalinventory_external_id_447627ff_like;",
            reverse_sql="ALTER INDEX inventory_monitor_externalinventory_external_id_447627ff_like RENAME TO inventory_monitor_abra_abra_id_ec838c69_like;",
        ),
    ]
