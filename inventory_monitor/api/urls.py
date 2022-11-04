from netbox.api.routers import NetBoxRouter

from . import views

app_name = 'inventory_monitor'
router = NetBoxRouter()
router.register('probes', views.ProbeViewSet)
router.register('contractors', views.ContractorViewSet)
router.register('contracts', views.ContractViewSet)
router.register('invmon_file_attachment', views.InvMonFileAttachmentViewSet)

urlpatterns = router.urls
