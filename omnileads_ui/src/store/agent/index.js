import {
    AgentWhatsappActions,
    AgentWhatsappMutations,
    AgentWhatsappState,
    AgentWhatsappGetters
} from './whatsapp';
import {
    AgentFacebookActions,
    AgentFacebookMutations,
    AgentFacebookState,
    AgentFacebookGetters
} from './facebook';

export const agentState = {
    ...AgentWhatsappState,
    ...AgentFacebookState
};

export const agentMutations = {
    ...AgentWhatsappMutations,
    ...AgentFacebookMutations
};

export const agentActions = {
    ...AgentWhatsappActions,
    ...AgentFacebookActions
};

export const agentGetters = {
    ...AgentWhatsappGetters,
    ...AgentFacebookGetters
};
