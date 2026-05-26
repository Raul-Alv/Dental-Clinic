from django.db import models
import re

class Paciente(models.Model):
    GENERO_CHOICES = [
        ("male", "Masculino"),
        ("female", "Femenino"),
        ("other", "Otro"),
        ("unknown", "Desconocido"),
    ]
    ESTADO_CIVIL_CHOICES = [
        ("A", "Anulado"),
        ("D", "Divorciado"),
        ("M", "Casado"),
        ("U", "Soltero"),
        ("W", "Viudo/a"),
        ("UNK", "Desconocido"),
    ]
    GENERO_NORMALIZATION = {
        "m": "male",
        "male": "male",
        "masculino": "male",
        "f": "female",
        "female": "female",
        "femenino": "female",
        "o": "other",
        "other": "other",
        "otro": "other",
        "u": "unknown",
        "unk": "unknown",
        "unknown": "unknown",
        "desconocido": "unknown",
    }
    ESTADO_CIVIL_NORMALIZATION = {
        "a": "A",
        "annulled": "A",
        "anulado": "A",
        "anulada": "A",
        "d": "D",
        "divorced": "D",
        "divorciado": "D",
        "divorciada": "D",
        "c": "M",
        "m": "M",
        "married": "M",
        "casado": "M",
        "casada": "M",
        "s": "U",
        "u": "U",
        "single": "U",
        "soltero": "U",
        "soltera": "U",
        "w": "W",
        "v": "W",
        "widowed": "W",
        "viudo": "W",
        "viuda": "W",
        "unk": "UNK",
        "unknown": "UNK",
        "desconocido": "UNK",
    }

    id = models.AutoField(primary_key=True) #ID autoincremental
    activo = models.BooleanField(default=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    genero = models.CharField(max_length=10, choices=GENERO_CHOICES, blank=False, default='unknown')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField()
    calle = models.CharField(max_length=255, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)
    codigo_postal = models.CharField(max_length=20, blank=True, null=True)
    pais = models.CharField(max_length=100, blank=True, null=True)
    estado_civil = models.CharField(max_length=10, choices=ESTADO_CIVIL_CHOICES, default='UNK')
    #contacto = models.CharField(max_length=100, blank=True, null=True)

    @classmethod
    def normalizar_genero(cls, value):
        raw_value = str(value or "").strip().lower()
        return cls.GENERO_NORMALIZATION.get(raw_value, "unknown")

    @classmethod
    def normalizar_estado_civil(cls, value):
        raw_value = str(value or "").strip().lower()
        return cls.ESTADO_CIVIL_NORMALIZATION.get(raw_value, "UNK")

    @property
    def genero_label(self):
        genero_normalizado = self.normalizar_genero(self.genero)
        return dict(self.GENERO_CHOICES).get(genero_normalizado, "Desconocido")

    @property
    def estado_civil_label(self):
        estado_civil_normalizado = self.normalizar_estado_civil(self.estado_civil)
        return dict(self.ESTADO_CIVIL_CHOICES).get(estado_civil_normalizado, "Desconocido")

    def save(self, *args, **kwargs):
        self.genero = self.normalizar_genero(self.genero)
        self.estado_civil = self.normalizar_estado_civil(self.estado_civil)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
class Practicante(models.Model):
    id = models.AutoField(primary_key=True) #ID autoincremental
    activo = models.BooleanField(default=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    genero = models.CharField(max_length=10, choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')], blank=False, default='O')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    cualificacion = models.CharField(max_length=100) #Buscar como hacerlo más detallado

    def __str__(self):
        return f"{"Dr." if self.genero == "M" else "Dra."} {self.nombre} {self.apellido}"

class Diente(models.Model):
    codigo = models.CharField(max_length=7, unique=True) #Codigo basado en ADA SNOMED 
    display = models.CharField(max_length=100)
    definicion = models.CharField(max_length=100)
    designacion_universal = models.PositiveSmallIntegerField(null=True, blank=True) #Diente universal (1-32)
    designacion_iso = models.PositiveSmallIntegerField(null=True, blank=True) #Diente ISO (11-48)

    def __str__(self):
        return f"{self.display}"
    
    @classmethod
    def from_definicion_string(cls, definicion):
        """
        Parsea un string tipo:
          "Diente incisivo central inferior derecho permanente; \
           designación universal 25; designación ISO 41"
        y devuelve kwargs para crear la instancia.
        """
        

        text = definicion or ''
        parts = [p.strip() for p in text.split(';')]
        #print(f"Parsing definition: {text} -> Parts: {parts}")
        # Si hay al menos 3 secciones, extraemos
        #print(f"Parts found: {len(parts)} -> {parts}")
        if len(parts) >= 3:
            # 1) hasta el primer ';'
            defin = parts[0]
            print(f"Parsed definition: {defin}")
            # 2) número de designación universal
            m_u = re.search(r'(\d+)', parts[1])
            # 3) número de designación iso
            m_i = re.search(r'(\d+)', parts[2])
            #print(f"Parsed definition: {defin}, Universal: {m_u.group(1) if m_u else None}, ISO: {m_i.group(1) if m_i else None}")
            return {
                'definicion': defin,
                'designacion_universal': int(m_u.group(1)) if m_u else None,
                'designacion_iso': int(m_i.group(1))    if m_i else None,
            }

        # Fallback: lo guardamos todo en 'definicion'
        return {
            'definicion': text,
            'designacion_universal': None,
            'designacion_iso': None,
        }
    
class StatusProcedimiento(models.TextChoices):
    PREPARACION = 'preparation', 'Preparación'
    EN_PROGRESO = 'in-progress', 'En Progreso'
    NO_REALIZADO = 'not-done', 'No Realizado'
    EN_ESPERA = 'on-hold', 'En Espera'
    PARADO = 'stopped', 'Parado'
    COMPLETADO = 'completed', 'Completado'
    CON_ERRORES = 'entered-in-error', 'Con Errores'
    DESCONOCIDO = 'unknown', 'Desconocido'

class ProcedimientoCatalogo(models.Model):
    codigo = models.CharField(max_length=20, unique=True) #Codigo basado en SNOMED CT
    text = models.CharField(max_length=100, blank=True) #Texto descriptivo del procedimiento

    def __str__(self):
        return self.text
    
class Procedimiento(models.Model):
    id = models.AutoField(primary_key=True) #ID autoincremental
    status = models.CharField(max_length=20, choices=StatusProcedimiento.choices, default=StatusProcedimiento.PREPARACION)
    codigo = models.ForeignKey(ProcedimientoCatalogo, on_delete=models.PROTECT) #Codigo del procedimiento basado en SNOMED CT
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)
    practicante = models.ForeignKey(Practicante, on_delete=models.PROTECT)
    practicante_externo_uri = models.URLField(blank=True, null=True) #URI del practicante externo si aplica
    diente = models.ForeignKey(Diente, on_delete=models.PROTECT, blank=True, null=True) #Diente afectado por el procedimiento
    descripcion = models.CharField(max_length=100)
    realizado_el = models.DateField()
    
    def __str__(self):
        return f"{self.codigo.text} - {self.paciente.nombre}, {self.realizado_el}"
    

    
