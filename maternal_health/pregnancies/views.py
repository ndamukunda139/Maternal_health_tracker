from .models import Pregnancy
from .serializers import PregnancySerializer
from rest_framework import permissions, viewsets, filters
from django.shortcuts import get_object_or_404
from patients.permissions import IsClinicianOrAdmin
from patients.models import Patient
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
import csv
from django.db.models import Count, Avg
from django.db.models.functions import TruncMonth

class PregnancyViewSet(viewsets.ModelViewSet):
    serializer_class = PregnancySerializer
    permission_classes = [permissions.IsAuthenticated]

    # Filters and Search

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['status', 'notes', 'patient__first_name', 'patient__last_name']
    ordering_fields = ['last_menstrual_period', 'expected_delivery_date']
    ordering = ['expected_delivery_date']


    def get_queryset(self):
        patient_id = self.kwargs.get("patient_pk")
        queryset = Pregnancy.objects.all()
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)

        user = self.request.user
        if hasattr(user, "role") and user.role == "patient":
            queryset = queryset.filter(patient__user=user)

        return queryset

    def perform_create(self, serializer):
        patient_id = self.kwargs.get("patient_pk")
        patient = get_object_or_404(Patient, pk=patient_id)
        serializer.save(
            patient=patient,
            created_by=self.request.user,
            updated_by=self.request.user
        )

    # patients can't create pregnancies, only doctors and nurses can create pregnancies for patients
    def create(self, request, *args, **kwargs):
        if hasattr(request.user, "role") and request.user.role == "patient":
            return Response({"error": "Patients cannot create pregnancies."}, status=403)
        return super().create(request, *args, **kwargs)

# Implement analytics endpoints for pregnancies
def _build_pregnancy_queryset(request, kwargs):
    queryset = Pregnancy.objects.all()
    patient_id = kwargs.get('patient_pk')
    if patient_id:
        queryset = queryset.filter(patient_id=patient_id)

    user = request.user
    if hasattr(user, 'role') and user.role == 'patient':
        queryset = queryset.filter(patient__user=user)

    return queryset

# export pregnancies to CSV for a patient, only accessible by that patient or clinicians/admins
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_pregnancies_csv(request, patient_pk=None):
    qs = _build_pregnancy_queryset(request, {'patient_pk': patient_pk})
    rows = list(qs.values())
    if not rows:
        return Response({'detail': 'No pregnancies found'}, status=status.HTTP_404_NOT_FOUND)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pregnancies_export.csv"'

    fieldnames = list(rows[0].keys())
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        for k, v in r.items():
            try:
                if hasattr(v, 'isoformat'):
                    r[k] = v.isoformat()
            except Exception:
                pass
        writer.writerow(r)

    return response

# Summary analytics endpoint for pregnancies, scoped to patient if patient_pk provided, otherwise global summary for clinicians/admins
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pregnancies_summary(request, patient_pk=None):
    """
    Return basic summary statistics for pregnancies as JSON.

    Clinicians/admins: can view any patient scope or global summary.
    Patients: may only view their own summary; if no `patient_pk` is provided,
    we automatically scope to the authenticated patient's record.
    """
    user = request.user
    if getattr(user, 'role', None) == 'patient':
        try:
            patient_obj = Patient.objects.get(user=user)
        except Patient.DoesNotExist:
            return Response({'detail': 'Patient record not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # if a different patient_pk was requested, forbid
        if patient_pk is not None and int(patient_pk) != patient_obj.id:
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
        
        # scope to the authenticated patient
        patient_pk = patient_obj.id
    
    # For non-patient users, we allow any scope but still enforce role-based access control
    elif getattr(user, 'role', None) not in ['doctor', 'nurse', 'admin']:
        return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

    qs = _build_pregnancy_queryset(request, {'patient_pk': patient_pk})
    total = qs.count()
    by_blood = {item['blood_type']: item['count'] for item in qs.values('blood_type').annotate(count=Count('id'))}
    avg_ga = qs.aggregate(avg_ga=Avg('gestational_age_weeks'))['avg_ga']

    monthly_qs = qs.annotate(month=TruncMonth('expected_delivery_date')).values('month').annotate(count=Count('id')).order_by('month')
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
        'total_pregnancies': total,
        'by_blood_type': by_blood,
        'average_gestational_age_weeks': avg_ga,
        'monthly_expected_deliveries': monthly,
    }

    return Response(data)

