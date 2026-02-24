from .models import Delivery
from .serializers import DeliverySerializer
from rest_framework import viewsets, filters


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

