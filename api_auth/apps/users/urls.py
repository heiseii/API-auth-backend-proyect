from django.urls import path
from .views import RegisterView, ProfileView, RoleAssignView, RoleListView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", ProfileView.as_view(), name="profile"),
    path("roles/", RoleListView.as_view(), name="roles"),
]