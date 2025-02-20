import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from inventory_monitor.helpers import (
    TEMPLATE_SERVICES_CONTRACTS,
    TEMPLATE_SERVICES_END,
    NumberColumn,
)
from inventory_monitor.models import Asset


class AssetTable(NetBoxTable):
    serial = tables.Column(linkify=True)
    type = columns.TemplateColumn(
        template_code="""
        {% if record.type %}
            <a href="{{ record.type.get_absolute_url }}">
                {% if record.type.color %}
                    <span class="badge" style="background-color: #{{ record.type.color }}">
                        {{ record.type.name }}
                    </span>
                {% else %}
                    {{ record.type.name }}
                {% endif %}
            </a>
        {% endif %}
        """,
        verbose_name="Type",
        orderable=True,
    )
    assignment_status = columns.ChoiceFieldColumn()
    lifecycle_status = columns.ChoiceFieldColumn()
    device = tables.Column(linkify=True)
    inventory_item = tables.Column(linkify=True)
    site = tables.Column(linkify=True)
    location = tables.Column(linkify=True)
    order_contract = tables.Column(linkify=True)
    price = NumberColumn()
    tags = columns.TagColumn()
    services_to = columns.TemplateColumn(template_code=TEMPLATE_SERVICES_END)
    services_contracts = tables.TemplateColumn(
        template_code=TEMPLATE_SERVICES_CONTRACTS
    )

    warranty_status = tables.TemplateColumn(
        template_code="""
            {% include 'inventory_monitor/inc/status_badge.html' with status_type='warranty' %}
        """,
        verbose_name="Warranty Status",
        orderable=False,
    )

    class Meta(NetBoxTable.Meta):
        model = Asset
        fields = (
            "pk",
            "id",
            "serial",
            "serial_actual",
            "partnumber",
            "device",
            "asset_number",
            "project",
            "assignment_status",
            "lifecycle_status",
            "location",
            "site",
            "vendor",
            "quantity",
            "price",
            "order_contract",
            "inventory_item",
            "warranty_start",
            "warranty_end",
            "warranty_status",
            "comments",
            "actions",
            "tags",
            "services_count",
            "services_contracts",
            "services_to",
            "type",
        )

        default_columns = (
            "id",
            "serial",
            "serial_actual",
            "device",
            "assignment_status",
            "lifecycle_status",
            "asset_number",
            "site",
            "quantity",
            "price",
            "actions",
            "type",
        )
