import ConversationActions from './conversation/actions';
import ConversationMutations from './conversation/mutations';
import ConversationState from './conversation/state';
import MessageActions from './messages/actions';
import MessageMutations from './messages/mutations';
import MessageState from './messages/state';
import TemplateActions from './templates/actions';
import TemplateMutations from './templates/mutations';
import TemplateState from './templates/state';
import ManagementActions from './management/actions';
import ManagementMutations from './management/mutations';
import ManagementState from './management/state';
import TransferChatActions from './transfer_chat/actions';
import TransferChatMutations from './transfer_chat/mutations';
import TransferChatState from './transfer_chat/state';
import TransferChatGetters from './transfer_chat/getters';
import ContactActions from './contact/actions';
import ContactMutations from './contact/mutations';
import ContactState from './contact/state';

export const AgentWhatsappState = {
    ...ConversationState,
    ...MessageState,
    ...TemplateState,
    ...ManagementState,
    ...TransferChatState,
    ...ContactState
};

export const AgentWhatsappMutations = {
    ...ConversationMutations,
    ...MessageMutations,
    ...TemplateMutations,
    ...ManagementMutations,
    ...TransferChatMutations,
    ...ContactMutations
};

export const AgentWhatsappActions = {
    ...ConversationActions,
    ...MessageActions,
    ...TemplateActions,
    ...ManagementActions,
    ...TransferChatActions,
    ...ContactActions
};

export const AgentWhatsappGetters = {
    ...TransferChatGetters
};
