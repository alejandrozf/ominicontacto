export default {
    initWhatsappProviders (state, providers) {
        state.supWhatsappProviders = providers;
    },
    initWhatsappProvider (state, provider = null) {
        if (provider) {
            state.supWhatsappProvider = {
                id: provider.id,
                nombre: provider.nombre,
                tipo_proveedor: provider.tipo_proveedor,
                configuracion: provider.configuracion
            };
        } else {
            state.supWhatsappProvider = {
                id: null,
                nombre: '',
                tipo_proveedor: null,
                configuracion: null
            };
        }
    }
};
