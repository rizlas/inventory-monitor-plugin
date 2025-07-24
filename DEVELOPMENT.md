# Inventory Monitor Plugin - Development Guide

## Recent Improvements (2025)

### Configuration Migration
- Follows NetBox plugin best practices with `default_settings` configuration
- Cleaned up unused configuration parameters and helper functions
- Settings now accessible via `settings.py` helper module

### Template Integration Cleanup
- Removed duplicate AssetProbeExtension from template extensions
- Integrated probe information directly into asset detail templates
- Eliminated redundant template functionality while preserving probe status display
- Cleaner separation of concerns between template extensions and page content

### Probe Status Visualization
- Added `is_recently_probed()` methods to Asset and Probe models
- Implemented visual feedback with CSS styling for recent vs stale probes
- Enhanced asset tables with probe status columns
- Probe information now displayed in asset detail pages with status badges

### Performance Optimizations
- Added database query optimizations in asset list views
- Implemented prefetch_related for related objects
- Reduced N+1 query problems in probe relationships

### Code Quality Improvements
- Centralized settings in plugin configuration (`__init__.py`)
- Settings helper module (`settings.py`) for easy access to configuration
- Enhanced CSS with CSS variables and theme support
- Added validation methods to Probe model
- Removed code duplication and unused functionality

## Architecture Overview

### Models Relationship
```
Asset ←→ Probe (via serial number matching)
Asset → AssetType
Asset → Contract (order_contract)
Asset ← GenericForeignKey (assigned to Device, Site, Location, etc.)
Asset ←→ RMA (via serial numbers)
Asset ←→ ABRA (many-to-many)
```

### Key Components
1. **Models**: Core business logic and data relationships with probe status methods
2. **Views**: Standard NetBox generic views with custom enhancements
3. **Tables**: Enhanced django-tables2 with probe status indicators
4. **Templates**: Custom templates with integrated probe status visualization
5. **Template Extensions**: Streamlined plugin integration points for NetBox objects
6. **Configuration**: Plugin settings via `default_settings` in `__init__.py`

## Recent Architectural Changes

### Configuration Refactoring (2025)
- **After**: NetBox plugin configuration pattern with `default_settings`
- **Benefits**: Configurable settings, follows NetBox best practices, easier maintenance

### Template Extension Cleanup (2025)
- **Before**: Duplicate probe display via AssetProbeExtension + asset detail template
- **After**: Single probe display integrated in asset detail template
- **Benefits**: Eliminated code duplication, cleaner architecture, better user experience

### Settings Access Pattern
```python
# Recommended approach
from inventory_monitor.settings import get_probe_recent_days
days = get_probe_recent_days()

# Alternative approach
from inventory_monitor.settings import get_plugin_settings
settings = get_plugin_settings()
days = settings.get("probe_recent_days", 7)
```

## Performance Considerations

### Configuration Architecture
The plugin follows NetBox plugin patterns:
- Settings defined in `__init__.py` as `default_settings`
- Helper functions in `settings.py` for easy access
- Backward compatible with previous versions

### Database Optimizations
- Use `select_related()` for foreign keys
- Use `prefetch_related()` for many-to-many and reverse foreign keys
- Index frequently queried fields (serial numbers, timestamps)

### Caching Strategies
- Consider caching probe status results for large asset lists
- Cache expensive aggregations like asset counts

## Future Improvements

### Short Term
1. Implement bulk operations for assets
2. Add more comprehensive error handling
3. Add asset lifecycle status automation

### Medium Term
1. Add API rate limiting
2. Implement real-time probe status updates
3. Add advanced filtering and search capabilities
4. Enhanced mobile-responsive UI

### Long Term
1. Machine learning for asset lifecycle prediction
2. Integration with external inventory systems
3. Advanced analytics and reporting dashboard
4. Multi-tenant probe data isolation
