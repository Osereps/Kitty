from rest_framework import routers
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from cats.views import (
    AchievementViewSet, CatViewSet, UserViewSet,
    VaccineViewSet, CatVaccinationViewSet, ReminderViewSet
)

router = routers.DefaultRouter()
router.register('cats', CatViewSet)
router.register('users', UserViewSet)
router.register('achievements', AchievementViewSet)
router.register(r'vaccines', VaccineViewSet)
router.register(r'cat-vaccinations', CatVaccinationViewSet)
router.register(r'reminders', ReminderViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
