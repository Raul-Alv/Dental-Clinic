from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db.models import Q
from rdflib import Graph
# Create your views here.

from .forms import ProcedimientoForm, PacienteForm, PracticanteForm, RDFUploadForm
from .models import Procedimiento, Paciente, Practicante, Diente
from . import rdfConverter
import json, re
from bs4 import BeautifulSoup

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
    return render(request, 'clinica/procedimientos/procedimiento_crear.html', {'form': form}) 

def procedimiento_list(request):
    procedimientos = Procedimiento.objects.filter(
        Q(paciente__activo=True), Q(practicante__activo=True))
    return render(request, 'clinica/procedimientos/procedimiento_list.html', {'procedimientos': procedimientos})

def getProcedimiento(request, id):
    procedimiento = get_object_or_404(Procedimiento, id=id)
    return render(request, 'clinica/procedimientos/procedimiento_detail.html', {'procedimiento': procedimiento})

def updateProcedimiento(request, id):
    procedimiento = get_object_or_404(Procedimiento, id=id)
    if request.method == 'POST':
        form = ProcedimientoForm(request.POST, instance=procedimiento)
        if form.is_valid():
            form.save()
            return redirect('procedimiento_list')
    else:
        form = ProcedimientoForm(instance=procedimiento)
    return render(request, 'clinica/procedimientos/procedimiento_update.html', {'form': form, 'procedimiento': procedimiento})

def deleteProcedimiento(request, id):
    procedimiento = get_object_or_404(Procedimiento, id=id)
    print(procedimiento)
    if request.method == 'POST':
        procedimiento.delete()
        
        return redirect('procedimiento_list')
    return render(request, 'clinica/procedimientos/procedimiento_delete.html', {'procedimiento': procedimiento})

def import_data(request):
    if request.method == 'POST':
        form = RDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            rdfConverter.import_data(request, form)
            return redirect('procedimiento_list')
    else:
        form = RDFUploadForm()

    return render(request, 'clinica/import.html', {'form': form })

def patient_export_view(request):
    pacientes = Paciente.objects.all()
    selected_id = request.GET.get("paciente")
    
    procedimientos = []
    paciente = None

    if selected_id:
        paciente = get_object_or_404(Paciente, id=selected_id)
        procedimientos = Procedimiento.objects.filter(paciente=paciente)

    return render(request, "clinica/export_historial.html", {
        "pacientes": pacientes,
        "procedimientos": procedimientos,
        "selected_paciente": paciente
    })


def crearPaciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save(commit=False)
            paciente.id = Paciente.objects.count() + 1
            paciente.activo = True  
            paciente.save()
            return redirect('pacientes_list')
    else:
        form = PacienteForm()
    return render(request, 'clinica/pacientes/pacientes_crear.html', {'form': form})


def paciente_list(request):
    pacientes = Paciente.objects.filter(activo=True)
    return render(request, 'clinica/pacientes/pacientes_list.html', {'pacientes': pacientes})

def getPaciente(request, id):
    paciente = get_object_or_404(Paciente, id=id)
    return render(request, 'clinica/pacientes/pacientes_detail.html', {'paciente': paciente})

def paciente_update(request, id):
    paciente = get_object_or_404(Paciente, id=id)
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('pacientes_list')
    else:
        form = PacienteForm(instance=paciente)
    return render(request, 'clinica/pacientes/pacientes_update.html', {'form': form, 'paciente': paciente})

def paciente_delete(request, id):
    paciente = get_object_or_404(Paciente, id=id)
    if request.method == 'POST':
        paciente.activo = False
        paciente.save()
        return redirect('pacientes_list')
    return render(request, 'clinica/pacientes/pacientes_delete.html', {'paciente': paciente})

def crearPracticante(request):
    if request.method == 'POST':
        form = PracticanteForm(request.POST)
        if form.is_valid():
            practicante = form.save(commit=False)
            practicante.id = Practicante.objects.count() + 1
            practicante.activo = True  
            practicante.save()
            return redirect('practicantes_list')
    else:
        form = PracticanteForm()
    return render(request, 'clinica/practicantes/practicantes_crear.html', {'form': form})


def practicante_list(request):
    practicantes = Practicante.objects.filter(activo=True)
    return render(request, 'clinica/practicantes/practicantes_list.html', {'practicantes': practicantes})

def getPracticante(request, id):
    practicante = get_object_or_404(Practicante, id=id)
    return render(request, 'clinica/practicantes/practicantes_detail.html', {'practicante': practicante})

def practicante_update(request, id):
    practicante = get_object_or_404(Practicante, id=id)
    if request.method == 'POST':
        form =PracticanteForm(request.POST, instance=practicante)
        if form.is_valid():
            form.save()
            return redirect('practicantes_list')
    else:
        form = PracticanteForm(instance=practicante)
    return render(request, 'clinica/practicantes/practicantes_update.html', {'form': form, 'practicante': practicante})

def practicante_delete(request, id):
    practicante = get_object_or_404(Practicante, id=id)
    if request.method == 'POST':
        practicante.activo = False
        practicante.save()
        return redirect('practicantes_list')
    return render(request, 'clinica/practicantes/practicantes_delete.html', {'practicante': practicante})