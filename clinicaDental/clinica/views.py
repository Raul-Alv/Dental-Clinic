from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db.models import Q
# Create your views here.

from .forms import ProcedimientoForm, PacienteForm
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
    if request.method == 'POST' and request.FILES['json_file']:
        json_file = request.FILES['json_file']
        data = json.load(json_file)
        """ for item in data:
            diente = Diente(
                codigo=item['title'],
                display=item['author'],
                definition=item['publication_year']
            )
            diente.save() """
        # Extract the HTML table
        html = data["text"]["div"]
        soup = BeautifulSoup(html, "html.parser")

        # Build a code → description map from the HTML table
        table_rows = soup.find_all("tr")
        description_map = {}
        for row in table_rows[1:]:  # skip header
            cells = row.find_all("td")
            if len(cells) >= 3:
                code = cells[0].text.strip()
                description = cells[2].text.strip()
                description_map[code] = description
        
        # Extract from compose.include
        entries = []
        for system in data.get("compose", {}).get("include", []):
            for concept in system.get("concept", []):
                code = concept["code"].strip()
                display = concept.get("display", "").strip()
                description = description_map.get(code, "")
                print(f"Code: {code}, Display: {display}, Description: {description}", end='\n')
                entries.append({
                    "code": code,
                    "display": display,
                    "description": description
                })
        # Save to the database
        for entry in entries:
            diente = Diente(
                codigo=entry['code'],
                display=entry['display'],
                definicion=entry['description']
            )
            #print(f"Saving Diente: {diente.codigo}, {diente.display}, {diente.definicion}")
            #diente.save()
        return redirect('procedimiento_list')
    return render(request, 'clinica/form.html')

def patient_export_view(request):
    pacientes = Paciente.objects.all()
    selected_id = request.GET.get("paciente")
    
    procedimientos = []
    paciente = None

    if selected_id:
        paciente = get_object_or_404(Paciente, id=selected_id)
        procedimientos = Procedimiento.objects.filter(paciente=paciente)

    return render(request, "clinica/export_procedures.html", {
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
            return redirect('procedimiento_list')
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