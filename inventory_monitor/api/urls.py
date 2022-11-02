from netbox.api.routers import NetBoxRouter

from . import views

app_name = 'inventory_monitor'
router = NetBoxRouter()
router.register('probes', views.ProbeViewSet)
router.register('contractors', views.ContractorViewSet)
router.register('contracts', views.ContractViewSet)

urlpatterns = router.urls
