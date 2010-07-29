#!/usr/bin/env python

from django.template import TemplateDoesNotExist
from django.template.loader import BaseLoader

from mercury.configuration.models import Template
from mercury.configuration.exceptions import BadConfiguration


class TemplateLoader(BaseLoader):
    is_usable = True

    def load_template_source(self, template_name, template_dirs=None):
        try:
            template = Template.objects.get(name=template_name)
        except Template.DoesNotExist:
            raise TemplateDoesNotExist("Couldn't find a template with name '%s'." % template_name)
        except Template.MultipleObjectsReturned:
            raise BadConfiguration("Multiple templates called '%s' found." % template_name)
        return (template.template, "mercury template %s (id=%s)" % (template_name, template.id))
