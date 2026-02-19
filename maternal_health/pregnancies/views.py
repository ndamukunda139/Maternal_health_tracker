from .models import Pregnancy
from .serializers import PregnancySerializer
from rest_framework import viewsets
from rest_framework import permissions

class PregnancyViewSet(viewsets.ModelViewSet):
    serializer_class = PregnancySerializer
    permission_classes = [permissions.IsAuthenticated]

    '''
    Override get_queryset to ensure patients only see their own pregnancies.
    Admins and doctors and nurses (other roles) can see all pregnancies to protect patients data.

    '''

    def get_queryset(self):
        patient_id = self.kwargs.get("patient_pk")
        queryset = Pregnancy.objects.all()
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        user = self.request.user
        if user.role == 'patient':
            return self.queryset.filter(patient__user=user)
        return queryset
    
    def perform_create(self, serializer):
        patient_id = self.kwargs.get("patient_pk")
        serializer.save(patient_id=patient_id, created_by=self.request.user, updated_by=self.request.user)
