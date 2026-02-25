from .models import Delivery
from .serializers import DeliverySerializer
from rest_framework import viewsets, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from patients.permissions import IsClinicianOrAdmin
from django.http import HttpResponse
import csv
from django.db.models import Count, Avg
from django.db.models.functions import TruncMonth
from rest_framework.response import Response
from rest_framework import status

class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer

    # Implementing filters and search
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['delivery_type', 'notes', 'patient__first_name', 'patient__last_name']
    ordering_fields = ['delivery_date']
    ordering = ['delivery_date']


    '''
    Override get_queryset to ensure patients only see their own pregnancies.
    Admins and doctors and nurses (other roles) can see all pregnancies to protect patients data
    '''
    
    def get_queryset(self):
        queryset = Delivery.objects.all()
        patient_id = self.kwargs.get("patient_pk")

        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)

        user = self.request.user
        if hasattr(user, "role") and user.role == "patient":
            queryset = queryset.filter(patient__user=user)

        return queryset
    
    def perform_create(self, serializer):
        serializer.save()

# Implement analytics endpoints for deliveries
def _build_delivery_queryset(request, kwargs):
    queryset = Delivery.objects.all()
    patient_id = kwargs.get('patient_pk')
    if patient_id:
        queryset = queryset.filter(patient_id=patient_id)

    user = request.user
    if hasattr(user, 'role') and user.role == 'patient':
        queryset = queryset.filter(patient__user=user)

    return queryset


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_deliveries_csv(request, patient_pk=None):
    qs = _build_delivery_queryset(request, {'patient_pk': patient_pk})
    rows = list(qs.values())
    if not rows:
        return Response({'detail': 'No deliveries found'}, status=404)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="deliveries_export.csv"'

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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def deliveries_summary(request, patient_pk=None):
    user = request.user
    # patients may only view their own deliveries summary
    if getattr(user, 'role', None) == 'patient':
        from patients.models import Patient as PatientModel
        try:
            patient_obj = PatientModel.objects.get(user=user)
        except PatientModel.DoesNotExist:
            return Response({'detail': 'Patient record not found.'}, status=status.HTTP_404_NOT_FOUND)
        if patient_pk is not None and int(patient_pk) != patient_obj.id:
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
        patient_pk = patient_obj.id
    elif getattr(user, 'role', None) not in ['doctor', 'nurse', 'admin']:
        return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

    qs = _build_delivery_queryset(request, {'patient_pk': patient_pk})
    total = qs.count()
    by_mode = {item['delivery_mode']: item['count'] for item in qs.values('delivery_mode').annotate(count=Count('id'))}
    avg_birth_weight = qs.aggregate(avg_bw=Avg('birth_weight_g'))['avg_bw']
    alive_counts = qs.values('alive').annotate(count=Count('id'))
    alive_summary = {item['alive']: item['count'] for item in alive_counts}

    monthly_qs = qs.annotate(month=TruncMonth('delivery_date')).values('month').annotate(count=Count('id')).order_by('month')
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
        'total_deliveries': total,
        'by_mode': by_mode,
        'average_birth_weight_g': avg_birth_weight,
        'alive_counts': alive_summary,
        'monthly_deliveries': monthly,
    }

    return Response(data)

