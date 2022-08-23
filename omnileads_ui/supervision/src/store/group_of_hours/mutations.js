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
    editTimeValidation (state, timeValidation) {
        if (timeValidation.id) {
            state.groupOfHour.validaciones_de_tiempo.find(function (x) {
                if (x.id === timeValidation.id) {
                    x.grupo_horario = timeValidation.grupo_horario;
                    x.tiempo_inicial = timeValidation.tiempo_inicial;
                    x.tiempo_final = timeValidation.tiempo_final;
                    x.dia_semana_inicial = timeValidation.dia_semana_inicial;
                    x.dia_semana_final = timeValidation.dia_semana_final;
                    x.dia_mes_inicio = timeValidation.dia_mes_inicio;
                    x.dia_mes_final = timeValidation.dia_mes_final;
                    x.mes_inicio = timeValidation.mes_inicio;
                    x.mes_final = timeValidation.mes_final;
                }
            });
        } else {
            state.timeValidation.tiempo_inicial = timeValidation.tiempo_inicial;
            state.timeValidation.tiempo_final = timeValidation.tiempo_final;
            state.timeValidation.dia_semana_inicial = timeValidation.dia_semana_inicial;
            state.timeValidation.dia_semana_final = timeValidation.dia_semana_final;
            state.timeValidation.dia_mes_inicio = timeValidation.dia_mes_inicio;
            state.timeValidation.dia_mes_final = timeValidation.dia_mes_final;
            state.timeValidation.mes_inicio = timeValidation.mes_inicio;
            state.timeValidation.mes_final = timeValidation.mes_final;
        }
    }
};
