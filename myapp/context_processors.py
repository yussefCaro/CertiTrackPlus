# myapp/context_processors.py
def navigation_menu(request):
    """
    Context processor para manejar el menú de navegación
    según los grupos del usuario
    """
    context = {
        'show_comercial_menu': False,
        'show_cotizaciones': False,
        'show_programaciones': False,
        'show_auditores_menu': False,
    }

    if request.user.is_authenticated:
        user_groups = [group.name for group in request.user.groups.all()]

        # Verificar grupos y establecer las variables del menú
        if 'Comercial' in user_groups:
            context['show_comercial_menu'] = True
            context['show_cotizaciones'] = True

        if 'Programacion' in user_groups:
            context['show_programaciones'] = True
            # Solo mostrar cotizaciones si no es comercial también
            if 'Comercial' not in user_groups:
                context['show_cotizaciones'] = True

        if 'Auditores' in user_groups:
            context['show_auditores_menu'] = True

    return context
