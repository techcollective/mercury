import json

from django.contrib.admin import site
from django.db import models
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from ajax_select import get_lookup

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
        results.append(result)
    return HttpResponse(json.dumps(results))


@login_required
def add_popup(request,app_label,model):
    """ present an admin site add view, hijacking the result if its the dismissAddAnotherPopup js and returning didAddPopup """
    themodel = models.get_model(app_label, model)
    admin = site._registry[themodel]

    admin.admin_site.root_path = "/ajax_select/" # warning: your URL should be configured here. I should be able to auto-figure this out but ...

    response = admin.add_view(request,request.path)
    if request.method == 'POST':
        if response.content.startswith('<script type="text/javascript">opener.dismissAddAnotherPopup'):
            return HttpResponse( response.content.replace('dismissAddAnotherPopup','didAddPopup' ) )
    return response
