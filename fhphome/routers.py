from rest_framework.routers import DefaultRouter

from proposals.viewsets import ProposalViewSet

router = DefaultRouter()
router.register('proposals-abc', ProposalViewSet, basename='proposals')

urlpatterns = router.urls