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
    publicPath: '/static/omnileads-ui-supervision/',
    pages: {
        supervision_dashboard: getPageConfig('supervision_dashboard'),
        security_audit: getPageConfig('security_audit'),
        add_agents_to_campaign: getPageConfig('add_agents_to_campaign'),
        pause_sets: getPageConfig('pause_sets'),
        external_sites: getPageConfig('external_sites'),
        call_dispositions: getPageConfig('call_dispositions'),
        external_systems: getPageConfig('external_systems')
    },
    devServer: {
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
