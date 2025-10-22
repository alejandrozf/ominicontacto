/* eslint-disable no-unused-vars */
import { HTTP_STATUS } from '@/globals';
import Service from '@/services/supervisor/whatsapp/reports/general_report_service';
const service = new Service();

export default {
    async initSupWhatsReportGeneral (
        { commit },
        {
            campaignId = null,
            filters = {
                startDate: null,
                endDate: null
            }
        }
    ) {
        try {
            const response = await service.getGeneralWhatsappReport({
                campaignId,
                filters
            });
            const { status, data } = response;
            commit(
                'initSupWhatsReportGeneral',
                status === HTTP_STATUS.SUCCESS ? data : null
            );
            return response;
        } catch (error) {
            console.error(
                `===> Error al obtener < Reporte General de Whatsapp de la Campana (${campaignId}) >`
            );
            console.error(error);
            commit('initSupWhatsReportGeneral', null);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al obtener Reporte General de Whatsapp'
            };
        }
    },
    initSupWhatsReportGeneralColors ({ commit }, { rgbColors, rgbaColors }) {
        commit('initSupWhatsReportGeneralColors', { rgbColors, rgbaColors });
    }
};
