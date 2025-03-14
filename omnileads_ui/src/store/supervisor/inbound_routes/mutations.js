export default {
    initInboundRoutes (state, inboundRoutes) {
        state.inboundRoutes = inboundRoutes;
    },
    initInboundRoutesDestinations (state, destinations) {
        state.destinations = destinations;
    },
    initInboundRoutesLanguages (state, languages) {
        state.languages = languages;
    },
    initInboundRouteDetail (state, inboundRoute) {
        state.inboundRouteDetail = inboundRoute;
    },
    initInboundRouteForm (state, inboundRoute) {
        if (inboundRoute === null) {
            state.inboundRouteForm = {
                id: null,
                nombre: '',
                telefono: '',
                prefijo_caller_id: '',
                idioma: null,
                destino: null,
                tipo_destino: null
            };
        } else {
            state.inboundRouteForm = {
                id: inboundRoute.id,
                nombre: inboundRoute.nombre,
                telefono: inboundRoute.telefono,
                prefijo_caller_id: inboundRoute.prefijo_caller_id,
                idioma: inboundRoute.idioma,
                destino: inboundRoute.destino.id,
                tipo_destino: inboundRoute.destino.tipo
            };
        }
    }
};
