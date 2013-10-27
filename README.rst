..   -*- mode: rst -*-

Django filters
=============

**Django filters** is module to provide filter and sorting for lists of objects. It's easily extandable system, that allows to configure which fields to use for filtering and sorting 
of your model.

Requirements
============

- python >= 2.5 (Python 3.x wasn't tested)
- django >= 1.2 (Tested with up to 1.6 version)

Installation
============

**Django filters** can be installed using pip: ::
    
    pip install git+git://github.com/ProstoKSI/django-filters.git

Setup
=====

Add 'filters' to INSTALLED_APPS: ::
    
    INSTALLED_APPS += ( 'filters', )

Use django-filters
==================

For example you have model ``Book``: ::

    class Book(models.Model):
        name = models.CharField(...)
        size = models.IntegerField(...)

then to make ``book_list`` view filterable and sortable, use next notation: ::
    
    from filters.decorators import modify_queryset

    import .settings as app_settings

    @modify_queryset(app_settings.BOOK_LIST_VIEW_FILTER)
    def book_list(request, template_name='books/book_list.html'):
        return TemplateRender(template_name, {'list': Book.objects.all()})
        
and in ``books/settings.py`` add next configuration for filtering: ::
   
    BOOK_LIST_VIEW_FILTER = {
        'sort':  {
            'list': {
                'name': ('name', _('By Name ascending')),
                'name_rev': ('-name', _('By Name descending')),
            },
            'default': 'name',
            'template': 'filters/sort_widget.html',
        },
        'filters': {
        }
    }

Contributing
============

Development of django-filters happens at github: https://github.com/ProstoKSI/django-filters

License
=======

Copyright (C) 2009-2013 ProstoKSI.
This program is licensed under the MIT License (see LICENSE)

