from netbox.plugins import PluginMenu, PluginMenuItem

menu = PluginMenu(
    label="Inventory Monitor",
    icon_class="mdi mdi-monitor",
    groups=(
        (
            "Network Probe",
            (
                PluginMenuItem(
                    link="plugins:inventory_monitor:probe_list",
                    link_text="Probes",
                    permissions=["inventory_monitor.view_probe"],
                ),
                PluginMenuItem(
                    link="plugins:inventory_monitor:probediff",
                    link_text="Network Changes",
                    permissions=["inventory_monitor.view_probediff"],
                ),
            ),
        ),
        (
            "Contracts",
            (
                PluginMenuItem(
                    link="plugins:inventory_monitor:contractor_list",
                    link_text="Contractors",
                    permissions=["inventory_monitor.view_contractor"],
                ),
                PluginMenuItem(
                    link="plugins:inventory_monitor:contract_list",
                    link_text="Contracts",
                    permissions=["inventory_monitor.view_contract"],
                ),
                PluginMenuItem(
                    link="plugins:inventory_monitor:invoice_list",
                    link_text="Invoices",
                    permissions=["inventory_monitor.view_invoice"],
                ),
            ),
        ),
        (
            "Components",
            (
                PluginMenuItem(
                    link="plugins:inventory_monitor:component_list",
                    link_text="Components",
                    permissions=["inventory_monitor.view_component"],
                ),
                PluginMenuItem(
                    link="plugins:inventory_monitor:componentservice_list",
                    link_text="Services",
                    permissions=["inventory_monitor.view_componentservice"],
                ),
            ),
        ),
    ),
)
