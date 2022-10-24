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
/*
 * Código js relacionado con vista de creación/modificación de un nodo de ruta entrante de tipo validación
   fecha/hora
 */

/* global nodosEntrantesCambioPorTipo */

var $tipoDestinoMatch = $('#tipoDestinoMatch');
var $destinoMatch = $('#destinoMatch');
var $tipoDestinoNoMatch = $('#tipoDestinoNoMatch');
var $destinoNoMatch = $('#destinoNoMatch');

// cuando se escoge un tipo de nodo destino se despliegan en el campo selector de destinos
// todos los nodos destinos de este tipo
nodosEntrantesCambioPorTipo($tipoDestinoMatch, $destinoMatch);
nodosEntrantesCambioPorTipo($tipoDestinoNoMatch, $destinoNoMatch);
