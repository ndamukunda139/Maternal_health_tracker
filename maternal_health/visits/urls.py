from rest_framework_nested import routers
from visits.views import VisitViewSet
from patients.views import PatientProfileViewSet

router = routers.DefaultRouter()
router.register(r'patients', PatientProfileViewSet, basename='patient')

# Nested router for visits under patients
patients_router = routers.NestedDefaultRouter(router, r'patients', lookup='patient')
patients_router.register(r'visits', VisitViewSet, basename='patient-visits')

urlpatterns = router.urls + patients_router.urls