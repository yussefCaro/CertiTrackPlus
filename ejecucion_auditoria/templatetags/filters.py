from django import template
# No necesitas importar 'from django.conf import settings' ni 'make_absolute'
# si solo usas el simple tag 'absolute_uri'

register = template.Library()

# 1. Filtro 'split' (Tu función original)
@register.filter
def split(value, key=','):
    if value:
        return value.split(key)
    return []

# 2. Simple Tag 'absolute_uri' (La nueva función necesaria para el PDF)
@register.simple_tag(takes_context=True)
def absolute_uri(context, url):
    """Obtiene la URL absoluta usando el objeto request del contexto para que WeasyPrint pueda acceder a las imágenes."""
    request = context['request']
    if url:
        return request.build_absolute_uri(url)
    return ""