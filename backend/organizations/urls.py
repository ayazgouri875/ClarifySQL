from django.urls import path
from .views import CurrentOrganizationView, OrganizationMembersView

urlpatterns = [
    path("current/", CurrentOrganizationView.as_view(), name="org-current"),
    path("members/", OrganizationMembersView.as_view(), name="org-members"),
]
