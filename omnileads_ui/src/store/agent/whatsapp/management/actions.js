/* eslint-disable no-unused-vars */
import AgentService from '@/services/supervisor/agents_campaign_service';
import Service from '@/services/agent/whatsapp/management_service';
const agentService = new AgentService();
const service = new Service();

export default {
    async agtWhatsManagementInitData ({ commit }) {
        try {
            const { activeAgents, status } = await agentService.getActiveAgents();
            await commit('agtWhatsManagementInitAgents', status === 'SUCCESS' ? activeAgents : []);
            const data = [
                {
                    id: 1,
                    phone: '7131313385',
                    agent: 39,
                    type: 0,
                    mean: 0,
                    result: 0,
                    score: 0,
                    start_datetime: new Date(),
                    end_datetime: new Date(),
                    observation: 'Lorem ipsum dolor, sit amet consectetur adipisicing elit. Dolorem eum nisi fuga error quod dolores culpa in, sunt a nulla quidem pariatur, vel quam reprehenderit vitae eius fugit incidunt soluta.'
                },
                {
                    id: 2,
                    phone: '7441313385',
                    agent: 39,
                    type: 0,
                    mean: 0,
                    result: 0,
                    score: 0,
                    start_datetime: new Date(),
                    end_datetime: new Date(),
                    observation: 'Lorem ipsum dolor, sit amet consectetur adipisicing elit. Dolorem eum nisi fuga error quod dolores culpa in, sunt a nulla quidem pariatur, vel quam reprehenderit vitae eius fugit incidunt soluta.'
                },
                {
                    id: 3,
                    phone: '7221313385',
                    agent: 39,
                    type: 0,
                    mean: 0,
                    result: 0,
                    score: 0,
                    start_datetime: new Date(),
                    end_datetime: new Date(),
                    observation: 'Lorem ipsum dolor, sit amet consectetur adipisicing elit. Dolorem eum nisi fuga error quod dolores culpa in, sunt a nulla quidem pariatur, vel quam reprehenderit vitae eius fugit incidunt soluta.'
                }
            ];
            await commit('agtWhatsManagementInitData', data);
        } catch (error) {
            await commit('agtWhatsManagementInitAgents', []);
            await commit('agtWhatsManagementInitData', []);
        }
    },
    agtWhatsManagementCreate ({ commit }, data) {
        // return await service.create(data);
        return {
            status: 'SUCCESS',
            message: 'Se creo satisfactoriamente el formulario de gestion'
        };
    },
    async agtWhatsManagementUpdate ({ commit }, { id, data }) {
        return await service.update(id, data);
    },
    async agtWhatsManagementDelete ({ commit }, id) {
        return await service.delete(id);
    }
};
