from django.shortcuts import render, redirect
from .forms import PatientRegistrationForm
from django.contrib.auth.decorators import login_required
from .models import Patient 

# Patient registation and management view
@login_required
def register_patient(request):
    if request.method == "POST":
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.user = request.user  # link to logged-in user
            patient.save()
            return redirect('patient_detail', pk=patient.pk)
        else:
            form = PatientRegistrationForm()
        return render(request, 'patients/register.html', {'form': form})


