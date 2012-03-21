(function($){

/* didAddPopup requires django's RelatedObjectLookups.js */
function didAddPopup(win, newId, newRepr) {
    var name = windowname_to_id(win.name);
    $("#"+name).trigger('didAddPopup', [html_unescape(newId), html_unescape(newRepr)]);
    win.close();
}

$.handleResult = function (event, ui){
    input_id = event.target.id;
    $("#" + input_id + "_hidden").val(ui.item.pk);
    $("#" + input_id + "_val").val(ui.item.value);
    $("#" + input_id + "_clear").show();
    if ($(ui.item).attr("autofill") != undefined) {
        for (field in ui.item.autofill) {
            // this is to work with id's in inlines, which look like
            // id_invoiceentry_set-0-item, where the target field will
            // look like id_invoiceentry_set-0-cost.
            split = "-"
            replace = input_id.split(split);
            if (replace.length == 1){
                // this will deal with regular fields which look like
                // id_customer
                replace = "id_" + field
            }
            else {
                replace = replace.slice(0,-1);
                replace.push(field);
                replace = replace.join(split);
            }
            replace = "#" + replace;
            old_val = $(replace).val();
            new_val = ui.item.autofill[field];
            if (new_val === null){
                new_val = "";
            }
            if (old_val != new_val){
                $(replace).val(new_val);
                $(replace).effect("highlight", {}, 2000);
            }
        }
    }
}

$.handleChange = function (event, ui){
    val_id = this.id + "_val";
    // blank the input and hidden id fields if the value in the box
    // is invalid (it should match the value it was originally set to)
    if($("#" + val_id).val() != $(this).val()){
        hidden_id = this.id + "_hidden";
        clear_id = this.id + "_clear";
        $(this).val("");
        $(this).change();
        $("#" + hidden_id).val("");
        $("#" + val_id).val("");
        $("#" + clear_id).hide();
    }
}

$(document).ready(function(){
    // Mouseover effect for X
    $(".ajax-clearfield img").hover(function(){
        $(this).attr("src", "/media/img/deleteover.png");
    }, function(){
        $(this).attr("src", "/media/img/delete.png");
    });
    // Clicking on X clears the input
    $("body").delegate(".ajax-clearfield", "click", function(){
        input_id = this.id;
        input_id = input_id.replace("_clear", "");
        $("#" + input_id).val("");
        $("#" + input_id).change();
        $("#" + input_id + "_hidden").val("");
        $(this).hide();
    });
    // so that new items from + popups end up in the input
    $("body").delegate(".ajax-input", "didAddPopup", function(event, id, repr) {
        data = Object();
        data.item = Object();
        data.item.pk = id;
        data.item.value = repr;
        handleResult(event, data);
        $(event.target).val(data.item.value);
    });
    // Hide X's if the input box is empty
    $(".ajax-clearfield").each(function(){
        input_id = this.id;
        input_id = input_id.replace("_clear", "");
        if (! $("#" + input_id).val()){
            $(this).hide();
        }
    });
});
})(django.jQuery);
