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
        page_dashboard: {
            entry: 'src/page_dashboard/main.js',
            template: 'public/index.html',
            filename: 'index.html',
            title: 'dashboard',
            chunks: ['chunk-vendors', 'chunk-common', 'page_dashboard']
        },
        page_audit: {
            entry: 'src/page_audit/main.js',
            template: 'public/audit.html',
            filename: 'audit.html',
            title: 'audit',
            chunks: ['chunk-vendors', 'chunk-common', 'page_audit']
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
