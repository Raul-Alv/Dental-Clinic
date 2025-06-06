from django.urls import path
from . import views, rdfConverter


urlpatterns = [
    path("", views.index, name='index'),
    path("procedimiento/", views.procedimiento_list, name='procedimiento_list'),
    path("procedimiento/crear/", views.crearProcedimiento, name='procedimiento_crear'),
    path("procedimiento/<int:id>/", views.getProcedimiento, name='procedimiento_detail'),
    path("procedimiento/<int:id>/update/", views.updateProcedimiento, name='procedimiento_update'),
    path("procedimiento/<int:id>/delete/", views.deleteProcedimiento, name='procedimiento_delete'),
    path('procedimiento/export/rdf/', rdfConverter.export_procedimientos_rdf, name='procedimiento_export_rdf'),
    path("import/", views.import_data, name='import_data'),
    path("procedimiento/export", views.patient_export_view, name="export_procedures"),
    path("procedimiento/export/<int:paciente_id>", rdfConverter.export_patient_rdf, name="export_procedures"),

    path("paciente/crear/", views.crearPaciente, name='pacientes_crear'),
    path("paciente/", views.paciente_list, name='pacientes_list'),
    path("paciente/<int:id>/", views.getPaciente, name='paciente_detail'),
]