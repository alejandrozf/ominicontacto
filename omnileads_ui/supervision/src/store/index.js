import { createStore } from 'vuex';
import AgentsCampaignService from '../services/agentsCampaignService.js';
import PauseSetActions from './pause_sets/actions';
import PauseSetMutations from './pause_sets/mutations';
import PauseSetState from './pause_sets/state';
const agentsCampaignService = new AgentsCampaignService();

export default createStore({
    state: {
        agents_by_campaign: [],
        active_agents: [],
        campaign: {},
        groups: [],
        ...PauseSetState
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
        ...PauseSetMutations
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
        ...PauseSetActions
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
