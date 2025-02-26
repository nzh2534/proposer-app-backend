from api import permissions
from rest_framework import generics, mixins

from .models import Proposal, ComplianceImages, Template
from .serializers import ProposalSerializer, ComplianceImagesSerializer, TemplateSerializer


class ProposalListCreateAPIView(
    permissions.AccessByCreatingUserPermission,
    generics.ListCreateAPIView):

    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer

class ProposalDetailAPIView(
    permissions.AccessByCreatingUserPermission,
    generics.RetrieveAPIView):

    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer

class ProposalUpdateAPIView(
    permissions.AccessByCreatingUserPermission,
    generics.UpdateAPIView):

    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    lookup_field = 'pk'

class ProposalDestroyAPIView(
    permissions.AccessByCreatingUserPermission,
    generics.DestroyAPIView):

    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    lookup_field = 'pk'

    def perform_destroy(self, instance):
        super().perform_destroy(instance)

class ComplianceListCreateAPIView(
    permissions.AccessByCreatingUserPermission,
    generics.ListCreateAPIView):

    queryset = ComplianceImages.objects.all()
    serializer_class = ComplianceImagesSerializer

class ComplianceUpdateAPIView(
    permissions.AccessByCreatingUserPermission,
    generics.UpdateAPIView):

    queryset = ComplianceImages.objects.all()
    serializer_class = ComplianceImagesSerializer
    lookup_field = 'id'

    def perform_update(self, serializer):
        instance = serializer.save()

class ComplianceDestroyAPIView(
    permissions.AccessByCreatingUserPermission,
    generics.DestroyAPIView):

    queryset = ComplianceImages.objects.all()
    serializer_class = ComplianceImagesSerializer
    lookup_field = 'id'

    def perform_destroy(self, instance):
        super().perform_destroy(instance)

class TemplateListCreateAPIView(
    permissions.AccessByCreatingUserPermission,
    generics.ListCreateAPIView):

    queryset = Template.objects.all()
    serializer_class = TemplateSerializer

class TemplateUpdateAPIView(
    permissions.AccessByCreatingUserPermission,
    generics.UpdateAPIView):

    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    lookup_field = 'id'

    def perform_update(self, serializer):
        instance = serializer.save()

class TemplateDestroyAPIView(
    permissions.AccessByCreatingUserPermission,
    generics.DestroyAPIView):

    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    lookup_field = 'id'

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
