/* eslint-disable no-unused-vars */
import { HTTP_STATUS } from '@/globals';
import Service from '@/services/supervisor/facebook/reports/general_report_service';
const service = new Service();

export default {
    async initSupFacebookReportGeneral (
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
            const response = await service.getGeneralFacebookReport({
                campaignId,
                filters
            });
            const { status, data } = response;
            commit(
                'initSupFacebookReportGeneral',
                status === HTTP_STATUS.SUCCESS ? data : null
            );
            return response;
        } catch (error) {
            console.error(
                `===> Error al obtener < Reporte General de Meta/Facebook de la Campana (${campaignId}) >`
            );
            console.error(error);
            commit('initSupFacebookReportGeneral', null);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al obtener Reporte General de Meta/Facebook'
            };
        }
    },
    initSupFacebookReportGeneralColors ({ commit }, { rgbColors, rgbaColors }) {
        commit('initSupFacebookReportGeneralColors', { rgbColors, rgbaColors });
    }
};
