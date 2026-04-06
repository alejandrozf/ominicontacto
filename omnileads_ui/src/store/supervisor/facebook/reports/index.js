import {
    SupervisorFacebookCampaignReportActions,
    SupervisorFacebookCampaignReportMutations,
    SupervisorFacebookCampaignReportState
} from './campaign';

import SupervisorFacebookGeneralReportState from './general_report/state';
import SupervisorFacebookGeneralReportMutations from './general_report/mutations';
import SupervisorFacebookGeneralReportActions from './general_report/actions';

export const SupervisorFacebookReportState = {
    ...SupervisorFacebookCampaignReportState,
    ...SupervisorFacebookGeneralReportState
};

export const SupervisorFacebookReportMutations = {
    ...SupervisorFacebookCampaignReportMutations,
    ...SupervisorFacebookGeneralReportMutations
};

export const SupervisorFacebookReportActions = {
    ...SupervisorFacebookCampaignReportActions,
    ...SupervisorFacebookGeneralReportActions
};
