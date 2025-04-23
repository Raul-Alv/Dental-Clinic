from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
# Create your views here.

from .forms import ProcedimientoForm
from .models import Procedimiento, Paciente, Practicante, Diente

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
    print(procedimientos)
    return render(request, 'clinica/procedimiento_list.html', {'procedimientos': procedimientos})

def getProcedimiento(request, id):
    procedimiento = get_object_or_404(Procedimiento, id=id)
    return render(request, 'clinica/procedimiento_detail.html', {'procedimiento': procedimiento})