# Plugin Configuration Guide

The Inventory Monitor plugin can be configured through NetBox's plugin settings. Add configuration to your `configuration.py` file:

```python
PLUGINS_CONFIG = {
    "inventory_monitor": {
        # Probe Status Settings
        "probe_recent_days": 7,          # Days to consider probe "recent"

        # External Inventory Status Configuration
        "external_inventory_status_config": {
            "1": {"label": "Active", "color": "success"},
            "0": {"label": "Pending Activation", "color": "warning"},
            "2": {"label": "Decommissioned", "color": "danger"},
        },

        # Custom tooltip template for status display
        "external_inventory_tooltip_template": "<span class='badge text-bg-{color}'>{code}</span> {label}",
    }
}
```

## Configuration Options

### Probe Status Settings

- **probe_recent_days** (default: 7): Number of days to consider a probe "recent"

### External Inventory Status Configuration

- **external_inventory_status_config** (default: see example): Maps status codes to display labels and Bootstrap colors
- **external_inventory_tooltip_template** (default: see example): Template string for formatting status tooltips

#### Status Configuration Structure
```python
{
    "status_code": {
        "label": "Human readable label",
        "color": "bootstrap_color_class"
    }
}
```

**Available Bootstrap Colors**: `primary`, `secondary`, `success`, `danger`, `warning`, `info`, `light`, `dark`

#### Tooltip Template Variables
- `{code}`: The status code
- `{label}`: The translated label  
- `{color}`: The Bootstrap color class

### Examples

**Simple Text Tooltip:**
```python
"external_inventory_tooltip_template": "{code}: {label}"
```

**Custom Badge Style:**
```python
"external_inventory_tooltip_template": "<span class='badge bg-{color} text-white'>{code}</span> - {label}"
```

**Different Status Codes:**
```python
"external_inventory_status_config": {
    "ACTIVE": {"label": "Active", "color": "success"},
    "INACTIVE": {"label": "Inactive", "color": "secondary"},
    "MAINTENANCE": {"label": "Under Maintenance", "color": "warning"},
}
```

## Using Settings in Code

```python
from inventory_monitor.settings import get_plugin_settings, get_probe_recent_days

# Get all settings
settings = get_plugin_settings()

# Get specific setting with helper function
recent_days = get_probe_recent_days()

# Get setting with fallback
custom_days = settings.get("probe_recent_days", 7)
```

## Migration from Previous Versions

If you were previously using hardcoded constants, update your code to use the plugin settings instead:

**Before:**
```python
# Old hardcoded approach
RECENT_DAYS = 7
```

**After:**
```python
from inventory_monitor.settings import get_probe_recent_days
recent_days = get_probe_recent_days()
# or
from django.conf import settings
PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("inventory_monitor", {})
days = PLUGIN_SETTINGS.get("probe_recent_days", 7)
```
