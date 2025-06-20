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
    path("procedimiento/export/<int:procedimiento_id>/rdf", rdfConverter.export_procedimiento_rdf, name="export_procedure_rdf"),

    path("paciente/crear/", views.crearPaciente, name='pacientes_crear'),
    path("paciente/", views.paciente_list, name='pacientes_list'),
    path("paciente/<int:id>/", views.getPaciente, name='paciente_detail'),
    path("paciente/<int:id>/update/", views.paciente_update, name='paciente_update'),
    path("paciente/<int:id>/delete/", views.paciente_delete, name='paciente_delete'),
    path("paciente/<int:paciente_id>/export/rdf/", rdfConverter.export_patient_rdf, name='exportar_paciente'),


    path("practicante/crear/", views.crearPracticante, name='practicantes_crear'),
    path("practicante/", views.practicante_list, name='practicantes_list'),
    path("practicante/<int:id>/", views.getPracticante, name='practicante_detail'),
    path("practicante/<int:id>/update/", views.practicante_update, name='practicante_update'),
    path("practicante/<int:id>/delete/", views.practicante_delete, name='practicante_delete'),

    path("historial/export", views.patient_export_view, name="export_historial"),
    path("historial/export/<int:paciente_id>", rdfConverter.build_patient_rdf, name="export_historial"),

    path("import/", views.import_data, name='import_data'),
]
