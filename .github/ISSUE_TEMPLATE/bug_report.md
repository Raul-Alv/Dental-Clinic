---
name: Bug report
about: Exportando RDF no permite el uso de predicados "complejos"
title: "[BUG]"
labels: bug
assignees: Raul-Alv

---

**Describe el bug**
A la hora de hacer el formato de exportación de los datos a RDF, se usa como ejemplo el proporcionado en la página de FHIR [Procedimiento de ejemplo](https://hl7.org/fhir/us/dental-data-exchange/Procedure-Oral-eval-example.ttl.html). Sin embargo, al usar los predicados como se usan en el ejemplo, la aplicación lanza el error: AttributeError at /clinica/procedimiento/export/rdf/
'URIRef' object has no attribute 'status'

**Como reproducir**
Un caso como ejemplo, en `export_procedimiento_rdf` la propiedad `status`
1. Cambiar el añadir al grafo la propiedad `status` de `FHIR.status` a `FHIR.Procedure.status`
2. En `urls.py`, cambiar la funcionalidad del botón de exportar a `export_procedimiento_rdf` si tiene otro valor
3. Entrar en la vista `clinica\procedimientos`
4. Pulsar el botón `Exportar`

**Comportamiento esperado**
El programa debería exportar y descargar un fichero `procedimiento.ttl` en el que la sintaxis es igual a la mostrada en el ejemplo de FHIR.
