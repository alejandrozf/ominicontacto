/* Copyright (C) 2018 Freetech Solutions

 This file is part of OMniLeads

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see http://www.gnu.org/licenses/.

*/

class Timer {
  constructor (horas_id, minutos_id, segundos_id) {
    this.horas = 0;
    this.minutos = 0;
    this.segundos = 0;
    this.horasDOM = $('#' + horas_id);
    this.minutosDOM = $('#' + minutos_id);
    this.segundosDOM = $('#' + segundos_id);
    this.control = null;
    this._show_all();
  }

  start() {
    var self = this;
    if (this.control === null) {
      this.control = setInterval(function(){self._tic();}, 1000);
    }
    else { 
      // console.log('Se intento iniciar dos veces el Timer.')
      // console.log(this);
    }
  };

  stop() {
    clearInterval(this.control);
    this.control = null;
  };

  restart() {
    this.segundos = 0;
    this.minutos = 0;
    this.horas = 0;
    this._show_all();
  }

  get_time_str() {
    return this._prepend_0(this.horas) + ':' + this._prepend_0(this.minutos) + ':' + 
    this._prepend_0(this.segundos);
  }

  _tic() {
    // Incremento 1 segundo
    if (this.segundos < 59) {
      this.segundos++;
    }
    else {
      // Incremento 1 minuto
      this.segundos = 0;
      if (this.minutos < 59){
        this.minutos++;
      }
      else{
        // Incremento 1 hora
        this.minutos = 0;
        this.horas++
        this._show_horas();
      }
      this._show_minutos();
    }
    this._show_segundos();
  };

  _show_all() {
    this._show_segundos();
    this._show_minutos();
    this._show_horas();
  }

  _prepend_0(number) {
    return (number > 9)? String(number) : '0' + String(number);
  }

  _show_segundos() {
    this.segundosDOM.html(':' + this._prepend_0(this.segundos));
  }

  _show_minutos() {
    this.minutosDOM.html(':' + this._prepend_0(this.minutos));
  }

  _show_horas() {
    this.horasDOM.html(this._prepend_0(this.horas));
  }
}
