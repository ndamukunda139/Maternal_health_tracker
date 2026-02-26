from rest_framework import viewsets, permissions
from django.shortcuts import get_object_or_404
from .models import Visit
from .serializers import VisitSerializer, PrenatalVisitSerializer, PostnatalVisitSerializer
from deliveries.models import Delivery
from pregnancies.models import Pregnancy
from patients.models import Patient
from rest_framework import serializers, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from patients.permissions import IsClinicianOrAdmin
from patients.models import Patient as PatientModel
from django.http import HttpResponse
import csv
from django.db.models import Count, Avg
from django.db.models.functions import TruncMonth


# VisitViewSet with dynamic serializer and strict filtering logic to ensure data integrity and proper access control.
class VisitViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    # Implementing filter and search

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['visit_type', 'notes', 'patient__first_name', 'patient__last_name']
    ordering_fields = ['visit_date']
    ordering = ['visit_date']

    # Override get_queryset to ensure proper filtering based on nested relationships and user role.
    def get_queryset(self):
        queryset = Visit.objects.all()

        patient_id = self.kwargs.get("patient_pk")
        pregnancy_id = self.kwargs.get("pregnancy_pk")
        delivery_id = self.kwargs.get("delivery_pk")

        # Strict filtering for patient + pregnancy
        if patient_id and pregnancy_id:
            if not Pregnancy.objects.filter(pk=pregnancy_id, patient_id=patient_id).exists():
                return Visit.objects.none()
            queryset = queryset.filter(patient_id=patient_id, pregnancy_id=pregnancy_id)

        elif patient_id:
            queryset = queryset.filter(patient_id=patient_id)

        elif pregnancy_id:
            queryset = queryset.filter(pregnancy_id=pregnancy_id)

        # Strict filtering for patient + delivery
        if patient_id and delivery_id:
            if not Delivery.objects.filter(pk=delivery_id, patient_id=patient_id).exists():
                return Visit.objects.none()
            queryset = queryset.filter(patient_id=patient_id, delivery_id=delivery_id)

        elif delivery_id:
            queryset = queryset.filter(delivery_id=delivery_id)

        # Restrict patients to only their own visits
        user = self.request.user
        if hasattr(user, "role") and user.role == "patient":
            queryset = queryset.filter(patient__user=user)

        return queryset

    # Override get_serializer_class to return different serializers based on the presence of pregnancy_pk (Prenatal) or delivery_pk (Postnatal) in the URL.
    def get_serializer_class(self):
        if "pregnancy_pk" in self.kwargs:
            return PrenatalVisitSerializer
        elif "delivery_pk" in self.kwargs:
            return PostnatalVisitSerializer
        return VisitSerializer

    # Override perform_create to automatically set patient, pregnancy, delivery, visit_type, and provider based on URL and authenticated user, with strict consistency checks.
    def perform_create(self, serializer):
        patient_id = self.kwargs.get("patient_pk")
        pregnancy_id = self.kwargs.get("pregnancy_pk")
        delivery_id = self.kwargs.get("delivery_pk")

        patient = get_object_or_404(Patient, pk=patient_id) if patient_id else None
        pregnancy = (
            get_object_or_404(Pregnancy, pk=pregnancy_id, patient_id=patient_id)
            if pregnancy_id else None
        )
        delivery = (
            get_object_or_404(Delivery, pk=delivery_id, patient_id=patient_id)
            if delivery_id else None
        )

        # Decide visit type automatically
        if pregnancy_id:
            visit_type = "Antenatal"
        elif delivery_id:
            visit_type = "Postnatal"
        else:
            visit_type = "General"

        # Strict consistency checks
        if pregnancy and patient and pregnancy.patient_id != int(patient_id):
            raise serializers.ValidationError("Pregnancy does not belong to this patient.")

        if delivery and patient and delivery.patient_id != int(patient_id):
            raise serializers.ValidationError("Delivery does not belong to this patient.")

        serializer.save(
            patient=patient,
            pregnancy=pregnancy,
            delivery=delivery,
            visit_type=visit_type,
            provider=self.request.user,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    # Override to provide custom error responses for validation errors
    def handle_exception(self, exc):
        if isinstance(exc, serializers.ValidationError):
            return Response(
                {"detail": "Validation failed", "error": exc.detail}, 
                status=status.HTTP_400_BAD_REQUEST)
        return super().handle_exception(exc)


# Helper function to build queryset for analytics endpoints with consistent filtering logic
def _build_visit_queryset(request, kwargs):
    queryset = Visit.objects.all()

    patient_id = kwargs.get("patient_pk")
    pregnancy_id = kwargs.get("pregnancy_pk")
    delivery_id = kwargs.get("delivery_pk")

    if patient_id and pregnancy_id:
        if not Pregnancy.objects.filter(pk=pregnancy_id, patient_id=patient_id).exists():
            return Visit.objects.none()
        queryset = queryset.filter(patient_id=patient_id, pregnancy_id=pregnancy_id)
    elif patient_id:
        queryset = queryset.filter(patient_id=patient_id)
    elif pregnancy_id:
        queryset = queryset.filter(pregnancy_id=pregnancy_id)

    if patient_id and delivery_id:
        if not Delivery.objects.filter(pk=delivery_id, patient_id=patient_id).exists():
            return Visit.objects.none()
        queryset = queryset.filter(patient_id=patient_id, delivery_id=delivery_id)
    elif delivery_id:
        queryset = queryset.filter(delivery_id=delivery_id)

    user = request.user
    if hasattr(user, "role") and user.role == "patient":
        queryset = queryset.filter(patient__user=user)

    return queryset

# Analytics endpoints for visits (CSV export and JSON summary) with consistent filtering logic and role-based access control.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_visits_csv(request, patient_pk=None, pregnancy_pk=None, delivery_pk=None):
    """Export visits as CSV. Optional nested filtering via patient_pk, pregnancy_pk, delivery_pk."""
    qs = _build_visit_queryset(request, {"patient_pk": patient_pk, "pregnancy_pk": pregnancy_pk, "delivery_pk": delivery_pk})

    rows = list(qs.values())

    if not rows:
        return Response({"detail": "No visits found"}, status=status.HTTP_404_NOT_FOUND)

    # Prepare CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="visits_export.csv"'

    fieldnames = list(rows[0].keys())
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()

    # convert non-serializable types
    for r in rows:
        for k, v in r.items():
            try:
                if hasattr(v, 'isoformat'):
                    r[k] = v.isoformat()
            except Exception:
                pass
        writer.writerow(r)

    return response

# Summary analytics endpoint for visits, scoped to patient/pregnancy/delivery if provided, with role-based access control.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def visits_summary(request, patient_pk=None, pregnancy_pk=None, delivery_pk=None):
    """
    Return basic summary statistics for visits as JSON.

    Clinicians/admins: can view any patient/pregnancy/delivery scope.
    Patients: may only view their own summary; if no `patient_pk` is provided,
    we automatically scope to the authenticated patient's record.
    
    """
    user = request.user
    if getattr(user, 'role', None) == 'patient':
        try:
            patient_obj = PatientModel.objects.get(user=user)
        except PatientModel.DoesNotExist:
            return Response({'detail': 'Patient record not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # if a different patient_pk was requested, forbid
        if patient_pk is not None and int(patient_pk) != patient_obj.id:
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
        
        # scope to the authenticated patient
        patient_pk = patient_obj.id
    
    # For non-patient users, we allow any scope but still enforce role-based access control
    elif getattr(user, 'role', None) not in ['doctor', 'nurse', 'admin']:
        return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

    qs = _build_visit_queryset(request, {"patient_pk": patient_pk, "pregnancy_pk": pregnancy_pk, "delivery_pk": delivery_pk})

    total = qs.count()
    by_type_qs = qs.values('visit_type').annotate(count=Count('id'))
    by_type = {item['visit_type']: item['count'] for item in by_type_qs}

    avg_hemo = qs.aggregate(avg_hemo=Avg('hemoglobin_level'))['avg_hemo']
    avg_weight = qs.aggregate(avg_weight=Avg('weight_kg'))['avg_weight']

    monthly_qs = qs.annotate(month=TruncMonth('visit_date')).values('month').annotate(count=Count('id')).order_by('month')
    monthly = []
    for m in monthly_qs:
        month_val = m.get('month')
        if month_val is None:
            month_str = None
        elif hasattr(month_val, 'date'):
            month_str = month_val.date().isoformat()
        elif hasattr(month_val, 'isoformat'):
            month_str = month_val.isoformat()
        else:
            month_str = str(month_val)
        monthly.append({'month': month_str, 'count': m['count']})

    data = {
        'total_visits': total,
        'by_type': by_type,
        'average_hemoglobin': avg_hemo,
        'average_weight_kg': avg_weight,
        'monthly_counts': monthly,
    }

    return Response(data)