from django.db import models

# Create your models here.
class Paciente(models.Model):
    activo = models.BooleanField(default=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    genero = models.CharField(max_length=10, choices=[('M', 'Masculino'), ('F', 'Femenino')])
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
class Practicante(models.Model):
    activo = models.BooleanField(default=True)
    tratamiento = models.CharField(max_length=10, choices=[('Dr.', 'Doctor'), ('Dra.', 'Doctora')])
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cualificacion = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.tratamiento} {self.nombre} {self.apellido}"

class Diente(models.Model):
    codigo = models.CharField(max_length=7, unique=True) #Codigo basado en ADA SNOMED 
    display = models.CharField(max_length=100)
    definicion = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.display}"
    
class Procedimiento(models.Model):
    codigo = models.CharField(max_length=10, unique=True) #Codigo basado en SNOMED CT
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    practicante = models.ForeignKey(Practicante, on_delete=models.CASCADE)
    diente = models.ForeignKey(Diente, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=100)
    realizado_el = models.DateField()
    

    def __str__(self):
        return f"{self.paciente.nombre} - {self.diente.display}, {self.realizado_el}"