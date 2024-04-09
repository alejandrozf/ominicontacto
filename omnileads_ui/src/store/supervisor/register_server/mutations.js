export default {
    initRegisterServer (state, { registered = false, registerServer = null, adminName = '', isAdmin = false }) {
        state.registerServer = {
            name: registerServer ? registerServer.client : '',
            email: registerServer ? registerServer.email : '',
            password: registerServer ? registerServer.password : '',
            phone: registerServer ? registerServer.phone : ''
        };
        state.registerServerStatus = registered;
        state.registerServerAdminName = adminName;
        state.registerServerIsAdmin = isAdmin;
    }
};
