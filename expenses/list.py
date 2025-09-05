# views.py
from django.shortcuts import render, redirect
from .forms import DriverForm, VehicleForm, DriverAssignmentForm
from .models import Driver, Vehicle, DriverAssignment

def driver_list(request):
    drivers = Driver.objects.all()
    form = DriverForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('driver_list')
    return render(request, 'expenses/driver_list.html', {'drivers': drivers, 'form': form})

def vehicle_list(request):
    vehicles = Vehicle.objects.all()
    form = VehicleForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('vehicle_list')
    return render(request, 'expenses/vehicle_list.html', {'vehicles': vehicles, 'form': form})


