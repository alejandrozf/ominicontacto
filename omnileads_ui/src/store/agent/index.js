import {
    AgentWhatsappActions,
    AgentWhatsappMutations,
    AgentWhatsappState,
    AgentWhatsappGetters
} from './whatsapp';

export const agentState = {
    ...AgentWhatsappState
};

export const agentMutations = {
    ...AgentWhatsappMutations
};

export const agentActions = {
    ...AgentWhatsappActions
};

export const agentGetters = {
    ...AgentWhatsappGetters
};
