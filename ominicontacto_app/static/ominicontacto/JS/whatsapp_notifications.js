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
/* global gettext */

const TITLE = {
    SUCCESS: gettext('¡Operación exitosa!'),
    ERROR: gettext('¡Operación erronea!'),
    WARNING: gettext('¡Advertencia!')
};

const ICON = {
    SUCCESS: 'success',
    ERROR: 'error',
    WARNING: 'warning',
    INFO: 'info'
};


const fireNotification = async (text, title = 'SUCCESS', icon = 'SUCCESS') => {
    try {
        // eslint-disable-next-line no-undef
        await Swal.fire({
            title: TITLE[title],
            icon: ICON[icon],
            text,
            timer: 5000,
            showConfirmButton: false,
            showCloseButton: true,
            position: 'top-end',
            toast: true
        });
    } catch (error) {
        console.error('===> ERROR: Swal Notification');
        console.error(error);
    }
};

const onWhatsappNotificationEvent = async ($event) => {
    const { title, text, icon } = $event.detail;
    await fireNotification(text, title, icon);
};

$(function () {
    // Whatsapp Notification Events
    window.document.addEventListener('onWhatsappNotificationEvent', onWhatsappNotificationEvent, false);
});