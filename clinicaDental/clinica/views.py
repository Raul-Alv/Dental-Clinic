from django.db.models import Q
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from . import rdfConverter
from .forms import PacienteForm, PracticanteForm, ProcedimientoForm, RDFUploadForm
from .models import Paciente, Practicante, Procedimiento


def _clinic_overview():
    procedimientos_activos = Procedimiento.objects.filter(
        Q(paciente__activo=True),
        Q(practicante__activo=True),
    ).select_related("codigo", "paciente", "practicante").order_by("-realizado_el")

    return {
        "pacientes_count": Paciente.objects.filter(activo=True).count(),
        "practicantes_count": Practicante.objects.filter(activo=True).count(),
        "procedimientos_count": procedimientos_activos.count(),
        "recent_procedimientos": procedimientos_activos[:3],
    }


def dashboard(request):
    context = {
        "title": "Panel Clinico | Dental Clinic",
        **_clinic_overview(),
    }
    return render(request, "clinica/index.html", context)


def crearProcedimiento(request):
    paciente_id = request.GET.get("paciente") or request.POST.get("paciente_context")
    if not paciente_id:
        return redirect("pacientes_list")

    paciente = get_object_or_404(Paciente, id=paciente_id, activo=True)

    if request.method == "POST":
        form = ProcedimientoForm(request.POST, paciente_fijado=paciente)
        if form.is_valid():
            procedure = form.save(commit=False)
            procedure.id = Procedimiento.objects.count() + 1
            procedure.paciente = paciente
            procedure.save()
            return redirect("paciente_detail", id=paciente.id)
    else:
        form = ProcedimientoForm(initial={"paciente": paciente}, paciente_fijado=paciente)

    return render(
        request,
        "clinica/procedimientos/procedimiento_crear.html",
        {"form": form, "paciente": paciente, "title": "Crear Procedimiento"},
    )


def procedimiento_list(request):
    return redirect("pacientes_list")


def getProcedimiento(request, id):
    procedimiento = get_object_or_404(Procedimiento, id=id)
    return render(
        request,
        "clinica/procedimientos/procedimiento_detail.html",
        {
            "procedimiento": procedimiento,
            "paciente": procedimiento.paciente,
            "title": "Detalle del Procedimiento",
        },
    )


def updateProcedimiento(request, id):
    procedimiento = get_object_or_404(Procedimiento, id=id)
    if request.method == "POST":
        form = ProcedimientoForm(
            request.POST,
            instance=procedimiento,
            paciente_fijado=procedimiento.paciente,
        )
        if form.is_valid():
            procedure = form.save()
            return redirect("paciente_detail", id=procedure.paciente_id)
    else:
        form = ProcedimientoForm(instance=procedimiento, paciente_fijado=procedimiento.paciente)

    return render(
        request,
        "clinica/procedimientos/procedimiento_update.html",
        {
            "form": form,
            "procedimiento": procedimiento,
            "paciente": procedimiento.paciente,
            "title": "Actualizar Procedimiento",
        },
    )


def deleteProcedimiento(request, id):
    procedimiento = get_object_or_404(Procedimiento, id=id)
    paciente_id = procedimiento.paciente_id
    if request.method == "POST":
        procedimiento.delete()
        return redirect("paciente_detail", id=paciente_id)

    return render(
        request,
        "clinica/procedimientos/procedimiento_delete.html",
        {"procedimiento": procedimiento, "title": "Eliminar Procedimiento"},
    )


def import_data(request):
    if request.method == "POST":
        form = RDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                rdfConverter.import_data(form)
            except ValidationError as exc:
                for error in exc.messages:
                    form.add_error(None, error)
            else:
                return redirect("pacientes_list")
    else:
        form = RDFUploadForm()

    return render(request, "clinica/import.html", {"form": form, "title": "Importar Datos RDF"})


def patient_export_view(request):
    pacientes = Paciente.objects.all()
    selected_id = request.GET.get("paciente")

    procedimientos = []
    paciente = None

    if selected_id:
        paciente = get_object_or_404(Paciente, id=selected_id)
        procedimientos = Procedimiento.objects.filter(paciente=paciente).select_related("codigo", "diente")

    return render(
        request,
        "clinica/export_historial.html",
        {
            "pacientes": pacientes,
            "procedimientos": procedimientos,
            "selected_paciente": paciente,
            "title": "Exportar Historial del Paciente",
        },
    )


def crearPaciente(request):
    if request.method == "POST":
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save(commit=False)
            paciente.activo = True
            paciente.save()
            return redirect("pacientes_list")
    else:
        form = PacienteForm()

    return render(request, "clinica/pacientes/pacientes_crear.html", {"form": form, "title": "Crear Paciente"})


def paciente_list(request):
    pacientes = Paciente.objects.filter(activo=True)
    return render(request, "clinica/pacientes/pacientes_list.html", {"pacientes": pacientes, "title": "Lista de Pacientes"})


def getPaciente(request, id):
    paciente = get_object_or_404(Paciente, id=id)
    procedimientos = Procedimiento.objects.filter(paciente=paciente).select_related(
        "codigo",
        "practicante",
        "diente",
    ).order_by("-realizado_el", "-id")
    return render(
        request,
        "clinica/pacientes/pacientes_detail.html",
        {
            "paciente": paciente,
            "procedimientos": procedimientos,
            "title": "Detalle del Paciente",
        },
    )


def paciente_update(request, id):
    paciente = get_object_or_404(Paciente, id=id)
    if request.method == "POST":
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect("pacientes_list")
    else:
        form = PacienteForm(instance=paciente)

    return render(
        request,
        "clinica/pacientes/pacientes_update.html",
        {"form": form, "paciente": paciente, "title": "Actualizar Paciente"},
    )


def paciente_delete(request, id):
    paciente = get_object_or_404(Paciente, id=id)
    if request.method == "POST":
        paciente.activo = False
        paciente.save()
        return redirect("pacientes_list")

    return render(
        request,
        "clinica/pacientes/pacientes_delete.html",
        {"paciente": paciente, "title": "Eliminar Paciente"},
    )


def crearPracticante(request):
    if request.method == "POST":
        form = PracticanteForm(request.POST)
        if form.is_valid():
            practicante = form.save(commit=False)
            practicante.id = Practicante.objects.count() + 1
            practicante.activo = True
            practicante.save()
            return redirect("practicantes_list")
    else:
        form = PracticanteForm()

    return render(
        request,
        "clinica/practicantes/practicantes_crear.html",
        {"form": form, "title": "Crear Practicante"},
    )


def practicante_list(request):
    practicantes = Practicante.objects.filter(activo=True)
    return render(
        request,
        "clinica/practicantes/practicantes_list.html",
        {"practicantes": practicantes, "title": "Lista de Practicantes"},
    )


def getPracticante(request, id):
    practicante = get_object_or_404(Practicante, id=id)
    return render(
        request,
        "clinica/practicantes/practicantes_detail.html",
        {"practicante": practicante, "title": "Detalle del Practicante"},
    )


def practicante_update(request, id):
    practicante = get_object_or_404(Practicante, id=id)
    if request.method == "POST":
        form = PracticanteForm(request.POST, instance=practicante)
        if form.is_valid():
            form.save()
            return redirect("practicantes_list")
    else:
        form = PracticanteForm(instance=practicante)

    return render(
        request,
        "clinica/practicantes/practicantes_update.html",
        {"form": form, "practicante": practicante, "title": "Actualizar Practicante"},
    )


def practicante_delete(request, id):
    practicante = get_object_or_404(Practicante, id=id)
    if request.method == "POST":
        practicante.activo = False
        practicante.save()
        return redirect("practicantes_list")

    return render(
        request,
        "clinica/practicantes/practicantes_delete.html",
        {"practicante": practicante, "title": "Eliminar Practicante"},
    )
