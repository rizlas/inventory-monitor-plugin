from netbox.api.viewsets import NetBoxModelViewSet

from .. import filtersets, models
from .serializers import (ContractorSerializer, ContractSerializer,
                          ProbeSerializer, InvMonFileAttachmentSerializer)
from netbox.api.metadata import ContentTypeMetadata


class ProbeViewSet(NetBoxModelViewSet):
    queryset = models.Probe.objects.prefetch_related('tags', 'device')
    serializer_class = ProbeSerializer
    filterset_class = filtersets.ProbeFilterSet


class ContractorViewSet(NetBoxModelViewSet):
    queryset = models.Contractor.objects.prefetch_related('tags')
    serializer_class = ContractorSerializer
    filterset_class = filtersets.ContractorFilterSet


class ContractViewSet(NetBoxModelViewSet):
    queryset = models.Contract.objects.prefetch_related('tags', 'contractor')
    serializer_class = ContractSerializer
    filterset_class = filtersets.ContractFilterSet


class InvMonFileAttachmentViewSet(NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = models.InvMonFileAttachment.objects.all()
    serializer_class = InvMonFileAttachmentSerializer
    filterset_class = filtersets.InvMonFileAttachmentFilterSet
