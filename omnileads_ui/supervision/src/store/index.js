import { createStore } from 'vuex';
import AgentsCampaignService from '../services/agents_campaign_service.js';
import PauseSetActions from './pause_set/actions';
import PauseSetMutations from './pause_set/mutations';
import PauseSetState from './pause_set/state';
import ExternalSiteActions from './external_site/actions';
import ExternalSiteMutations from './external_site/mutations';
import ExternalSiteState from './external_site/state';
import CallDispositionActions from './call_disposition/actions';
import CallDispositionMutations from './call_disposition/mutations';
import CallDispositionState from './call_disposition/state';
import ExternalSystemActions from './external_system/actions';
import ExternalSystemMutations from './external_system/mutations';
import ExternalSystemState from './external_system/state';
import FormActions from './form/actions';
import FormMutations from './form/mutations';
import FormState from './form/state';
const agentsCampaignService = new AgentsCampaignService();

export default createStore({
    state: {
        agents_by_campaign: [],
        active_agents: [],
        campaign: {},
        groups: [],
        ...PauseSetState,
        ...ExternalSiteState,
        ...CallDispositionState,
        ...ExternalSystemState,
        ...FormState
    },
    mutations: {
        addAgentToCampaign (state, newAgent) {
            state.agents_by_campaign.push(newAgent);
        },
        initAgentsCampaign (state, agents) {
            state.agents_by_campaign = agents;
        },
        initCampaign (state, campaign) {
            state.campaign = campaign;
        },
        initActiveAgents (state, activeAgents) {
            state.active_agents = activeAgents;
        },
        removeAgentOfCampaign (state, agentId) {
            state.agents_by_campaign = state.agents_by_campaign.filter(e => e.agent_id !== agentId);
        },
        updateAgentPenalty (state, payload) {
            // eslint-disable-next-line array-callback-return
            state.agents_by_campaign.filter((agent) => {
                if (agent.agent_id === payload.agent_id) {
                    agent.agent_penalty = payload.penalty;
                }
            });
        },
        ...PauseSetMutations,
        ...ExternalSiteMutations,
        ...CallDispositionMutations,
        ...ExternalSystemMutations,
        ...FormMutations
    },
    actions: {
        addAgentToCampaign ({ commit }, newAgent) {
            commit('addAgentToCampaign', newAgent);
        },
        removeAgentOfCampaign ({ commit }, agentId) {
            commit('removeAgentOfCampaign', agentId);
        },
        async initAgentsCampaign ({ commit }, campaignId) {
            const { agentsCampaign, campaign } = await agentsCampaignService.getAgentsByCampaign(campaignId);
            commit('initCampaign', campaign);
            commit('initAgentsCampaign', agentsCampaign);
        },
        async initActiveAgents ({ commit }) {
            const { activeAgents, groups } = await agentsCampaignService.getActiveAgents();
            commit('initActiveAgents', activeAgents);
            commit('initGroups', groups);
        },
        updateAgentPenalty ({ commit }, payload) {
            commit('updateAgentPenalty', payload);
        },
        ...PauseSetActions,
        ...ExternalSiteActions,
        ...CallDispositionActions,
        ...ExternalSystemActions,
        ...FormActions
    },
    modules: {
    },
    getters: {
        getAgentsByCampaign: state => state.agents_by_campaign,
        getActiveAgents: state => state.active_agents,
        getCampaign: state => state.campaign,
        getGroups: state => state.groups,
        getPauseSets: state => state.pauseSets,
        getPauseSetDetail: state => state.pauseSetDetail,
        getPauses: state => state.pauses
    }
});
