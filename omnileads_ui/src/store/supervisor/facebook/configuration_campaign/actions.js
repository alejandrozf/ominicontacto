/* eslint-disable no-unused-vars */
import { HTTP_STATUS } from '@/globals';
import { TEMPLATE_TYPES } from '@/globals/supervisor/whatsapp';
import Service from '@/services/supervisor/whatsapp/templates_service';
const service = new Service();
const PARAMS_REGEX = /{{\d+}}/g;

export default {
    async initSupCampaignTemplates ({ commit }, { campaignId = null, lineId = null }) {
        try {
            commit('initSupCampaignTemplates', []);
            if (!campaignId) {
                commit('initSupCampaignTemplates', []);
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al obtener los templates'
                };
            }
            const response = await service.getTemplates(campaignId, lineId);
            const { status, data } = response;
            let templates = [];
            if (status === HTTP_STATUS.SUCCESS) {
                templates = data.message_templates || [];
                if (lineId) {
                    templates = templates.concat(data.whatsapp_templates.map((t) => {
                        var regexResults_header = []
                        if(t.text_header){
                            regexResults_header = t.text_header.match(PARAMS_REGEX);
                        }
                        console.log(">>>> regexResults_header", regexResults_header);
                        var regexResults_text = t.text.match(PARAMS_REGEX);
                        console.log(">>>> regexResults_text", regexResults_text);
                        return {
                            id: t.id,
                            name: t.name,
                            type: TEMPLATE_TYPES.WHATSAPP,
                            configuration: {
                                text_header: t.text_header ? t.text_header : "",
                                text: t.text,
                                type: t.type,
                                status: t.status,
                                created: t.created,
                                updated: t.updated,
                                identifier_media: t.identifier_media,
                                link_media: t.link_media,
                                numParams_header: regexResults_header ? regexResults_header.length : 0,
                                numParams_text: regexResults_text ? regexResults_text.length : 0
                            }
                        };
                    }));
                }
            }
            commit('initSupCampaignTemplates', templates);
            return response;
        } catch (error) {
            console.error('Error al obtener los templates');
            console.error(error);
            commit('initSupCampaignTemplates', []);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al obtener los templates'
            };
        }
    }
};
