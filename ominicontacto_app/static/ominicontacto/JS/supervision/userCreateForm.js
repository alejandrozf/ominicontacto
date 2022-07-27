(function () {
    var AGENTE_ROL_ID = document.currentScript.dataset.agenteRolId;
    $(function () {
        var email_field = $('#id_0-email');
        var email_label = email_field.prev('label');
        email_label.html(email_label.text().replace('*', '').trim() + '<b class="hidden" style="color:red"> *</b>');
        var rol_select = $('#id_0-rol');
        rol_select.change(on_rol_select_change);
        function on_rol_select_change() {
            if (rol_select.val() == AGENTE_ROL_ID) {
                email_field.prop('required', true);
                email_label.children('b').removeClass('hidden');
            } else {
                email_field.prop('required', false);
                email_label.children('b').addClass('hidden');
            }
        }
        on_rol_select_change();
    });
})();
