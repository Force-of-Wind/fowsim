import abc
import inspect

from django.apps import apps

from django.db import models


class AbstractModel(models.Model):
    class Meta:
        abstract = True

    @classmethod
    @abc.abstractmethod
    def get_cls(cls):
        """Returns Class object of the current Class"""

    @classmethod
    @abc.abstractmethod
    def get_type_choices(cls):
        """Call super().get_type_choices_from_cls(cls) with the concrete class"""

    @staticmethod
    def get_subclasses(cls, *args, **kwargs):
        for app_config in apps.get_app_configs():
            for app_model in app_config.get_models():
                model_classes = [c.__name__ for c in inspect.getmro(app_model)]
                if cls.__name__ in model_classes:
                    yield app_model

    @staticmethod
    def get_type_choices_from_cls(cls):
        # Finds all subclasses of the class extending AbstractModel for a choices dropdown
        query_filter = None
        for cls in cls.get_subclasses(cls):
            app_label, model = cls._meta.label_lower.split('.')
            current_filter = models.Q(app_label=app_label, model=model)

            if query_filter is None:
                query_filter = current_filter
            else:
                query_filter |= current_filter

        return query_filter


def listToChoices(inputs):
    return [(x, x) for x in inputs]
