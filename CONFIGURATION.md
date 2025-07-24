# Plugin Configuration Guide

The Inventory Monitor plugin can be configured through NetBox's plugin settings. Add configuration to your `configuration.py` file:

```python
PLUGINS_CONFIG = {
    "inventory_monitor": {
        # Probe Status Settings
        "probe_recent_days": 7,          # Days to consider probe "recent"
    }
}
```

## Configuration Options

### Probe Status Settings

- **probe_recent_days** (default: 7): Number of days to consider a probe "recent"

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
