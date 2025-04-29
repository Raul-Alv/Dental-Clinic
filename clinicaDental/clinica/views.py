from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
# Create your views here.

from .forms import ProcedimientoForm
from .models import Procedimiento, Paciente, Practicante, Diente
from . import rdfConverter

def index(request):
    return HttpResponse("Hello, world. You're at the clinica index.")

def crearProcedimiento(request):
    if request.method == 'POST':
        form = ProcedimientoForm(request.POST)
        if form.is_valid():
            procedure = form.save(commit=False)
            procedure.id = Procedimiento.objects.count() + 1
            procedure.save()
            return redirect('procedimiento_list')
    else:
        form = ProcedimientoForm()
    return render(request, 'clinica/procedimiento_crear.html', {'form': form}) 

def procedimiento_list(request):
    procedimientos = Procedimiento.objects.all()
    return render(request, 'clinica/procedimiento_list.html', {'procedimientos': procedimientos})

def getProcedimiento(request, id):
    procedimiento = get_object_or_404(Procedimiento, id=id)
    return render(request, 'clinica/procedimiento_detail.html', {'procedimiento': procedimiento})

def updateProcedimiento(request, id):
    procedimiento = get_object_or_404(Procedimiento, id=id)
    if request.method == 'POST':
        form = ProcedimientoForm(request.POST, instance=procedimiento)
        if form.is_valid():
            form.save()
            return redirect('procedimiento_list')
    else:
        form = ProcedimientoForm(instance=procedimiento)
    return render(request, 'clinica/procedimiento_update.html', {'form': form, 'procedimiento': procedimiento})

def deleteProcedimiento(request, id):
    procedimiento = get_object_or_404(Procedimiento, id=id)
    print(procedimiento)
    if request.method == 'POST':
        procedimiento.delete()
        
        return redirect('procedimiento_list')
    return render(request, 'clinica/procedimiento_delete.html', {'procedimiento': procedimiento})
