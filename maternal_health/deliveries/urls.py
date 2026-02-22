from rest_framework_nested import routers
from .views import DeliveryViewSet
from patients.views import PatientProfileViewSet
from visits.views import VisitViewSet

router = routers.DefaultRouter()
router.register(r'patients', PatientProfileViewSet, basename='patient')

# Nested route to get deliveries for a specific patient
patient_router = routers.NestedDefaultRouter(router, r'patients', lookup='patient')
patient_router.register(r'deliveries', DeliveryViewSet, basename='patient-deliveries')


# Nesed route for visits under deliveries
delivery_router = routers.NestedDefaultRouter(patient_router, r'deliveries', lookup='delivery')
delivery_router.register(r'visits', VisitViewSet, basename='delivery-visits')

urlpatterns = router.urls + patient_router.urls + delivery_router.urls

# Urls to get all deliveries in the system
router.register(r'deliveries', DeliveryViewSet, basename='deliveries')
urlpatterns = router.urls