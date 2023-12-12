import {
    SupervisorWhatsappCampaignReportActions,
    SupervisorWhatsappCampaignReportMutations,
    SupervisorWhatsappCampaignReportState
} from './campaign';

import SupervisorWhatsappGeneralReportState from './general_report/state';
import SupervisorWhatsappGeneralReportMutations from './general_report/mutations';
import SupervisorWhatsappGeneralReportActions from './general_report/actions';

export const SupervisorWhatsappReportState = {
    ...SupervisorWhatsappCampaignReportState,
    ...SupervisorWhatsappGeneralReportState
};

export const SupervisorWhatsappReportMutations = {
    ...SupervisorWhatsappCampaignReportMutations,
    ...SupervisorWhatsappGeneralReportMutations
};

export const SupervisorWhatsappReportActions = {
    ...SupervisorWhatsappCampaignReportActions,
    ...SupervisorWhatsappGeneralReportActions
};
