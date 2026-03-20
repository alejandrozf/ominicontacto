<template>
  <div class="disabled cursor-pointer" @click="requestConversation()">
    <div class="flex justify-content-between flex-wrap">
      <div class="flex align-items-center justify-content-center">
        <Avatar icon="pi pi-user" size="xlarge" shape="circle" />
        <span class="pl-2">{{ conversationInfo.from }}</span>
      </div>
      <div
        v-if="conversationInfo.numMessages > 0"
        class="flex align-items-center justify-content-center"
      >
        <Badge v-if="conversationInfo.isMine && conversationInfo.numMessagesUnread > 0" :value="conversationInfo.numMessagesUnread" />
        <Button
          icon="pi pi-arrow-circle-left"
          class="p-button-secondary p-button-rounded ml-2"
          @click.stop="requestConversation()"
          v-tooltip.top="$t('globals.request')"
          v-if="!conversationInfo.isMine && conversationInfo.isNew"
        />
      </div>
    </div>
    <div class="flex justify-content-between flex-wrap my-2">
      <div
        v-if="conversationInfo.transferAgent"
        class="flex align-items-center justify-content-center"
      >
        <Tag
          icon="pi pi-user-plus"
          :value="`Transferido por ${conversationInfo.transferAgent}`"
          severity="secondary"
          rounded
        ></Tag>
      </div>
      <div class="flex align-items-center justify-content-center">
        <small class="font-italic">
          <b>{{ conversationInfo.date }}</b>
        </small>
      </div>
    </div>
    <div class="flex justify-content-between flex-wrap my-2">
      <div class="flex align-items-center justify-content-center">
        <div class="grid">
          <div class="col-12">
            <Tag
              v-if="isExpired"
              icon="pi pi-clock"
              :value="`${$t('views.whatsapp.conversations.expired_conversation')}`"
              severity="warning"
              rounded
            ></Tag>
          </div>
          <div class="col-12" v-if="conversationInfo.error">
            <Tag
              icon="pi pi-times"
              :value="`${$t('views.whatsapp.conversations.error_conversation')}`"
              v-tooltip="`${conversationInfo.errorEx.reason} [${conversationInfo.errorEx.code}]`"
              severity="danger"
              rounded
            ></Tag>
          </div>
        </div>
      </div>
      <div class="flex align-items-center justify-content-center">
        <Tag
          :style="{ background: facebook_color }"
          icon="pi pi-sitemap"
          :value="`${$t('globals.campaign')} (${
            conversationInfo.campaignName
          })`"
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
import { notificationEvent, NOTIFICATION } from '@/globals/agent/facebook';

export default {
    data () {
        return {
            facebook_color: COLORS.FACEBOOK.Blue,
            isExpired: false
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
                    numMessagesUnread: 0,
                    isMine: false,
                    isNew: false,
                    expire: null,
                    transferAgent: null,
                    errorEx: {},
                    error: false
                };
            }
        }
    },
    methods: {
        ...mapActions(['agtFacebookCoversationRequest']),
        getConversationStorageInfo (data = {}) {
            const info = data && data.conversation_data ? data.conversation_data : {};
            return {
                id: info && info.id ? info.id : this.conversationInfo.id,
                campaignId:
                    info && info.campaing_id ? info.campaing_id : this.conversationInfo.campaignId,
                campaignName:
                    info && info.campaing_name ? info.campaing_name : this.conversationInfo.campaignName,
                page_client_id:
                    info && info.destination ? info.destination : null,
                client: info && info.client ? info.client : null,
                agent: info && info.agent ? info.agent : null,
                transferAgent:
                    info && info.transfer_agent
                        ? info.transfer_agent
                        : this.conversationInfo.transferAgent || null,
                isActive: info && Object.prototype.hasOwnProperty.call(info, 'is_active')
                    ? info.is_active
                    : null,
                isDisposition: info && Object.prototype.hasOwnProperty.call(info, 'is_disposition')
                    ? info.is_disposition
                    : null,
                expire: info && info.expire ? info.expire : this.conversationInfo.expire,
                timestamp: info && info.timestamp ? info.timestamp : null,
                messageNumber:
                    info && info.message_number ? info.message_number : this.conversationInfo.numMessages,
                messageUnreadNumber:
                    info && info.message_unread ? info.message_unread : this.conversationInfo.numMessagesUnread,
                photo: info && info.photo ? info.photo : null,
                page: info && info.page ? info.page : null,
                errorEx: info && info.error_ex ? info.error_ex : this.conversationInfo.errorEx,
                error: info && info.error ? info.error : this.conversationInfo.error,
                client_alias: info && info.client_alias ? info.client_alias : this.conversationInfo.from
            };
        },
        async requestConversation () {
            const { status, message, data } = await this.agtFacebookCoversationRequest(
                this.conversationInfo.id
            );
            if (status === HTTP_STATUS.SUCCESS) {
                localStorage.setItem(
                    'agtFacebookConversationInfo',
                    JSON.stringify(this.getConversationStorageInfo(data))
                );
                localStorage.setItem(
                    'agtFacebookConversationAttending',
                    this.conversationInfo.id
                );
                this.$router.push({
                    name: 'agent_facebook_conversation_detail',
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
        },
        checkExpirationDate () {
            const now = new Date();
            const expire = new Date(this.conversationInfo.expire);
            this.isExpired = expire < now;
        }
    },
    watch: {
        conversationInfo: {
            handler () {
                if (this.conversationInfo.expire !== null) {
                    this.checkExpirationDate();
                }
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
