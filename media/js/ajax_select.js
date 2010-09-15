
/* didAddPopup requires django's RelatedObjectLookups.js */

function didAddPopup(win, newId, newRepr) {
    var name = windowname_to_id(win.name);
    $("#"+name).trigger('didAddPopup', [html_unescape(newId), html_unescape(newRepr)]);
    win.close();
}

function handleResult(event, ui){
    input_id = event.target.id;
    $("#" + input_id + "_hidden").val(ui.item.pk);
    $("#" + input_id).val(ui.item.value);
    $("#" + input_id + "_clear").show();
}

$(document).ready(function(){
    // Hide X's if the input box is empty
    $(".ajax-clearfield").each(function(){
        input_id = this.id;
        input_id = input_id.replace("_clear", "");
        if (! $("#" + input_id).val()){
            $(this).hide();
        }
    });
});
