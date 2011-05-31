from functools import wraps

from django.utils.decorators import available_attrs
from django.template.response import SimpleTemplateResponse

from filters.widgets import generate_modifiers

def modify_queryset(conf, var_name='list'):
    """
        Example of usage:
        @to_template('template.html')
        @modify_queryset({
            'sort': {
                'list': {
                    'var1': ('var1', _('Var 1 up')),
                    'var1_rev': ('-var1', _('Var 1 down')),
                },
                'default': 'var1',
                'template': 'filters/sort_widget.html',
            },
            'filters': {},
        })
        def my_view(request):
            return {'list': MyModel.objects.all()}

        Better usage:
        @modify_queryset(settings.MYVIEW_CHANGE_VIEW)
        def my_view(request):
            return TemplateRender('template.html', {'list': MyModel.objects.all()})

        And somewhere in settings:
        MYVIEW_CHANGE_VIEW = {
            'sort': {
                'var_dict': {},
                'default': 'var1',
                'extra': {
                    'wtf': '1',
                },
                'template': 'filters/sort_widget.html',
            },
            'filters': {}
        }
    """
    modifiers = generate_modifiers(conf)
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            result = view_func(request, *args, **kwargs)
            if isinstance(result, dict) or isinstance(result, SimpleTemplateResponse):
                data = request.GET.copy()
                data.update(request.POST)
                rendered = {}
                context = result if isinstance(result, dict) else result.context_data
                for name, modifier in modifiers.items():
                    context[var_name] = modifier.modify_queryset(request, context[var_name], data)
                for name, modifier in modifiers.items():
                    rendered[name] = modifier.render(request)
                context['modifiers'] = rendered
            return result
        return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)
    return decorator

