import ProvidersActions from './providers/actions';
import ProvidersMutations from './providers/mutations';
import ProvidersState from './providers/state';
import LinesActions from './lines/actions';
import LinesMutations from './lines/mutations';
import LinesState from './lines/state';
import MessageTemplateActions from './message_templates/actions';
import MessageTemplateMutations from './message_templates/mutations';
import MessageTemplateState from './message_templates/state';
import WhatsappTemplateActions from './whatsapp_templates/actions';
import WhatsappTemplateMutations from './whatsapp_templates/mutations';
import WhatsappTemplateState from './whatsapp_templates/state';
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

export const SupervisorWhatsappState = {
    ...ProvidersState,
    ...LinesState,
    ...MessageTemplateState,
    ...WhatsappTemplateState,
    ...GroupOfMessageTemplateState,
    ...ConfigurationCampaignState,
    ...SupervisorWhatsappReportState
};

export const SupervisorWhatsappMutations = {
    ...ProvidersMutations,
    ...LinesMutations,
    ...MessageTemplateMutations,
    ...WhatsappTemplateMutations,
    ...GroupOfMessageTemplateMutations,
    ...ConfigurationCampaignMutations,
    ...SupervisorWhatsappReportMutations
};

export const SupervisorWhatsappActions = {
    ...ProvidersActions,
    ...LinesActions,
    ...MessageTemplateActions,
    ...WhatsappTemplateActions,
    ...GroupOfMessageTemplateActions,
    ...ConfigurationCampaignActions,
    ...SupervisorWhatsappReportActions
};
