from django.urls import path

from .invitation_views import InvitationActivateView, InvitationDetailView


urlpatterns = [
    path('<str:token>/', InvitationDetailView.as_view(), name='invitation-detail'),
    path(
        '<str:token>/activate/',
        InvitationActivateView.as_view(),
        name='invitation-activate',
    ),
]
