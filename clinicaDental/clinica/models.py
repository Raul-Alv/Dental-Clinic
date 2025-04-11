from django.db import models

# Create your models here.
class Paciente(models.Model):
    activo = models.BooleanField(default=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    genero = models.CharField(max_length=10, choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')], blank=False, default='O')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField()
    direccion = models.CharField(max_length=255, blank=True, null=True)
    estado_civil = models.CharField(max_length=10, choices=[('S', 'Soltero'), ('C', 'Casado'), ('D', 'Divorciado')], default='S')
    #contacto = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
class Practicante(models.Model):
    activo = models.BooleanField(default=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    genero = models.CharField(max_length=10, choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')], blank=False, default='O')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    cualificacion = models.CharField(max_length=100) #Buscar como hacerlo más detallado

    def __str__(self):
        return f"{"Dr." if {self.genero == "Masculino"} else "Dra."} {self.nombre} {self.apellido}"

class Diente(models.Model):
    codigo = models.CharField(max_length=7, unique=True) #Codigo basado en ADA SNOMED 
    display = models.CharField(max_length=100)
    definicion = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.display}"
    
class StatusProcedimiento(models.TextChoices):
    PREPARACION = 'preparation', 'Preparación'
    EN_PROGRESO = 'in-progress', 'En Progreso'
    NO_REALIZADO = 'not-done', 'No Realizado'
    EN_ESPERA = 'on-hold', 'En Espera'
    PARADO = 'stopped', 'Parado'
    COMPLETADO = 'completed', 'Completado'
    CON_ERRORES = 'entered-in-error', 'Con Errores'
    DESCONOCIDO = 'unknown', 'Desconocido'
    
class Procedimiento(models.Model):
    codigo = models.CharField(max_length=10, unique=True) #Codigo basado en SNOMED CT
    status = models.CharField(max_length=20, choices=StatusProcedimiento.choices, default=StatusProcedimiento.PREPARACION)
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)
    practicante = models.ForeignKey(Practicante, on_delete=models.PROTECT)
    diente = models.ForeignKey(Diente, on_delete=models.PROTECT)
    descripcion = models.CharField(max_length=100)
    realizado_el = models.DateField()
    

    def __str__(self):
        return f"{self.paciente.nombre} - {self.diente.display}, {self.realizado_el}"
    
