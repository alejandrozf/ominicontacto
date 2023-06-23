const path = require('path');

function getCsfrToken (cookie) {
    const arr = cookie.split(';');
    for (const a in arr) {
        if (arr[a].search('csrftoken=') !== -1) {
            return arr[a].replace('csrftoken=', '');
        }
    }
}

function getPageConfig (pageName) {
    return {
        entry: 'src/main.js',
        template: `public/${pageName}.html`,
        filename: `${pageName}.html`,
        title: pageName,
        chunks: ['chunk-vendors', 'chunk-common', pageName]
    };
}

module.exports = {
    chainWebpack: (config) => {
        config.resolve.alias.set('@assets', path.resolve(__dirname, 'src/assets'));
    },
    publicPath: '/static/omnileads-ui-supervision/',
    pages: {
        supervision_dashboard: getPageConfig('supervision_dashboard'),
        security_audit: getPageConfig('security_audit'),
        add_agents_to_campaign: getPageConfig('add_agents_to_campaign'),
        pause_sets: getPageConfig('pause_sets'),
        external_sites: getPageConfig('external_sites'),
        external_site_authentications: getPageConfig('external_site_authentications'),
        call_dispositions: getPageConfig('call_dispositions'),
        external_systems: getPageConfig('external_systems'),
        forms: getPageConfig('forms'),
        pauses: getPageConfig('pauses'),
        inbound_routes: getPageConfig('inbound_routes'),
        outbound_routes: getPageConfig('outbound_routes'),
        group_of_hours: getPageConfig('group_of_hours'),
        ivrs: getPageConfig('ivrs'),
        register_server: getPageConfig('register_server')
    },
    devServer: {
        contentBase: './src/assets',
        proxy: {
            '/api': {
                target: 'https://nginx',
                ws: false,
                changeOrigin: true,
                logLevel: 'debug',
                secure: false,
                bypass: (req) => {
                    if (req.headers && req.headers.referer) {
                        req.headers['X-CSRFToken'] = getCsfrToken(req.headers.cookie);
                    }
                }
            },
            '/media': {
                target: 'https://nginx',
                changeOrigin: true
            }
        }
    }
};
