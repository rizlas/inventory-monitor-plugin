from django.urls import path
from netbox.views.generic import ObjectChangeLogView

from . import models, views

urlpatterns = (
    # Probes
    path('probes/', views.ProbeListView.as_view(), name='probe_list'),
    path('probes/add/', views.ProbeEditView.as_view(), name='probe_add'),
    path('probes/<int:pk>/', views.ProbeView.as_view(), name='probe'),
    path('probes/<int:pk>/edit/', views.ProbeEditView.as_view(), name='probe_edit'),
    path('probes/<int:pk>/delete/',
         views.ProbeDeleteView.as_view(), name='probe_delete'),
    path('probes/<int:pk>/changelog/', ObjectChangeLogView.as_view(),
         name='probe_changelog', kwargs={'model': models.Probe}),
    path("probes/delete/", views.ProbeBulkDeleteView.as_view(),
         name="probe_bulk_delete",),


    # Contractors
    path('contractors/', views.ContractorListView.as_view(), name='contractor_list'),
    path('contractors/add/', views.ContractorEditView.as_view(),
         name='contractor_add'),
    path('contractors/<int:pk>/', views.ContractorView.as_view(), name='contractor'),
    path('contractors/<int:pk>/edit/',
         views.ContractorEditView.as_view(), name='contractor_edit'),
    path('contractors/<int:pk>/delete/',
         views.ContractorDeleteView.as_view(), name='contractor_delete'),
    path('contractors/<int:pk>/changelog/', ObjectChangeLogView.as_view(),
         name='contractor_changelog', kwargs={'model': models.Contractor}),


    # Contracts
    path('contracts/', views.ContractListView.as_view(), name='contract_list'),
    path('contracts/add/', views.ContractEditView.as_view(), name='contract_add'),
    path('contracts/<int:pk>/', views.ContractView.as_view(), name='contract'),
    path('contracts/<int:pk>/edit/',
         views.ContractEditView.as_view(), name='contract_edit'),
    path('contracts/<int:pk>/delete/',
         views.ContractDeleteView.as_view(), name='contract_delete'),
    path('contracts/<int:pk>/changelog/', ObjectChangeLogView.as_view(),
         name='contract_changelog', kwargs={'model': models.Contract}),

    # Files
    path('invmon_file_attachments/add/', views.InvMonFileAttachmentEditView.as_view(),
         name='invmon_file_attachment_add'),
    path('invmon_file_attachments/<int:pk>/edit/',
         views.InvMonFileAttachmentEditView.as_view(), name='invmon_file_attachment_edit'),
    path('invmon_file_attachments/<int:pk>/delete/',
         views.InvMonFileAttachmentDeleteView.as_view(), name='invmon_file_attachment_delete'),
)
