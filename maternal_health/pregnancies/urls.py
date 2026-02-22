from rest_framework_nested import routers
from .views import PregnancyViewSet
from patients.views import PatientProfileViewSet
from visits.views import VisitViewSet

# Base router for patients
router = routers.DefaultRouter()
router.register(r'patients', PatientProfileViewSet, basename='pregnancy')

# Nested route to get pregnancies for a specific patient
patient_router = routers.NestedDefaultRouter(router, r'patients', lookup='patient')
patient_router.register(r'pregnancies', PregnancyViewSet, basename='patient-pregnancies')


# Nested route for visits under 
pregnancies_router = routers.NestedDefaultRouter(patient_router, r'pregnancies', lookup='pregnancy')
pregnancies_router.register(r'visits', VisitViewSet, basename='pregnancy-visits')

urlpatterns = router.urls + patient_router.urls + pregnancies_router.urls


# Urls to get all pregnancies in the system
router.register(r'pregnancies', PregnancyViewSet, basename='pregnancies')
urlpatterns = router.urls