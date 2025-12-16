/* eslint-disable no-unused-vars */
import { HTTP_STATUS } from '@/globals';
import { TEMPLATE_TYPES } from '@/globals/supervisor/facebook';
import Service from '@/services/supervisor/facebook/templates_service';
const service = new Service();
const PARAMS_REGEX = /{{\d+}}/g;

export default {
    async initSupCampaignFacebookTemplates ({ commit }, { campaignId = null, pageId = null }) {
        try {
            commit('initSupCampaignFacebookTemplates', []);
            if (!campaignId) {
                commit('initSupCampaignFacebookTemplates', []);
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al obtener los templates'
                };
            }
            const response = await service.getTemplates(campaignId, pageId);
            const { status, data } = response;
            let templates = [];
            if (status === HTTP_STATUS.SUCCESS) {
                templates = data.facebook_templates || [];
            }
            commit('initSupCampaignFacebookTemplates', templates);
            return response;
        } catch (error) {
            console.error('Error al obtener los templates');
            console.error(error);
            commit('initSupCampaignFacebookTemplates', []);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al obtener los templates'
            };
        }
    }
};
