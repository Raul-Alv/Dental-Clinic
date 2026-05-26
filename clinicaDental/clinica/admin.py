from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import CharWidget
from .models import Paciente, Practicante, Diente, Procedimiento, ProcedimientoCatalogo
from import_export.formats.base_formats import CSV

# 1. Resource para Diente
class DienteResource(resources.ModelResource):  
    # Este campo virtual lee la columna "definicion" de tu JSON
    code = fields.Field(attribute='codigo', column_name='code')
    display = fields.Field(attribute='display', column_name='display')
    definicion = fields.Field(attribute='definition', column_name='definition')

    class Meta:
        model = Diente
        # Claves únicas para identificar registros al hacer import
        import_id_fields = ('code', )
        # Columnas del archivo de importación que vas a procesar
        fields = (
            'code',
            'display',
            'definition',
            'designacion_universal',
            'designacion_iso',
        )

    def before_import_row(self, row, **kwargs):
        """
        Antes de importar cada fila:
        - Parseamos el texto 'definicion'
        - Rellenamos los campos reales en row
        """
        desc = row.get('definition', '')
        parsed = Diente.from_definicion_string(desc)
        #print(f"Parsed row: {parsed}")
        row['definition'] = parsed['definicion']
        row['designacion_universal'] = parsed['designacion_universal']
        row['designacion_iso'] = parsed['designacion_iso']


# 2. Admin personalizado para Diente
@admin.register(Diente)
class DienteAdmin(ImportExportModelAdmin):
    resource_class = DienteResource
    list_display = ('definicion', 'designacion_universal', 'designacion_iso')
    search_fields = ('definicion',)


class ProcedimientoCatalogoResource(resources.ModelResource):
    codigo = fields.Field(attribute='codigo', column_name='codigo', widget=CharWidget())
    text   = fields.Field(attribute='text',   column_name='text',   widget=CharWidget())

    class Meta:
        model            = ProcedimientoCatalogo
        import_id_fields = ('codigo',)
        fields           = ('codigo','text',)
    
    @classmethod
    def get_import_formats(cls):
        """
        Solo CSV (descarta XLS, JSON, etc.)
        """
        return [CSV()]

@admin.register(ProcedimientoCatalogo)
class CatalogoAdmin(ImportExportModelAdmin):
    resource_class = ProcedimientoCatalogoResource
    list_display   = ('codigo','text')
    search_fields  = ('codigo','text')

# 3. Registro genérico para los demás modelos
admin.site.register(Paciente)
admin.site.register(Practicante)
admin.site.register(Procedimiento)