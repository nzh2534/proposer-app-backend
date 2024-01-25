from api import permissions
from rest_framework import generics, mixins

from .models import Proposal, ComplianceImages, Template
from .serializers import ProposalSerializer, ComplianceImagesSerializer, TemplateSerializer


class ProposalListCreateAPIView(
    permissions.AccessByCreatingUserPermission,
    generics.ListCreateAPIView):

    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    # -------- ISN'T NEEDED; SET IN SETTINGS.PY ----------
    # authentication_classes = [     
    #     authentication.SessionAuthentication,
    #     TokenAuthentication
    #     ]

    # ------- IF COMMENTED OUT, DEFAULTS TO PERM IN SETTINGS (CURRENTLY ALL AUTH USERS)------
    # permission_classes = [permissions.IsAdminUser,IsStaffEditorPermission] #Removed bc of Mixin

    #For creating a user in the db along with a new object
    # def perform_create(self, serializer):
    #     #serializer.save(user=self.request.user)
    #     return super().perform_create(serializer)

class ProposalDetailAPIView(
    permissions.AccessByCreatingUserPermission,
    generics.RetrieveAPIView):

    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    # lookup_field = 'pk' #like Proposal.objects.get()...

class ProposalUpdateAPIView(
    permissions.AccessByCreatingUserPermission,
    generics.UpdateAPIView):

    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    # permission_classes = [permissions.IsAdminUser,IsStaffEditorPermission] #Removed bc of Mixin
    lookup_field = 'pk'

    # def perform_update(self, serializer):
    #     instance = serializer.save()
    #     if not instance.description:
    #         instance.description = instance.title
    #     if instance.nofo != '':
    #         if len(list(instance.complianceimages_set.all())) == 0:
    #             r = Redis('localhost', 6379)
    #             print(r)
    #             queue = django_rq.get_queue('default', connection=r)
    #             print(queue)
    #             queue.enqueue(compliance_tool, file_path=instance.nofo, pk=instance.pk)
    #             print(queue)
    #             # redis_queue(instance.nofo, instance.pk)
    #             # print(job.get_status())
    #             # result = compliance_tool(instance.nofo, instance.pk)
    #             # index = 0
    #             # proposal = Proposal.objects.get(pk=instance.pk)
    #             # for i in result[0]:
    #             #     new_ci = ComplianceImages(
    #             #         proposal=proposal,
    #             #         title=(i),
    #             #         content=(result[1][index]),
    #             #         title_text=result[2][index],
    #             #         content_text=result[3][index],
    #             #         page_number=result[4][index]
    #             #         )
    #             #     new_ci.save()
    #             #     index += 1

class ProposalDestroyAPIView(
    permissions.AccessByCreatingUserPermission,
    generics.DestroyAPIView):

    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    lookup_field = 'pk'

    def perform_destroy(self, instance):
        super().perform_destroy(instance)


    queryset = ComplianceImages.objects.all()
    serializer_class = ComplianceImagesSerializer

class ComplianceUpdateAPIView(
    permissions.AccessByCreatingUserPermission,
    generics.UpdateAPIView):

    queryset = ComplianceImages.objects.all()
    serializer_class = ComplianceImagesSerializer
    # permission_classes = [permissions.IsAdminUser,IsStaffEditorPermission] #Removed bc of Mixin
    lookup_field = 'id'

    def perform_update(self, serializer):
        instance = serializer.save()
        # if not instance.description:
        #     instance.description = instance.title

class ComplianceDestroyAPIView(
    permissions.AccessByCreatingUserPermission,
    generics.DestroyAPIView):

    queryset = ComplianceImages.objects.all()
    serializer_class = ComplianceImagesSerializer
    lookup_field = 'id'

    def perform_destroy(self, instance):
        super().perform_destroy(instance)

# ----- Alternative Function based view for understanding


# class ProposalMixinView(
#     mixins.ListModelMixin,
#     mixins.RetrieveModelMixin,
#     mixins.CreateModelMixin,
#     generics.GenericAPIView
#     ):
#     queryset = Proposal.objects.all()
#     serializer_class = ProposalSerializer
#     lookup_field = 'pk'

#     def get(self, request, *args, **kwargs):
#         print(args, kwargs)
#         pk = kwargs.get('pk')
#         if pk is not None:
#             return self.retrieve(request, *args, **kwargs)
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)

# @api_view(['GET', 'POST'])
# def proposal_alt_view(request, pk=None, *args, **kwargs):
#     method = request.method #GET or POST ex
    
#     if method == "GET":
#         if pk is not None:
#             #detail view
#             obj = get_object_or_404(Proposal, pk=pk)
#             data = ProposalSerializer(obj, many=False).data
#             return Response(data)
#         #else list view
#         qs = Proposal.objects.all()
#         data = ProposalSerializer(qs, many=True).data
#         return Response(data)

#     if method == "POST":
#         # create an item
#         serializer = ProposalSerializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             # instance = serializer.save()
#             # instance = form.save()
#             title = serializer.validated_data.get('title')
#             description = serializer.validated_data.get('description') or None
#             if description is None:
#                 description = title
#             serializer.save(content = description)
#             print(serializer.data)
#             return Response(serializer.data)
#         return Response({"invalid": "not good data"}, status=400)
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
    lookup_field = 'pk'

    def perform_update(self, serializer):
        instance = serializer.save()

class TemplateDestroyAPIView(
    permissions.AccessByCreatingUserPermission,
    generics.DestroyAPIView):

    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    lookup_field = 'pk'

    def perform_destroy(self, instance):
        super().perform_destroy(instance)