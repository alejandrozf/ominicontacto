export default {
    initPauses (state, pauses) {
        state.pauses = pauses;
    },
    initPauseDetail (state, pause) {
        state.pauseDetail = pause;
    },
    initPauseForm (state, pause) {
        if (pause === null) {
            state.pauseForm = {
                id: null,
                nombre: '',
                tipo: '',
                eliminada: false
            };
        } else {
            state.pauseForm = {
                id: pause.id,
                nombre: pause.nombre,
                tipo: pause.tipo,
                eliminada: pause.eliminada
            };
        }
    }
};
