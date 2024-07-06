from django.urls import path
from .views import RegisterView, LoginView, UserDetailView, OrganisationListView

urlpatterns = [
    path('auth/register/', RegisterView.as_view()),
    path('auth/login/', LoginView.as_view()),
    path('api/users/<str:user_id>/', UserDetailView.as_view()),
    path('api/organisations/', OrganisationListView.as_view())
]