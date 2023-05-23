import { createStore } from 'vuex';
import { supervisorActions, supervisorGetters, supervisorMutations, supervisorState } from './supervisor';
import { agentActions, agentMutations, agentState, agentGetters } from './agent';

export default createStore({
    state: {
        ...supervisorState,
        ...agentState
    },
    mutations: {
        ...supervisorMutations,
        ...agentMutations
    },
    actions: {
        ...supervisorActions,
        ...agentActions
    },
    modules: {
    },
    getters: {
        ...supervisorGetters,
        ...agentGetters
    }
});
