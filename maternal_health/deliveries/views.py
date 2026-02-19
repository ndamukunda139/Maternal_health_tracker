from .models import Delivery
from .serializers import DeliverySerializer
from rest_framework import viewsets


class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer

    '''
    Override get_queryset to ensure patients only see their own pregnancies.
    Admins and doctors and nurses (other roles) can see all pregnancies to protect patients data
    '''
    def get_queryset(self):
        user = self.request.user
        if user.role == 'patient':
            return self.queryset.filter(patient__user=user)
        return Delivery.objects.all()
    
    def perform_create(self, serializer):
        serializer.save()
