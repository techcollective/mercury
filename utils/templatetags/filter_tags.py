from django import template

from django.utils.text import capfirst

register = template.Library()


class TitleNode(template.Node):
    def render(self, context):
        title = context["title"]
        if title.endswith(" by"):
            title = capfirst(title)
        else:
            title = "By " + title
        context["title"] = title
        return ""

@register.tag
def set_filter_title(parser, token):
    return TitleNode()
