from netbox.api.viewsets import NetBoxModelViewSet

from .. import filtersets, models
from .serializers import (ContractorSerializer, ContractSerializer,
                          ProbeSerializer)


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
