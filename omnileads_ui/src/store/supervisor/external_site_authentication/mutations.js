export default {
    initExternalSiteAuthentications (state, sites) {
        state.externalSiteAuthentications = sites;
    },
    initExternalSiteAuthentication (state, siteAuthentication = null) {
        if (siteAuthentication) {
            state.externalSiteAuthentication = {
                id: siteAuthentication.id,
                nombre: siteAuthentication.nombre,
                url: siteAuthentication.url,
                username: siteAuthentication.username,
                password: siteAuthentication.password,
                campo_token: siteAuthentication.campo_token,
                duracion: siteAuthentication.duracion,
                campo_duracion: siteAuthentication.campo_duracion,
                token: siteAuthentication.token,
                expiracion_token: siteAuthentication.expiracion_token,
                ssl_estricto: siteAuthentication.ssl_estricto
            };
        } else {
            state.externalSiteAuthentication = {
                id: null,
                nombre: null,
                url: '',
                username: '',
                password: '',
                campo_token: 'token',
                campo_duracion: '',
                duracion: 0,
                token: null,
                expiracion_token: null,
                ssl_estricto: false
            };
        }
    }
};
