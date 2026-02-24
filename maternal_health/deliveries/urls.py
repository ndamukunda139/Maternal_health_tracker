from rest_framework_nested import routers
from .views import DeliveryViewSet
from patients.views import PatientProfileViewSet
from visits.views import VisitViewSet

router = routers.DefaultRouter()
router.register(r'patients', PatientProfileViewSet, basename='patient')
router.register(r'deliveries', DeliveryViewSet, basename='deliveries')  # top-level deliveries

# Nested route to get deliveries for a specific patient
patient_router = routers.NestedDefaultRouter(router, r'patients', lookup='patient')
patient_router.register(r'deliveries', DeliveryViewSet, basename='patient-deliveries')

# Nested route for visits under deliveries
delivery_router = routers.NestedDefaultRouter(patient_router, r'deliveries', lookup='delivery')
delivery_router.register(r'visits', VisitViewSet, basename='delivery-visits')

# Combine routes, patient delivery and visit
urlpatterns = router.urls + patient_router.urls + delivery_router.urls