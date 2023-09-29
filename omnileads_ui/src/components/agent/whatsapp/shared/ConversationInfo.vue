<template>
  <div class="disabled">
    <div class="flex justify-content-between flex-wrap">
      <div class="flex align-items-center justify-content-center">
        <Avatar
          icon="pi pi-user"
          size="xlarge"
          shape="circle"
        />
        <span class="pl-2">{{ conversationInfo.from }}</span>
      </div>
      <div
        v-if="conversationInfo.numMessages > 0"
        class="flex align-items-center justify-content-center"
      >
        <Badge :value="conversationInfo.numMessages" />
        <Button
          icon="pi pi-arrow-circle-left"
          class="p-button-secondary p-button-rounded ml-2"
          @click="requestConversation()"
          v-tooltip.top="$t('globals.request')"
          v-if="!conversationInfo.isMine && conversationInfo.isNew"
        />
      </div>
    </div>
    <div class="flex justify-content-end flex-wrap my-2">
      <div class="flex align-items-center justify-content-center">
        <small class="font-italic">
          <b>{{ conversationInfo.date }}</b>
        </small>
      </div>
    </div>
    <div class="flex justify-content-end flex-wrap mb-2">
      <div class="flex align-items-center justify-content-center">
        <Tag
          :style="{ background: whatsapp_color }"
          icon="pi pi-sitemap"
          :value="`${$t('globals.campaign')} (${conversationInfo.campaignName})`"
          severity="info"
          rounded
        ></Tag>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import { HTTP_STATUS, COLORS } from '@/globals';
import { notificationEvent, NOTIFICATION } from '@/globals/agent/whatsapp';

export default {
    data () {
        return {
            whatsapp_color: COLORS.WHATSAPP.TealGreen
        };
    },
    props: {
        conversationInfo: {
            type: Object,
            default: () => {
                return {
                    id: null,
                    from: '-----',
                    date: '-----',
                    campaignId: '',
                    campaignName: '',
                    numMessages: 0,
                    isMine: false,
                    isNew: false
                };
            }
        }
    },
    methods: {
        ...mapActions(['agtWhatsCoversationRequest']),
        async requestConversation () {
            const { status, message } = await this.agtWhatsCoversationRequest(
                this.conversationInfo.id
            );
            if (status === HTTP_STATUS.SUCCESS) {
                this.$router.push({
                    name: 'agent_whatsapp_conversation_detail',
                    params: { id: this.conversationInfo.id }
                });
                await notificationEvent(
                    NOTIFICATION.TITLES.SUCCESS,
                    message,
                    NOTIFICATION.ICONS.SUCCESS
                );
            } else {
                await notificationEvent(
                    NOTIFICATION.TITLES.ERROR,
                    message,
                    NOTIFICATION.ICONS.ERROR
                );
            }
        }
    },
    watch: {
        conversationInfo: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
