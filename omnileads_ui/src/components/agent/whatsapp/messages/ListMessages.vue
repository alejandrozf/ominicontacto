<template>
  <Listbox
    :options="messages"
    :filter="true"
    optionLabel="from"
    :emptyFilterMessage="$t('globals.without_data')"
    v-bind:filterPlaceholder="
      $t('globals.find_by', { field: $tc('globals.name') }, 1)
    "
  >
    <template #option="data">
      <ConversationInfo
        :conversationInfo="getConversationInfo(data.option)"
        @click="conversationDetail(data.option)"
      />
    </template>
  </Listbox>
</template>

<script>
import ConversationInfo from '@/components/agent/whatsapp/shared/ConversationInfo';
export default {
    components: {
        ConversationInfo
    },
    props: {
        messages: {
            type: Array,
            default: () => []
        }
    },
    methods: {
        getConversationInfo (data) {
            return {
                id: data.id,
                from: data.from,
                date: data.date.toLocaleString(),
                campaignId: data.campaignId,
                campaignName: data.campaignName,
                numMessages: data.numMessages,
                isMine: data.isMine,
                isNew: data.isNew,
                expire: data.expire,
                error: data.error
            };
        },
        conversationDetail ({ id, isNew, isMine }) {
            if (!isNew && isMine) {
                this.$router.push({
                    name: 'agent_whatsapp_conversation_detail',
                    params: { id }
                });
            }
        }
    }
};
</script>
