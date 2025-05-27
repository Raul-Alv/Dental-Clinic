from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
# Create your views here.

from .forms import ProcedimientoForm
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