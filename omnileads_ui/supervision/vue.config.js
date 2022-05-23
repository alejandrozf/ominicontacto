function getCsfrToken (cookie) {
    const arr = cookie.split(';');
    for (const a in arr) {
        if (arr[a].search('csrftoken=') !== -1) {
            return arr[a].replace('csrftoken=', '');
        }
    }
}

module.exports = {
    publicPath: '/static/omnileads-ui-supervision/',
    pages: {
        supervision_dashboard: {
            entry: 'src/main.js',
            template: 'public/supervision_dashboard.html',
            filename: 'supervision_dashboard.html',
            title: 'supervision_dashboard',
            chunks: ['chunk-vendors', 'chunk-common', 'supervision_dashboard']
        },
        page_audit: {
            entry: 'src/main.js',
            template: 'public/audit.html',
            filename: 'audit.html',
            title: 'audit',
            chunks: ['chunk-vendors', 'chunk-common', 'page_audit']
        },
        add_agents_to_campaign: {
            entry: 'src/main.js',
            template: 'public/add_agents_to_campaign.html',
            filename: 'add_agents_to_campaign.html',
            title: 'add_agents_to_campaign',
            chunks: ['chunk-vendors', 'chunk-common', 'add_agents_to_campaign']
        },
        pause_sets: {
            entry: 'src/main.js',
            template: 'public/pause_sets.html',
            filename: 'pause_sets.html',
            title: 'pause_sets',
            chunks: ['chunk-vendors', 'chunk-common', 'pause_sets']
        }
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
