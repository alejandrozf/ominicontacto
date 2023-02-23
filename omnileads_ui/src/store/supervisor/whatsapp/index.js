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

export const SupervisorWhatsappState = {
    ...ProvidersState,
    ...LinesState,
    ...MessageTemplateState,
    ...WhatsappTemplateState
};

export const SupervisorWhatsappMutations = {
    ...ProvidersMutations,
    ...LinesMutations,
    ...MessageTemplateMutations,
    ...WhatsappTemplateMutations
};

export const SupervisorWhatsappActions = {
    ...ProvidersActions,
    ...LinesActions,
    ...MessageTemplateActions,
    ...WhatsappTemplateActions
};
