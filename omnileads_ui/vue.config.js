const path = require('path');
function getCsfrToken (cookie) {
    const arr = cookie.split(';');
    for (const a in arr) {
        if (arr[a].search('csrftoken=') !== -1) {
            return arr[a].replace('csrftoken=', '');
        }
    }
}

const historyApiFallback = {
    rewrites: [],
    verbose: true,
}

const publicPath = process.env.VUE_APP_PUBLIC_PATH || '/static/omnileads-frontend/';

function getPageConfig (pageName) {
    historyApiFallback.rewrites.push({
        from: new RegExp(`${publicPath}${pageName}/.+`),
        to: `${publicPath}${pageName}.html`
    })
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
    publicPath,
    lintOnSave: process.env.NODE_ENV !== 'production',
    pages: {
        // Supervisor Pages
        supervisor_supervision_dashboard: getPageConfig('supervisor_supervision_dashboard'),
        supervisor_security_audit: getPageConfig('supervisor_security_audit'),
        supervisor_add_agents_to_campaign: getPageConfig('supervisor_add_agents_to_campaign'),
        supervisor_pause_sets: getPageConfig('supervisor_pause_sets'),
        supervisor_external_sites: getPageConfig('supervisor_external_sites'),
        supervisor_external_site_authentications: getPageConfig('supervisor_external_site_authentications'),
        supervisor_call_dispositions: getPageConfig('supervisor_call_dispositions'),
        supervisor_external_systems: getPageConfig('supervisor_external_systems'),
        supervisor_forms: getPageConfig('supervisor_forms'),
        supervisor_pauses: getPageConfig('supervisor_pauses'),
        supervisor_inbound_routes: getPageConfig('supervisor_inbound_routes'),
        supervisor_outbound_routes: getPageConfig('supervisor_outbound_routes'),
        supervisor_group_of_hours: getPageConfig('supervisor_group_of_hours'),
        supervisor_ivrs: getPageConfig('supervisor_ivrs'),
        supervisor_register_server: getPageConfig('supervisor_register_server'),
        // Supervisor WhatsApp Pages
        supervisor_whatsapp_providers: getPageConfig('supervisor_whatsapp_providers'),
        supervisor_whatsapp_lines: getPageConfig('supervisor_whatsapp_lines'),
        supervisor_whatsapp_message_templates: getPageConfig('supervisor_whatsapp_message_templates'),
        supervisor_whatsapp_templates: getPageConfig('supervisor_whatsapp_templates'),
        supervisor_whatsapp_group_of_message_templates: getPageConfig('supervisor_whatsapp_group_of_message_templates'),
        supervisor_whatsapp_report_campaign_conversations: getPageConfig('supervisor_whatsapp_report_campaign_conversations'),
        supervisor_whatsapp_report_general: getPageConfig('supervisor_whatsapp_report_general'),
        // Agent Whatsapp Pages
        agent_whatsapp_index: getPageConfig('agent_whatsapp_index'),
        agent_whatsapp_conversation: getPageConfig('agent_whatsapp_conversation'),
        agent_whatsapp_conversation_new: getPageConfig('agent_whatsapp_conversation_new'),
        agent_whatsapp_templates: getPageConfig('agent_whatsapp_templates'),
        agent_whatsapp_disposition_chat: getPageConfig('agent_whatsapp_disposition_chat'),
        agent_whatsapp_message_transfer: getPageConfig('agent_whatsapp_message_transfer'),
        agent_whatsapp_image_uploader: getPageConfig('agent_whatsapp_image_uploader'),
        agent_whatsapp_file_uploader: getPageConfig('agent_whatsapp_file_uploader'),
        agent_whatsapp_contact_form: getPageConfig('agent_whatsapp_contact_form')
    },
    devServer: {
        historyApiFallback,
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
        },
        public: 'localhost',
        sockPath: `${publicPath}sockjs-node`,
        disableHostCheck: true,
        overlay: {
            warnings: true,
            errors: true
        }
    }
};
