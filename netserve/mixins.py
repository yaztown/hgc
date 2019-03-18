'''
Created on Sunday 10/03/2019

@author: yaztown
'''

from .response import JsonResponse

class ContextMixin(object):
    """
    A default context mixin that passes the keyword arguments received by
    get_context_data as the template context.
    """

    def get_context_data(self, **kwargs):
        if 'view' not in kwargs:
            kwargs['view'] = self
        return kwargs


class JSONResponseMixin(object):
    """
    A mixin that can be used to render a template.
    """
    response_class = JsonResponse

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a response, using the `response_class` for this
        view, with a template rendered with the given context.

        If any keyword arguments are provided, they will be
        passed to the constructor of the response class.
        """
        return self.response_class(
            request=self.request,
            data=context,
            **response_kwargs
        )


class MultipleObjectMixin(ContextMixin):
    """
    A mixin for views manipulating multiple objects.
    """
    allow_empty = True
    queryset = None
    model = None
    context_object_name = None

    def get_queryset(self):
        """
        Return the list of items for this view.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        return self.__class__._get_instances()
    
    def get_allow_empty(self):
        """
        Returns ``True`` if the view should display empty lists, and ``False``
        if a 404 should be raised instead.
        """
        return self.allow_empty

    def get_context_object_name(self, object_list):
        """
        Get the name of the item to be used in the context.
        """
        if self.context_object_name:
            return self.context_object_name
        elif hasattr(object_list, 'model'):
            return '%s_list' % object_list.model._meta.model_name
        else:
            return None

    def get_context_data(self, **kwargs):
        """
        Get the context for this view.
        """
        queryset = kwargs.pop('object_list', self.object_list)
        context_object_name = self.get_context_object_name(queryset)
        context = {
            'object_list': queryset
        }
        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)
        return super(MultipleObjectMixin, self).get_context_data(**context)
