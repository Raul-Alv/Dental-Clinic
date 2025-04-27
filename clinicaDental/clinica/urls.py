from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name='index'),
    path("procedimiento/", views.procedimiento_list, name='procedimiento_list'),
    path("procedimiento/crear/", views.crearProcedimiento, name='procedimiento_crear'),
    path("procedimiento/<int:id>/", views.getProcedimiento, name='procedimiento_detail'),
    path("procedimiento/<int:id>/update/", views.updateProcedimiento, name='procedimiento_update'),
    path("procedimiento/<int:id>/delete/", views.deleteProcedimiento, name='procedimiento_delete'),
]