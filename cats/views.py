from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from datetime import date, timedelta

from .models import Achievement, Cat, User, Vaccine, CatVaccination, Reminder
from .permissions import IsOwnerOrReadOnly, IsCatOwnerOrReadOnly
from .serializers import (
    AchievementSerializer, CatSerializer, UserSerializer,
    VaccineSerializer, CatVaccinationSerializer, ReminderSerializer
)


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['color', 'owner']
    search_fields = ['name']
    ordering_fields = ['name', 'birth_year']
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer


class VaccineViewSet(viewsets.ModelViewSet):
    queryset = Vaccine.objects.all()
    serializer_class = VaccineSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]


class CatVaccinationViewSet(viewsets.ModelViewSet):
    queryset = CatVaccination.objects.all()
    serializer_class = CatVaccinationSerializer
    permission_classes = [IsCatOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['cat', 'vaccine', 'date']
    ordering_fields = ['date', 'next_date']

    def get_queryset(self):
        qs = CatVaccination.objects.all()
        status_filter = self.request.query_params.get('status', None)
        if status_filter == 'expired':
            qs = qs.filter(completed=False, next_date__lt=date.today())
        elif status_filter == 'pending':
            qs = qs.filter(completed=False, next_date__gte=date.today())
        elif status_filter == 'completed':
            qs = qs.filter(completed=True)
        return qs

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def expired(self, request):
        expired = CatVaccination.objects.filter(
            completed=False, next_date__lt=date.today()
        )
        serializer = self.get_serializer(expired, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def upcoming(self, request):
        days_ahead = int(request.query_params.get('days', 7))
        upcoming_date = date.today() + timedelta(days=days_ahead)
        upcoming = CatVaccination.objects.filter(
            completed=False, next_date__gte=date.today(), next_date__lte=upcoming_date
        )
        serializer = self.get_serializer(upcoming, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def due(self, request):
        overdue = CatVaccination.objects.filter(
            completed=False, next_date__lt=date.today()
        )
        serializer = self.get_serializer(overdue, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsCatOwnerOrReadOnly])
    def complete(self, request, pk=None):
        vaccination = self.get_object()
        vaccination.completed = True
        vaccination.save()
        serializer = self.get_serializer(vaccination)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsCatOwnerOrReadOnly])
    def remind(self, request, pk=None):
        vaccination = self.get_object()
        message = request.data.get('message', f'Напоминание: вакцинация {vaccination.vaccine.name} для кота {vaccination.cat.name}')
        reminder = Reminder.objects.create(
            cat=vaccination.cat,
            vaccination=vaccination,
            message=message
        )
        serializer = ReminderSerializer(reminder)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReminderViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.all()
    serializer_class = ReminderSerializer
    permission_classes = [IsCatOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['cat']
    ordering_fields = ['created_at']

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            return Reminder.objects.filter(cat__owner=self.request.user)
        return Reminder.objects.none()
