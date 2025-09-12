/* Copyright (C) 2025 Freetech Solutions

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

$(document).ready(function () {
    
    const $ubdForm = $('form#user-bulk-delete');
    const selectAllItemCheck = $('#_selected_item');
    
    selectAllItemCheck.on('click', function () {
        if (selectAllItemCheck.prop('checked')) {
            $('[name="_selected_item"]').prop('checked', true);
        } else {
            $('[name="_selected_item"]').prop('checked', false);
        }
    });

    $('.table').on('click', '[name="_selected_item"]', function () {
        if ($(this).prop('checked')) {
            if ($('[name="_selected_item"]:not(:checked)').length  !== 0) {
                selectAllItemCheck.prop('checked', false);
                selectAllItemCheck.prop('indeterminate', true);
            } else {
                selectAllItemCheck.prop('checked', true);
                selectAllItemCheck.prop('indeterminate', false);
            }
        } else {
            if ($('[name="_selected_item"]:checked').length !== 0) {
                selectAllItemCheck.prop('checked', false);
                selectAllItemCheck.prop('indeterminate', true);
            } else {
                selectAllItemCheck.prop('checked', false);
                selectAllItemCheck.prop('indeterminate', false);
            }
        }
    });

    $ubdForm.on('submit', function(event) {
        $ubdForm.remove('[name="id"]');
        const checked = $('[name="_selected_item"]:checked');
        if (checked.length) {
            checked.each(function() {
                $ubdForm.append(
                    $('<input type="hidden" name="id" />').attr('value', this.value)
                );
            });
        } else {
            event.preventDefault();
        }
    });

    try {
        const dtable = $('.table').DataTable();
        dtable.on('draw', function () {
            const {start, end} = dtable.page.info();
            const checked = $('[name="_selected_item"]:checked').length;
            if (checked === (end - start)) {
                selectAllItemCheck.prop('checked', true);
                selectAllItemCheck.prop('indeterminate', false);
            } else if (checked === 0) {
                selectAllItemCheck.prop('checked', false);
                selectAllItemCheck.prop('indeterminate', false);
            } else {
                selectAllItemCheck.prop('checked', false);
                selectAllItemCheck.prop('indeterminate', true);
            }
        });
    } catch (error) { /* */}
});
