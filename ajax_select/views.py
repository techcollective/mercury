from django.db import models
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder

from ajax_select import get_lookup

from mercury.admin import site

@login_required
def ajax_lookup(request, channel):
    """ this view supplies results for both foreign keys and many to many fields """

    # it should come in as GET unless global $.ajaxSetup({type:"POST"}) has been set
    # in which case we'll support POST
    query_param = "term"
    if request.method == "GET":
        # we could also insist on an ajax request
        if query_param not in request.GET:
            return HttpResponse('')
        query = request.GET[query_param]
    else:
        if query_param not in request.POST:
            return HttpResponse('')
        query = request.POST[query_param]

    lookup_channel = get_lookup(channel)

    instances = lookup_channel.get_query(query, request)

    results = []
    for item in instances:
        itemf = lookup_channel.format_item(item)
        resultf = lookup_channel.format_result(item)
        result = {"pk": unicode(item.pk),
                  "value": itemf,
                  "label": resultf,
                  }
        autofill  = lookup_channel.generate_autofill(item)
        if autofill:
            result.update({"autofill": autofill})
        results.append(result)
    return HttpResponse(DjangoJSONEncoder().encode(results))


@login_required
def add_popup(request, app_label,model):
    """ present an admin site add view, hijacking the result if its the dismissAddAnotherPopup js and returning didAddPopup """
    themodel = models.get_model(app_label, model)
    admin = site._registry[themodel]

    response = admin.add_view(request, request.path)
    if request.method == 'POST':
        if hasattr(response, "render"):
            # this is done because the response might be a TemplateResponse
            # to re-display the form with errors, and it's not legal to access
            # the content attribute before render() is called.
            response.render()
        if 'dismissAddAnotherPopup' in response.content:
            return HttpResponse(response.content.replace('dismissAddAnotherPopup','didAddPopup'))
    return response
