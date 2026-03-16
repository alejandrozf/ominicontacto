<template>
  <div>
    <Fieldset legend="Detalle de conversación Meta/Facebook" :toggleable="true">
      <div class="grid">
        <div class="sm:col-12 md:col-12 lg:col-6 xl:col-6">
          <span>
            <b>{{ $t("models.whatsapp.conversation.campaign") }}:</b>
            {{ agtFacebookConversationInfo.campaignName }}
          </span>
        </div>
        <div class="sm:col-12 md:col-12 lg:col-6 xl:col-6">
          <span>
            <b>Page Client ID:</b>
            <Tag icon="pi pi-id-card" severity="info" :value="agtFacebookConversationInfo.page_client_id" rounded></Tag>
          </span>
        </div>
        <div class="sm:col-12 md:col-12 lg:col-6 xl:col-6">
          <span>
            <b>Página:</b>
            {{ agtFacebookConversationInfo.page.name }} ({{ agtFacebookConversationInfo.page.page_id }})
          </span>
        </div>
        <div class="sm:col-12 md:col-12 lg:col-6 xl:col-6">
          <span>
            <b>{{ $t("models.whatsapp.conversation.message") }}:</b>
            <Tag icon="pi pi-comments" severity="primary" :value="agtFacebookConversationInfo.messageNumber" rounded></Tag>
          </span>
        </div>
        <div class="sm:col-12 md:col-12 lg:col-6 xl:col-6">
          <span>
            <b>{{ $t("models.whatsapp.conversation.expire") }}:</b>
            <Tag :icon="getIcon(agtFacebookConversationInfo.expire)" :severity="getColor(agtFacebookConversationInfo.expire)" :value="getValue(agtFacebookConversationInfo.expire)" rounded></Tag>
          </span>
        </div>
        <div class="sm:col-12 md:col-12 lg:col-6 xl:col-6">
          <span>
            <b>{{ $t("models.whatsapp.conversation.is_active") }}:</b>
            <i v-if="agtFacebookConversationInfo.isActive" class="pi pi-check-circle" style="color: green"></i>
            <i v-else class="pi pi-times-circle" style="color: red"></i>
          </span>
        </div>
      </div>
    </Fieldset>
    <HeaderConversation :isExpired="isExpired" :viewAsReport="true" class="mt-4" />
    <div class="flex justify-content-between flex-wrap my-2">
      <div class="flex align-items-center justify-content-center">
        <Tag v-if="isExpired" icon="pi pi-clock" :value="`${$t('views.whatsapp.conversations.expired_conversation')}`" severity="warning" rounded></Tag>
      </div>
      <div class="flex align-items-center justify-content-center">
        <Tag :style="{ background: facebookColor }" icon="pi pi-sitemap" :value="`${$t('globals.campaign')} (${agtFacebookConversationInfo.campaignName})`" severity="info" rounded></Tag>
      </div>
    </div>
    <ListMessages id="listMessages" class="scroll" />
  </div>
</template>

<script>
import { mapState } from 'vuex';
import HeaderConversation from '@/components/agent/facebook/conversation/HeaderConversation';
import ListMessages from '@/components/agent/facebook/conversation/ListMessages';
import { COLORS } from '@/globals';

export default {
    inject: ['$helpers'],
    components: {
        HeaderConversation,
        ListMessages
    },
    data () {
        return {
            facebookColor: COLORS.FACEBOOK.Blue,
            isExpired: false
        };
    },
    computed: {
        ...mapState(['agtFacebookConversationInfo'])
    },
    methods: {
        checkExpirationDate () {
            if (this.agtFacebookConversationInfo.expire) {
                const now = new Date();
                const expire = new Date(this.agtFacebookConversationInfo.expire);
                this.isExpired = now > expire;
            }
        },
        getColor (expired) {
            const currentDate = new Date();
            const expiredDate = new Date(expired);
            if (expiredDate.getTime() < currentDate.getTime()) {
                return 'warning';
            } else if (expiredDate.getTime() > currentDate.getTime()) {
                return 'success';
            }
            return 'secondary';
        },
        getValue (expired) {
            return this.$helpers.getDatetimeFormat(expired);
        },
        getIcon (expired) {
            const currentDate = new Date();
            const expiredDate = new Date(expired);
            if (expiredDate.getTime() < currentDate.getTime()) {
                return 'pi pi-exclamation-triangle';
            } else if (expiredDate.getTime() > currentDate.getTime()) {
                return 'pi pi-check-circle';
            }
            return 'pi pi-clock';
        }
    },
    watch: {
        agtFacebookConversationInfo: {
            handler () {
                this.checkExpirationDate();
            },
            deep: true,
            immediate: true
        }
    }
};
</script>

<style scoped>
.scroll {
  overflow-y: scroll;
  height: calc(100vh - 180px);
}
</style>
