import ProvidersActions from './providers/actions';
import ProvidersMutations from './providers/mutations';
import ProvidersState from './providers/state';
import LinesActions from './lines/actions';
import LinesMutations from './lines/mutations';
import LinesState from './lines/state';
import MessageTemplateActions from './message_templates/actions';
import MessageTemplateMutations from './message_templates/mutations';
import MessageTemplateState from './message_templates/state';

export const SupervisorWhatsappState = {
    ...ProvidersState,
    ...LinesState,
    ...MessageTemplateState
};

export const SupervisorWhatsappMutations = {
    ...ProvidersMutations,
    ...LinesMutations,
    ...MessageTemplateMutations
};

export const SupervisorWhatsappActions = {
    ...ProvidersActions,
    ...LinesActions,
    ...MessageTemplateActions
};
