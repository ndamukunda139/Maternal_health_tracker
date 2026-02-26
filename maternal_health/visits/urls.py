from rest_framework_nested import routers
from patients.views import PatientProfileViewSet
from pregnancies.views import PregnancyViewSet
from deliveries.views import DeliveryViewSet
from visits.views import VisitViewSet, export_visits_csv, visits_summary
from django.urls import path

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

# Analytics endpoints (CSV export + JSON summary)
urlpatterns += [
	path('analytics/visits/export/', export_visits_csv, name='visits-export'),
	path('analytics/visits/summary/', visits_summary, name='visits-summary'),

	path('patients/<int:patient_pk>/analytics/visits/export/', export_visits_csv, name='patient-visits-export'),
	path('patients/<int:patient_pk>/analytics/visits/summary/', visits_summary, name='patient-visits-summary'),

	path('patients/<int:patient_pk>/pregnancies/<int:pregnancy_pk>/analytics/visits/export/', export_visits_csv, name='pregnancy-visits-export'),
	path('patients/<int:patient_pk>/pregnancies/<int:pregnancy_pk>/analytics/visits/summary/', visits_summary, name='pregnancy-visits-summary'),

	path('patients/<int:patient_pk>/deliveries/<int:delivery_pk>/analytics/visits/export/', export_visits_csv, name='delivery-visits-export'),
	path('patients/<int:patient_pk>/deliveries/<int:delivery_pk>/analytics/visits/summary/', visits_summary, name='delivery-visits-summary'),
]
