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
        getConversationInfo (data = null) {
            return {
                id: data && data.id ? data.id : null,
                from: data && data.from ? data.from : null,
                date: data && data.date ? data.date.toLocaleString() : null,
                campaignId: data && data.campaignId ? data.campaignId : null,
                campaignName: data && data.campaignName ? data.campaignName : null,
                numMessages: data && data.numMessages ? data.numMessages : null,
                numMessagesUnread: data && data.numMessagesUnread ? data.numMessagesUnread : null,
                isMine: data && data.isMine ? data.isMine : null,
                isNew: data && data.isNew ? data.isNew : null,
                expire: data && data.expire ? data.expire : null,
                errorEx: data && data.errorEx ? data.errorEx : null,
                error: data && data.error ? data.error : false
            };
        },
        conversationDetail ({ id, isNew, isMine }) {
            if (!isNew && isMine) {
                localStorage.setItem('agtWhatsappConversationAttending', id);
                this.$router.push({
                    name: 'agent_whatsapp_conversation_detail',
                    params: { id }
                });
            }
        }
    }
};
</script>
