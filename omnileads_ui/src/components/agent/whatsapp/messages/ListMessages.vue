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
        :from="data.option.from"
        :date="data.option.date.toLocaleString()"
        :numMessages="data.option.numMessages"
        @click="conversationDetail(data.option.id)"
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
        conversationDetail (id) {
            this.$router.push({
                name: 'agent_whatsapp_conversation_detail',
                params: { id }
            });
        }
    }
};
</script>
