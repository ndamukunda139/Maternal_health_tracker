from rest_framework_nested import routers
from patients.views import PatientProfileViewSet
from pregnancies.views import PregnancyViewSet
from deliveries.views import DeliveryViewSet
from visits.views import VisitViewSet

# Base router
router = routers.DefaultRouter()
router.register(r'patients', PatientProfileViewSet, basename='patient')
router.register(r'visits', VisitViewSet, basename='visits')        # top-level visits
router.register(r'deliveries', DeliveryViewSet, basename='deliveries')  # top-level deliveries
router.register(r'pregnancies', PregnancyViewSet, basename='pregnancies')  # top-level pregnancies

# Nested pregnancies under patients
patients_router = routers.NestedDefaultRouter(router, r'patients', lookup='patient')
patients_router.register(r'pregnancies', PregnancyViewSet, basename='patient-pregnancies')
patients_router.register(r'deliveries', DeliveryViewSet, basename='patient-deliveries')
patients_router.register(r'visits', VisitViewSet, basename='patient-visits')

# Nested deliveries under pregnancies
pregnancies_router = routers.NestedDefaultRouter(patients_router, r'pregnancies', lookup='pregnancy')
pregnancies_router.register(r'deliveries', DeliveryViewSet, basename='pregnancy-deliveries')
pregnancies_router.register(r'visits', VisitViewSet, basename='pregnancy-visits')

# Nested visits under deliveries
deliveries_router = routers.NestedDefaultRouter(patients_router, r'deliveries', lookup='delivery')
deliveries_router.register(r'visits', VisitViewSet, basename='delivery-visits')


# Combine all
urlpatterns = []
urlpatterns += router.urls
urlpatterns += patients_router.urls
urlpatterns += pregnancies_router.urls
urlpatterns += deliveries_router.urls

# urlpatterns = router.urls + patients_router.urls + pregnancies_router.urls + deliveries_router.urls