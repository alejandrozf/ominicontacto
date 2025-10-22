
import PagesActions from './pages/actions';
import PagesMutations from './pages/mutations';
import PagesState from './pages/state';
import MessageTemplateActions from './message_templates/actions';
import MessageTemplateMutations from './message_templates/mutations';
import MessageTemplateState from './message_templates/state';
// import WhatsappTemplateActions from './whatsapp_templates/actions';
// import WhatsappTemplateMutations from './whatsapp_templates/mutations';
// import WhatsappTemplateState from './whatsapp_templates/state';
import GroupOfMessageTemplateActions from './group_of_message_templates/actions';
import GroupOfMessageTemplateMutations from './group_of_message_templates/mutations';
import GroupOfMessageTemplateState from './group_of_message_templates/state';
import ConfigurationCampaignActions from './configuration_campaign/actions';
import ConfigurationCampaignMutations from './configuration_campaign/mutations';
import ConfigurationCampaignState from './configuration_campaign/state';
import {
    SupervisorWhatsappReportActions,
    SupervisorWhatsappReportMutations,
    SupervisorWhatsappReportState
} from './reports';

export const SupervisorFacebookState = {
    ...PagesState,
    ...MessageTemplateState,
    ...GroupOfMessageTemplateState,
    ...ConfigurationCampaignState,
    ...SupervisorWhatsappReportState
};

export const SupervisorFacebookMutations = {
    ...PagesMutations,
    ...MessageTemplateMutations,
    ...GroupOfMessageTemplateMutations,
    ...ConfigurationCampaignMutations,
    ...SupervisorWhatsappReportMutations
};

export const SupervisorFacebookActions = {
    ...PagesActions,
    ...MessageTemplateActions,
    ...GroupOfMessageTemplateActions,
    ...ConfigurationCampaignActions,
    ...SupervisorWhatsappReportActions
};
