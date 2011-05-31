from django import template
from django.core.urlresolvers import reverse

register = template.Library()

SKIP_PAGINATION = True # When new filter adds\removes - remove page variable from GET, to jump to first page

@register.simple_tag
def query(GET, name, value, simple_query=True):
    result = u'?'
    if simple_query or name not in GET:
        result += name + u'=' + unicode(value)
    else:
        result += name + u'=' + GET[name] + "," + unicode(value)
    for get_name in GET:
        if name != get_name and (get_name != u"page" or not SKIP_PAGINATION):
            result += u'&' + get_name + u'=' + GET[get_name]
    return result

@register.simple_tag
def current_query(GET):
    result = u'?'
    for get_name in GET:
        result += u'&' + get_name + u'=' + GET[get_name]
    return result

@register.simple_tag
def remove_query(GET, name, value):
    result = u'?'
    for get_name in GET:
        if result != u'?':
            result += u'&'
        if name != get_name:
            if get_name != u"page" or not SKIP_PAGINATION:
                result += get_name + u'=' + GET[get_name]
        else:
            if ',' in GET[get_name]:
                result += get_name + u'=' + GET[get_name].replace(unicode(value)+',', '').replace(','+unicode(value), '')
    return result

def filter(request, name, objects, current, simple_query=True):
    items = []
    for index, value, count in objects:
        if (type(current) == type(index) and index == current) or (type(current) == list and index in current):
            items.append((request.path + remove_query(request.GET, name, index), value, count, True))
        else:
            items.append((request.path + query(request.GET, name, index, simple_query), value, count, False))
    return items

@register.inclusion_tag("search/filter_simple.html", takes_context = True)
def filter_simple(context, name, list, current):
    """
        Make simple filter (when you can choose only one object to filter)
        Usage: filter_simple [ name of variable in query ] [ list of objects you want to filter from ] [ current value ]
    """
    context['items'] = filter(context['request'], name, list, current)
    return context

@register.inclusion_tag("search/filter_complex.html", takes_context = True)
def filter_complex(context, name, list, current):
    """
        Make complex filter (when you can choose more than one object from list in one time)
        Usage: filter_complex [ name of variable in query ] [ list of objects you want to filter from ] [ current value ]
    """
    context['items'] = filter(context['request'], name, list, current, False)
    return context

@register.inclusion_tag("search/filter_current.html", takes_context = True)
def filter_current(context, name, list, current):
    """
        Rander current values for this filter
        Usage: filter_current [ name of variable in query ] [ list of objects from where you'll see current ] [ current value ]
    """
    context['var_name'] = name
    context['var_list'] = list
    context['var_current'] = current
    return context
    
@register.inclusion_tag("search/show_filters.html", takes_context = True)
def show_filters(context):
    return context

@register.inclusion_tag("search/show_current_filters.html", takes_context = True)
def show_current_filters(context):
    return context
    
@register.inclusion_tag("search/show_sort.html", takes_context = True)
def show_sort(context):
    return context
