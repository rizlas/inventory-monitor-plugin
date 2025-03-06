import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

# Helper imports for custom columns and templates
from inventory_monitor.helpers import (
    TEMPLATE_SERVICES_CONTRACTS,
    TEMPLATE_SERVICES_END,
    NumberColumn,
)
from inventory_monitor.models import Asset


class AssetTable(NetBoxTable):
    """
    Table configuration for displaying Asset objects in list views
    """

    #
    # Basic identification columns
    #
    name = tables.Column(linkify=True)
    serial = tables.Column(linkify=True)
    partnumber = tables.Column()
    asset_number = tables.Column()

    #
    # Type and classification columns
    #
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

    #
    # Status columns
    #
    assignment_status = columns.ChoiceFieldColumn()
    lifecycle_status = columns.ChoiceFieldColumn()

    # Formatted column for warranty status using a template
    warranty_status = tables.TemplateColumn(
        template_code="""
            {% include 'inventory_monitor/inc/status_badge.html' with status_type='warranty' %}
        """,
        verbose_name="Warranty Status",
        orderable=False,
    )

    #
    # Assignment columns
    #
    assigned_object = tables.Column(
        verbose_name="Assigned Object", orderable=False, linkify=True
    )

    #
    # Related object columns
    #
    inventory_item = tables.Column(linkify=True)
    order_contract = tables.Column(linkify=True)

    #
    # Additional information columns
    #
    project = tables.Column()
    vendor = tables.Column()
    quantity = tables.Column()
    price = NumberColumn()  # Custom column for proper price formatting

    #
    # Service information columns
    #
    services_to = columns.TemplateColumn(
        template_code=TEMPLATE_SERVICES_END, verbose_name="Service End"
    )
    services_contracts = tables.TemplateColumn(
        template_code=TEMPLATE_SERVICES_CONTRACTS, verbose_name="Service Contracts"
    )

    #
    # Warranty information columns
    #
    warranty_start = tables.Column()
    warranty_end = tables.Column()

    #
    # Metadata columns
    #
    tags = columns.TagColumn()
    comments = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = Asset

        # Define all available fields that can be displayed in the table
        fields = (
            # Key identifiers
            "pk",
            "id",
            # Basic identification
            "name",
            "serial",
            "partnumber",
            "asset_number",
            # Type and classification
            "type",
            # Status
            "assignment_status",
            "lifecycle_status",
            # Assignment
            "assigned_object",
            # Additional information
            "project",
            "vendor",
            "quantity",
            "price",
            # Related objects
            "order_contract",
            "inventory_item",
            # Warranty information
            "warranty_start",
            "warranty_end",
            "warranty_status",
            # Service information
            "services_count",
            "services_contracts",
            "services_to",
            # Metadata
            "comments",
            "tags",
            "actions",
        )

        # Define the default columns that are shown when the table first loads
        default_columns = (
            "id",
            "name",
            "serial",
            "type",
            "assigned_object",
            "assignment_status",
            "lifecycle_status",
            "asset_number",
            "quantity",
            "price",
            "actions",
        )
