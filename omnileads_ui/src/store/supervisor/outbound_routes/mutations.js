export default {
    initOutboundRoutes (state, outboundRoutes) {
        state.outboundRoutes = outboundRoutes;
    },
    initOutboundRoute (state, outboundRoute) {
        if (outboundRoute === null) {
            state.outboundRoute = {
                id: null,
                nombre: '',
                ring_time: 25,
                dial_options: 'Tt',
                troncales: [],
                patrones_de_discado: []
            };
        } else {
            state.outboundRoute = {
                id: outboundRoute.id,
                nombre: outboundRoute.nombre,
                ring_time: outboundRoute.ring_time,
                dial_options: outboundRoute.dial_options,
                troncales: outboundRoute.troncales,
                patrones_de_discado: outboundRoute.patrones_de_discado
            };
        }
    },
    initOutboundRouteSipTrunks (state, sipTrunks) {
        state.sipTrunks = sipTrunks;
    },
    initOutboundRouteOrphanTrunks (state, orphanTrunks) {
        state.orphanTrunks = orphanTrunks;
    },
    initDialPatternForm (state, dialPattern) {
        if (dialPattern === null) {
            state.dialPattern = {
                id: null,
                prepend: null,
                prefix: null,
                match_pattern: null
            };
        } else {
            state.dialPattern = {
                id: dialPattern.id,
                prepend: dialPattern.prepend,
                prefix: dialPattern.prefix,
                match_pattern: dialPattern.match_pattern
            };
        }
    },
    initTrunkForm (state, trunk) {
        if (trunk === null) {
            state.trunk = {
                id: null,
                troncal: null
            };
        } else {
            state.trunk = {
                id: trunk.id,
                troncal: trunk.troncal
            };
        }
    },
    addTrunk (state, trunk) {
        state.outboundRoute.troncales.push(trunk);
    },
    removeTrunk (state, trunkId) {
        state.outboundRoute.troncales = state.outboundRoute.troncales.filter(t => t.troncal !== trunkId);
    },
    addDialPattern (state, dialPattern) {
        state.outboundRoute.patrones_de_discado.push(dialPattern);
    },
    removeDialPattern (state, dialPattern) {
        if (dialPattern.id) {
            state.outboundRoute.patrones_de_discado = state.outboundRoute.patrones_de_discado.filter(pd => pd.id !== dialPattern.id);
        } else {
            state.outboundRoute.patrones_de_discado = state.outboundRoute.patrones_de_discado.filter(
                pd => !(pd.match_pattern === dialPattern.match_pattern && pd.prefix === dialPattern.prefix));
        }
    },
    editTrunk (state, trunk) {
        if (trunk.id) {
            state.outboundRoute.troncales.filter(function (t) {
                if (t.id === trunk.id) {
                    t.troncal = trunk.troncal;
                }
            });
        } else {
            state.outboundRoute.troncales.filter(function (t) {
                if (t.troncal === trunk.troncal) {
                    t.troncal = trunk.troncal;
                }
            });
        }
    },
    editDialPattern (state, dialPattern) {
        if (dialPattern.id) {
            state.outboundRoute.patrones_de_discado.filter(function (pd) {
                if (pd.id === dialPattern.id) {
                    pd.prepend = dialPattern.prepend;
                    pd.prefix = dialPattern.prefix;
                    pd.match_pattern = dialPattern.match_pattern;
                }
            });
        } else {
            state.outboundRoute.patrones_de_discado.filter(function (pd) {
                if (pd.match_pattern === state.dialPattern.match_pattern && pd.prefix === state.dialPattern.prefix) {
                    pd.prepend = dialPattern.prepend;
                    pd.prefix = dialPattern.prefix;
                    pd.match_pattern = dialPattern.match_pattern;
                }
            });
        }
    }
};
