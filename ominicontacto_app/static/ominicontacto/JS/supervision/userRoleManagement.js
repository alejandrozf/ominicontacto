/* Copyright (C) 2018 Freetech Solutions
/* Copyright (C) 2018 Freetech Solutions

 This file is part of OMniLeads

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Lesser General Public License version 3, as published by
 the Free Software Foundation.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Lesser General Public License for more details.

 You should have received a copy of the GNU Lesser General Public License
 along with this program.  If not, see http://www.gnu.org/licenses/.

*/
/* global Mustache Urls gettext */

var role_manager = undefined;

$(function () {
    var permissions = JSON.parse($('#permisos').val());
    var roles = JSON.parse($('#roles').val());
    role_manager = new RoleManager(permissions, roles, templates);
});

class RoleManager {

    constructor (permissions, roles, templates) {
        var self = this;
        this.permissions = permissions;
        this.roles = roles;
        this.templates = templates;

        this.drawVisibleRolesOptions();
        this.drawRolesToApplyOptions();
        this.drawPermissions();

        $('#visible_roles').change(function () {self.updateVisibleRoles(); });
        $('#create_role_btn').click(function () {
            $('#modalCreateRole').modal('show');
        });
        $('#create_role_submit').click(function () {self.createRole();});
        $('#delete_role_submit').click(function () {self.deleteRole();});
        $('#apply_permissions_submit').click(function () {self.applyRolePermissions();});
    }

    getRoleById(role_id) {
        for (var i = this.roles.length - 1; i >= 0; i--) {
            if(this.roles[i].id == role_id) {
                return this.roles[i];
            }
        }
    }

    updateVisibleRoles() {
        $('table[id^=role_row_]').hide();
        var selected_visible = $('#visible_roles').val();
        if (selected_visible == null) return;
        for (var i = selected_visible.length - 1; i >= 0; i--) {
            var selected_role = selected_visible[i];
            this.showSelectedRole(selected_role);
        }
    }

    addRole(role){
        this.roles.push(role);
        this.drawVisibleRolesOption(role.id, role.name, $('#visible_roles'), true);
        this.drawRolesToApplyOption(role.id, role.name, $('#role_model'));
        this.updateVisibleRoles();
    }

    createRole() {
        var self = this;
        var name = $('#new_role_name').val();
        var URL = Urls.api_new_role();
        $.ajax({
            url: URL,
            type: 'POST',
            dataType: 'json',
            data: {name: name},
            success: function(data){
                if (data['status'] == 'OK') {
                    var role = data['role'];
                    role.is_immutable = false;
                    self.addRole(role);
                    alert(gettext('Se creó el rol: \n') + role.name);
                }
                else {
                    // Show error message
                    alert(gettext('No se pudo crear el rol: \n') + data['message']);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                alert(gettext('Error al crear nuevo Rol.'));
                console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
            }
        });
        $('#modalCreateRole').modal('hide');
    }

    deleteRole() {
        var self = this;
        var role_id = $('#role_to_delete').val();
        var role_name = this.getRoleById(role_id).name;
        var URL = Urls.api_delete_role();
        $.ajax({
            url: URL,
            type: 'POST',
            dataType: 'json',
            data: {role_id: role_id},
            success: function(data){
                if (data['status'] == 'OK') {
                    self.removeRole(role_id);
                    alert(gettext('Se eliminó el rol: ') + role_name);
                }
                else {
                    // Show error message
                    alert(gettext('No se pudo eliminar el rol: ') + role_name + '\n' + data['message']);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                alert(gettext('Error al eliminar Rol: ') + role_name);
                console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
            }
        });
        $('#modalDeleteRole').modal('hide');
    }

    removeRole(role_id) {
        $('#role_row_' + role_id).remove();
        $('#visible_roles').children().filter('[value=' + role_id + ']').remove();
        $('#role_model').children().filter('[value=' + role_id + ']').remove();
    }

    applyRolePermissions() {
        var target_role_id = $('#target_role').val();
        var role_model_id = $('#role_model').val();
        var action = $('#apply_action').val();
        var target_role = this.getRoleById(target_role_id);
        var role_model = this.getRoleById(role_model_id);
        if (action == 'mimic') {
            target_role.permissions = role_model.permissions.slice();
        }
        else {
            for (var permission_id of role_model.permissions) {
                if (target_role.permissions.indexOf(permission_id) == -1){
                    target_role.permissions.push(permission_id);
                }
            }
        }
        $('#modalApplyPermissions').modal('hide');
        this.updatePermissions(target_role);
    }

    /* View */
    drawVisibleRolesOptions() {
        var container = $('#visible_roles');
        for (var i = this.roles.length - 1; i >= 0; i--) {
            var role = this.roles[i];
            this.drawVisibleRolesOption(role.id, role.name, container, false);
        }
    }

    drawVisibleRolesOption(role_id, role_name, container, is_selected) {
        var selected = (is_selected)? 'selected': '';
        var option = Mustache.render(
            this.templates.visible_role_option, {role_id: role_id, role_name: role_name, selected: selected});
        $(container).append(option);
    }

    drawRolesToApplyOptions() {
        var container = $('#role_model');
        for (var i = this.roles.length - 1; i >= 0; i--) {
            var role = this.roles[i];
            this.drawRolesToApplyOption(role.id, role.name, container);
        }        
    }

    drawRolesToApplyOption(role_id, role_name, container) {
        var option = Mustache.render(
            this.templates.apply_role_option, {role_id: role_id, role_name: role_name});
        $(container).append(option);
    }

    drawPermissions() {
        var permissions_row = $('#permissions_row');
        for (var permission_id in this.permissions) {
            var permission = this.permissions[permission_id];
            var permission_cell = Mustache.render(
                this.templates.permission_cell, {'permission': permission});
            $(permissions_row).append(permission_cell);
        }
    }

    updatePermissions(role) {
        $('[permission_role="'+role.id+'"]').each(function() {
            var permission_id = Number($(this).attr('permission_id'));
            $(this).prop('checked', role.permissions.indexOf(permission_id) > -1);
        });
    }

    showSelectedRole(role_id) {
        var role_row_id = '#role_row_' + role_id;
        if ($(role_row_id).length > 0)
            $(role_row_id).show();
        else
            this.drawRoleColumn(role_id);
    }

    drawRoleColumn(role_id) {
        var role = this.getRoleById(role_id);
        var permissions_cells = '';
        var submenu = '';
        if (!role.is_immutable) {
            submenu = Mustache.render(this.templates.role_submenu, {role_id: role_id});
        }
        var disabled = (role.is_immutable)? 'disabled': '';

        for (var permission_id in this.permissions) {
            var permission = this.permissions[permission_id];
            var checked = (role.permissions.indexOf(Number(permission_id)) > -1)? 'checked': '';
            permissions_cells += Mustache.render(this.templates.permission_checkbox,
                {
                    role_id: role_id, permission: permission, permission_id: permission_id,
                    checked: checked , disabled: disabled
                });
        }
        var role_column = Mustache.render(
            this.templates.role_column,
            {
                role_id: role_id, role_name: role.name, permissions_cells: permissions_cells,
                submenu: submenu
            });
        $('#main_grid').append(role_column);

    }

    saveRole(role_id) {
        var permissions = $('[permission_role="' + role_id + '"]:checked').map(function() {
            return $(this).attr('permission_id');
        }).get();
        var role_name = role_manager.getRoleById(role_id).name;

        var URL = Urls.api_update_role_permissions();
        $.ajax({
            url: URL,
            type: 'POST',
            dataType: 'json',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify({role_id: role_id, permissions: permissions}),
            success: function(data){
                if (data['status'] == 'OK') {
                    alert(gettext('Se guardó el rol: ') + role_name);
                }
                else {
                    // Show error message
                    alert(gettext('No se pudo guardar el rol: ') + role_name + '\n' + data['message']);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                alert(gettext('Error al guardar Rol: ') + role_name);
                console.log(gettext('Error al ejecutar => ') + textStatus + ' - ' + errorThrown);
            }
        });
    }

}


function saveRole(role_id) {
    role_manager.saveRole(role_id);
}

function mimicRolePermissionsForm(role_id) {
    $('#modalApplyPermissions').modal('show');
    $('#apply_permissions_title').html(gettext('Imitar permisos de Rol'));
    
    $('#target_role').val(role_id);
    $('#apply_action').val('mimic');
}

function addRolePermissionsForm(role_id) {
    $('#modalApplyPermissions').modal('show');
    $('#apply_permissions_title').html(gettext('Agregar permisos de Rol'));
    
    $('#target_role').val(role_id);
    $('#apply_action').val('add');
}

function deleteRoleForm(role_id) {
    var role_name = role_manager.getRoleById(role_id).name;
    $('#role_to_delete').val(role_id);
    $('#delete_role_label').html(role_name);
    $('#modalDeleteRole').modal('show');
}

var templates = {
    visible_role_option: '<option value="{{ role_id }}" {{ selected }}>{{ role_name }}</option>',
    
    apply_role_option: '<option value="{{ role_id }}">{{ role_name }}</option>',
    
    permission_cell: '<tr><td>{{ permission }}</td></tr>',
    
    role_column: 
    '<table class="table table-bordered"  id="role_row_{{ role_id }}">'+
    '  <thead><tr><td>{{ role_name }} {{{ submenu }}}</td></tr></thead>'+
    '  <tbody>{{{ permissions_cells }}}</tbody>'+
    '</table>',
    

    role_submenu: 
    '<a class="btn btn-secondary dropdown-toggle" href="#" role="button" id="dropdownRole{{ role_id }}" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"></a>' +
    '  <div class="dropdown-menu" aria-labelledby="dropdownRole{{ role_id }}">' +
    '    <a class="dropdown-item" href="javascript:" onclick="saveRole({{ role_id }})">Guardar</a>' +
    '    <a class="dropdown-item" href="javascript:" onclick="mimicRolePermissionsForm({{ role_id }})">Imitar permisos de..</a>' +
    '    <a class="dropdown-item" href="javascript:" onclick="addRolePermissionsForm({{ role_id }})">Aplicar permisos de..</a>' +
    '    <a class="dropdown-item" href="javascript:" onclick="deleteRoleForm({{ role_id }})">Eliminar</a>' +
    '  </div>',

    permission_checkbox:'<tr><td>'+
    '<input type="checkbox" permission_role="{{ role_id }}" name="{{ permission }}" permission_id="{{ permission_id }}" {{ checked }} {{disabled}}>'+
    '</td></tr>',
};
