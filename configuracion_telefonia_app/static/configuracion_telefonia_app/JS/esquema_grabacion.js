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

// Adiciona tooltip sobre campo de id agente

$(function () {
    $('#id_id_agente').tooltip({'trigger':'focus', 'title': gettext('Atención: el ID de Agente como variable no está disponible para campañas Entrantes ni Salientes de Discador')});
});
