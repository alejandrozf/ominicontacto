import ProvidersActions from './providers/actions';
import ProvidersMutations from './providers/mutations';
import ProvidersState from './providers/state';
import MessageTemplateActions from './message_templates/actions';
import MessageTemplateMutations from './message_templates/mutations';
import MessageTemplateState from './message_templates/state';

export const SupervisorWhatsappState = {
    ...ProvidersState,
    ...MessageTemplateState
};

export const SupervisorWhatsappMutations = {
    ...ProvidersMutations,
    ...MessageTemplateMutations
};

export const SupervisorWhatsappActions = {
    ...ProvidersActions,
    ...MessageTemplateActions
};
