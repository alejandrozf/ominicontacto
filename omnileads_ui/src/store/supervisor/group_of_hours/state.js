export default {
    groupOfHours: [],
    groupOfHour: {
        id: null,
        nombre: '',
        validaciones_de_tiempo: []
    },
    timeValidation: {
        id: null,
        tiempo_inicial: null,
        tiempo_final: null,
        dia_semana_inicial: null,
        dia_semana_final: null,
        dia_mes_inicio: null,
        dia_mes_final: null,
        mes_inicio: null,
        mes_final: null
    },
    weekdays: [
        { option: 'Lunes', value: 0 },
        { option: 'Martes', value: 1 },
        { option: 'Miércoles', value: 2 },
        { option: 'Jueves', value: 3 },
        { option: 'Viernes', value: 4 },
        { option: 'Sábado', value: 5 },
        { option: 'Domingo', value: 6 }
    ],
    months: [
        { option: 'Enero', value: 1 },
        { option: 'Febrero', value: 2 },
        { option: 'Marzo', value: 3 },
        { option: 'Abril', value: 4 },
        { option: 'Mayo', value: 5 },
        { option: 'Junio', value: 6 },
        { option: 'Julio', value: 7 },
        { option: 'Agosto', value: 8 },
        { option: 'Septiembre', value: 9 },
        { option: 'Octubre', value: 10 },
        { option: 'Noviembre', value: 11 },
        { option: 'Diciembre', value: 12 }
    ]
};
