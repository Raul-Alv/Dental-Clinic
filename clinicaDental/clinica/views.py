from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
# Create your views here.

from .forms import ProcedimientoForm
from .models import Procedimiento, Paciente, Practicante, Diente

def index(request):
    return HttpResponse("Hello, world. You're at the clinica index.")

""" def crearProcedimiento(request):
    form = ProcedimientoForm()
    if request.method == 'POST':
        form = ProcedimientoForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse("Procedimiento creado con éxito.")
    return render(request, 'clinica/crear_procedimiento.html', {'form': form}) """

def procedimiento_list(request):
    procedimientos = Procedimiento.objects.all()
    print(procedimientos)
    return render(request, 'clinica/procedimiento_list.html', {'procedimientos': procedimientos})

def getProcedimiento(request, id):
    procedimiento = get_object_or_404(Procedimiento, id=id)
    return render(request, 'clinica/procedimiento_detail.html', {'procedimiento': procedimiento})