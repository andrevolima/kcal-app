from django.urls import path

from .invitation_views import AthleteInviteView
from .views import AthleteDeactivateView, AthleteDetailView, AthleteListCreateView


urlpatterns = [
    path('', AthleteListCreateView.as_view(), name='athlete-list-create'),
    path('<int:pk>/', AthleteDetailView.as_view(), name='athlete-detail'),
    path('<int:pk>/invite/', AthleteInviteView.as_view(), name='athlete-invite'),
    path(
        '<int:pk>/deactivate/',
        AthleteDeactivateView.as_view(),
        name='athlete-deactivate',
    ),
]
