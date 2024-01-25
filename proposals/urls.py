from django.urls import path

from . import views

urlpatterns = [
    path('', views.ProposalListCreateAPIView.as_view(), name='proposal-list'),
    path('<int:pk>/update/', views.ProposalUpdateAPIView.as_view(), name='proposal-edit'),
    path('<int:pk>/delete/', views.ProposalDestroyAPIView.as_view()),
    path('<int:pk>/', views.ProposalDetailAPIView.as_view(), name='proposal-detail'),
    path('<int:pk>/compliance/', views.ComplianceListCreateAPIView.as_view(), name='compliance-list'),
    path('<int:pk>/compliance/<int:id>/update/', views.ComplianceUpdateAPIView.as_view(), name='compliance-edit'),
    path('<int:pk>/compliance/<int:id>/delete/', views.ComplianceDestroyAPIView.as_view()),
    path('template/', views.TemplateListCreateAPIView.as_view(), name='template-list'),
    path('template/<int:pk>/update/', views.TemplateUpdateAPIView.as_view(), name='template-edit'),
    path('template/<int:pk>/delete/', views.TemplateDestroyAPIView.as_view())
]
