/* didAddPopup requires django's RelatedObjectLookups.js */
function didAddPopup(win, newId, newRepr) {
    var name = windowname_to_id(win.name);
    $("#"+name).trigger('didAddPopup', [html_unescape(newId), html_unescape(newRepr)]);
    win.close();
}

function handleResult(event, ui){
    input_id = event.target.id;
    $("#" + input_id + "_hidden").val(ui.item.pk);
    $("#" + input_id + "_val").val(ui.item.value);
    $("#" + input_id + "_clear").show();
    if ($(ui.item).attr("autofill") != undefined) {
        for (field in ui.item.autofill) {
            replace = input_id;
            replace = replace.split("-");
            replace = replace.slice(0,-1);
            replace.push(field);
            replace = replace.join("-");
            $("#" + replace).val(ui.item.autofill[field]);
        }
    }
}

function handleChange(event, ui){
    val_id = this.id + "_val";
    if($("#" + val_id).val() != $(this).val()){
        hidden_id = this.id + "_hidden";
        clear_id = this.id + "_clear";
        $(this).val("");
        $(this).change();
        $("#" + hidden_id).val("");
        $("#" + clear_id).hide();
    }
}

$(document).ready(function(){
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
