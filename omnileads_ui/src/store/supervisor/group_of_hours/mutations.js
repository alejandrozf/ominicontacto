export default {
    initGroupOfHours (state, groupOfHours) {
        state.groupOfHours = groupOfHours;
    },
    initGroupOfHour (state, groupOfHour) {
        if (groupOfHour === null) {
            state.groupOfHour = {
                id: null,
                nombre: '',
                validaciones_de_tiempo: []
            };
        } else {
            state.groupOfHour = {
                id: groupOfHour.id,
                nombre: groupOfHour.nombre,
                validaciones_de_tiempo: groupOfHour.validaciones_de_tiempo
            };
        }
    },
    initTimeValidation (state, timeValidation) {
        if (timeValidation === null) {
            state.timeValidation = {
                id: null,
                tiempo_inicial: null,
                tiempo_final: null,
                dia_semana_inicial: null,
                dia_semana_final: null,
                dia_mes_inicio: null,
                dia_mes_final: null,
                mes_inicio: null,
                mes_final: null
            };
        } else {
            state.timeValidation = {
                id: timeValidation.id,
                tiempo_inicial: timeValidation.tiempo_inicial,
                tiempo_final: timeValidation.tiempo_final,
                dia_semana_inicial: timeValidation.dia_semana_inicial,
                dia_semana_final: timeValidation.dia_semana_final,
                dia_mes_inicio: timeValidation.dia_mes_inicio,
                dia_mes_final: timeValidation.dia_mes_final,
                mes_inicio: timeValidation.mes_inicio,
                mes_final: timeValidation.mes_final
            };
        }
    },
    addTimeValidation (state, timeValidation) {
        state.groupOfHour.validaciones_de_tiempo.push(timeValidation);
    },
    removeTimeValidation (state, timeValidation) {
        if (timeValidation.id) {
            state.groupOfHour.validaciones_de_tiempo = state.groupOfHour.validaciones_de_tiempo.filter(tv => tv.id !== timeValidation.id);
        } else {
            state.groupOfHour.validaciones_de_tiempo = state.groupOfHour.validaciones_de_tiempo.filter(
                tv => !(timeValidation.tiempo_inicial === tv.tiempo_inicial &&
                        timeValidation.tiempo_final === tv.tiempo_final &&
                        timeValidation.dia_semana_inicial === tv.dia_semana_inicial &&
                        timeValidation.dia_semana_final === tv.dia_semana_final &&
                        timeValidation.dia_mes_inicio === tv.dia_mes_inicio &&
                        timeValidation.dia_mes_final === tv.dia_mes_final &&
                        timeValidation.mes_inicio === tv.mes_inicio &&
                        timeValidation.mes_final === tv.mes_final));
        }
    },
    editTimeValidation (state, { oldTimeValidation, newTimeValidation }) {
        if (newTimeValidation.id) {
            state.groupOfHour.validaciones_de_tiempo.find(function (tv) {
                if (tv.id === newTimeValidation.id) {
                    tv.grupo_horario = newTimeValidation.grupo_horario;
                    tv.tiempo_inicial = newTimeValidation.tiempo_inicial;
                    tv.tiempo_final = newTimeValidation.tiempo_final;
                    tv.dia_semana_inicial = newTimeValidation.dia_semana_inicial;
                    tv.dia_semana_final = newTimeValidation.dia_semana_final;
                    tv.dia_mes_inicio = newTimeValidation.dia_mes_inicio;
                    tv.dia_mes_final = newTimeValidation.dia_mes_final;
                    tv.mes_inicio = newTimeValidation.mes_inicio;
                    tv.mes_final = newTimeValidation.mes_final;
                }
            });
        } else {
            state.groupOfHour.validaciones_de_tiempo.find(function (tv) {
                if (oldTimeValidation.tiempo_inicial === tv.tiempo_inicial &&
                    oldTimeValidation.tiempo_final === tv.tiempo_final &&
                    oldTimeValidation.dia_semana_inicial === tv.dia_semana_inicial &&
                    oldTimeValidation.dia_semana_final === tv.dia_semana_final &&
                    oldTimeValidation.dia_mes_inicio === tv.dia_mes_inicio &&
                    oldTimeValidation.dia_mes_final === tv.dia_mes_final &&
                    oldTimeValidation.mes_inicio === tv.mes_inicio &&
                    oldTimeValidation.mes_final === tv.mes_final) {
                    tv.tiempo_inicial = newTimeValidation.tiempo_inicial;
                    tv.tiempo_final = newTimeValidation.tiempo_final;
                    tv.dia_semana_inicial = newTimeValidation.dia_semana_inicial;
                    tv.dia_semana_final = newTimeValidation.dia_semana_final;
                    tv.dia_mes_inicio = newTimeValidation.dia_mes_inicio;
                    tv.dia_mes_final = newTimeValidation.dia_mes_final;
                    tv.mes_inicio = newTimeValidation.mes_inicio;
                    tv.mes_final = newTimeValidation.mes_final;
                }
            });
        }
    }
};
