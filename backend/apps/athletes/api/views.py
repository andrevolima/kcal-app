from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.athletes.selectors import (
    get_accessible_athletes,
    get_nutritionist_athletes,
)
from apps.athletes.services import (
    create_athlete,
    deactivate_athlete,
    update_athlete,
)

from .permissions import CanAccessAthlete, IsNutritionist
from .serializers import (
    AthleteCreateSerializer,
    AthleteSerializer,
    AthleteUpdateSerializer,
)


class AthleteListCreateView(generics.GenericAPIView):
    permission_classes = [IsNutritionist]

    def get(self, request):
        athletes = get_nutritionist_athletes(nutritionist=request.user)
        page = self.paginate_queryset(athletes)
        serializer = AthleteSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = AthleteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        athlete = create_athlete(
            nutritionist=request.user,
            **serializer.validated_data,
        )
        return Response(AthleteSerializer(athlete).data, status=status.HTTP_201_CREATED)


class AthleteDetailView(generics.GenericAPIView):
    permission_classes = [CanAccessAthlete]
    serializer_class = AthleteSerializer

    def get_queryset(self):
        return get_accessible_athletes(user=self.request.user)

    def get(self, request, *args, **kwargs):
        athlete = self.get_object()
        return Response(AthleteSerializer(athlete).data)

    def patch(self, request, *args, **kwargs):
        athlete = self.get_object()
        serializer = AthleteUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        athlete = update_athlete(
            athlete=athlete,
            nutritionist=request.user,
            **serializer.validated_data,
        )
        return Response(AthleteSerializer(athlete).data)


class AthleteDeactivateView(APIView):
    permission_classes = [IsNutritionist, CanAccessAthlete]

    def post(self, request, pk):
        athlete = generics.get_object_or_404(
            get_nutritionist_athletes(nutritionist=request.user),
            pk=pk,
        )
        self.check_object_permissions(request, athlete)
        athlete = deactivate_athlete(
            athlete=athlete,
            nutritionist=request.user,
        )
        return Response(AthleteSerializer(athlete).data)
