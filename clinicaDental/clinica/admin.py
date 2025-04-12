from django.contrib import admin
from .models import Paciente, Practicante, Diente, Procedimiento

# Register your models here.
admin.site.register(Paciente)
admin.site.register(Practicante)
admin.site.register(Diente)
admin.site.register(Procedimiento)
