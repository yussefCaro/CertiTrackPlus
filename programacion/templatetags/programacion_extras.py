from django import template

register = template.Library()

@register.filter
def tiene_programacion_activa(programaciones):
    return programaciones.filter(estado__in=["En Curso", "Finalizada", "Cancelada"]).exists()
