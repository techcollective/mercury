#!/usr/bin/env python

from django.template import TemplateDoesNotExist
from django.template.loader import BaseLoader

from configuration.models import PdfTemplate


class PdfTemplateLoader(BaseLoader):
    is_usable = True

    def load_template_source(self, template_name, template_dirs=None):
        try:
            template = PdfTemplate.objects.get(name=template_name)
        except PdfTemplate.DoesNotExist:
            raise TemplateDoesNotExist("Couldn't find a template with name '%s'" % template_name)
        return (template.template, "PdfTemplate object (name=%s, id=%s)" % (template_name, template.id))
