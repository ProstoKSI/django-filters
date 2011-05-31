from functools import wraps

from django.utils.decorators import available_attrs
from django.template.loader import render_to_string
from django.template.response import RequestContext, SimpleTemplateResponse


class BasicWidget(object):
    render_template = 'filters/widget.html'

    def __init__(self, extra={}, template=None):
        self.template = template if template else self.render_template
        self.extra = extra

    def render(self, request):
        return render_to_string(self.template, self.extra, context_instance=RequestContext(request))

    def modify_queryset(self, request, queryset, data):
        return queryset


class ContainerWidget(BasicWidget):

    def __init__(self, widgets, extra={}, template=None):
        super(ContainerWidget, self).__init__(extra, template)
        self.widgets = widgets

    def render(self, request):
        rendered = []
        for widget in self.widgets:
            rendered.append((widget, widget.render(request)))
        self.extra['widgets'] = rendered
        return super(ContainerWidget, self).render(request)

    def modify_queryset(self, request, queryset, data):
        for widget in self.widgets:
            queryset = widget.modify_queryset(request, queryset, data)
        return queryset


class SortWidget(BasicWidget):
    render_template = 'filters/sort_widget.html'
    sort_variable = 'sort'

    def __init__(self, params, default, extra={}, template=None, sort_variable=None):
        super(SortWidget, self).__init__(extra, template)
        self.sort_var = sort_variable if sort_variable else self.sort_variable
        self.params = params
        self.default = default
        self.extra['sort_params'] = self.params
        self.extra['sort_default'] = self.default

    def modify_queryset(self, request, queryset, data):
        sort = data.get(self.sort_var, self.default)
        if sort not in self.params:
            sort = self.default
        self.extra['sort_current'] = sort
        ordering = self.params[sort][0]
        if callable(ordering):
            return ordering(queryset)
        return queryset.order_by(ordering).distinct()


class BaseFilterWidget(BasicWidget):
    render_template = 'filters/filter_widget.html'

    def __init__(self, name, default, extra={}, template=None):
        super(BaseFilterWidget, self).__init__(extra, template)
        self.name = name
        self.default = default
        self.extra['name'] = self.name
        self.extra['default'] = default

    def get_current_state(self, request, data):
        return data.get(self.name, self.default)

    def filter_queryset(self, request, queryset, state):
        return queryset

    def modify_queryset(self, request, queryset, data):
        state = self.get_current_state(request, data)
        return self.filter_queryset(request, queryset, state)


class FieldFilterWidget(BaseFilterWidget):
    render_template = 'filters/field_filter.html'

    def __init__(self, name, default, field_name, field_id, extra={}, template=None):
        super(FieldFilterWidget, self).__init__(name, default, extra, template)
        self.field_name = field_name
        self.field_id = field_id

    def filter_queryset(self, request, queryset, state):
        # TODO: This stuff is temprorary, while I'll figure out how it should be
        field = queryset.model.__dict__[self.field_name].field
        parent_model = field.related.parent_model
        self.extra['choices'] = parent_model.objects.filter(**{field.related_query_name() + '__in': queryset}).distinct()
        if state:
            return queryset.filter(**{self.field_name + '__' + self.field_id: state})
        return queryset


class OneChooseFilterWidget(BasicWidget):
    render_template = 'filters/one_choose_filter.html'


class ManyChooseFilterWidget(BasicWidget):
    render_template = 'filters/many_choose_filter.html'


class AnyFilterWidget(BasicWidget):
    render_template = 'filters/any_filter.html'


    def __init__(self, params, extra={}, template=None):
        super(AnyFilterWidget, self).__init__(extra, template)
        self.params = params
        self.extra['filter_params'] = self.params


    def modify_queryset(self, request, queryset, data):
        return queryset


class FilterContainerWidget(ContainerWidget):
    render_template = 'filters/filter_container.html'


FILTER_TYPES = {
    'field': FieldFilterWidget,
    'one_choose': OneChooseFilterWidget,
    'simple': OneChooseFilterWidget,
    'many_choose': ManyChooseFilterWidget,
    'any': AnyFilterWidget,
}

def generate_filter(conf):
    filter_type = conf.pop('type', 'simple')
    if filter_type in FILTER_TYPES:
        return FILTER_TYPES[filter_type](**conf)
    return None

def generate_modifiers(conf):
    result = {}
    if 'sort' in conf:
        result['sort'] = SortWidget(**conf['sort'])
    if 'filter' in conf:
        result['filters'] = generate_filter(conf['filter'])
    if 'filters' in conf:
        filters = []
        for filter in conf['filters']:
            filters.append(generate_filter(filter))
        result['filters'] = FilterContainerWidget(filters)
    return result

