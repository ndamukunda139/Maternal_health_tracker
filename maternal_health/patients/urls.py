from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'patients', views.PatientProfileViewSet, basename='patient')

urlpatterns=[
    path('', include(router.urls)),
]