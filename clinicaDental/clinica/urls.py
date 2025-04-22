from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name='index'),
    path("procedimiento/", views.procedimiento_list, name='procedimiento_list'),
    #path("procedimiento/crear/", views.crearProcedimiento, name='crear_procedimiento'),
    #path("procedimiento/<int:id>/", views.getProcedimiento, name='get_procedimiento'),
]