const path = require("path");
module.exports = {
    publicPath: '/static/omnileads-ui-supervision/',
    devServer: {
        proxy: {
            '/api': {
                target: 'https://nginx',
                ws: false,
                changeOrigin: true,
                logLevel: 'debug',
                secure: false,
                bypass: (req, res) => {
                    if (req.headers && req.headers.referer) {
                        req.headers['X-CSRFToken'] = getCsfrToken(req.headers.cookie)
                    }
                    console.log(req.headers)
                },
            },
            '/media': {
                target: 'https://nginx',
                changeOrigin: true

            },
        }
    }
}

function getCsfrToken(cookie) {
    let arr = cookie.split(';');
    for (const a in arr) {
        if (arr[a].search('csrftoken=') != -1) {
            return arr[a].replace('csrftoken=', '')
        }
    }
}
