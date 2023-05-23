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

export const AgentWhatsappState = {
    ...ConversationState,
    ...MessageState,
    ...TemplateState,
    ...ManagementState,
    ...TransferChatState
};

export const AgentWhatsappMutations = {
    ...ConversationMutations,
    ...MessageMutations,
    ...TemplateMutations,
    ...ManagementMutations,
    ...TransferChatMutations
};

export const AgentWhatsappActions = {
    ...ConversationActions,
    ...MessageActions,
    ...TemplateActions,
    ...ManagementActions,
    ...TransferChatActions
};

export const AgentWhatsappGetters = {
    ...TransferChatGetters
};
