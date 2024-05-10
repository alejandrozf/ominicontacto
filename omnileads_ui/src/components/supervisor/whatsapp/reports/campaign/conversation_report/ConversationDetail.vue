<template>
  <div>
    <Fieldset
      :legend="$t('views.whatsapp.reports.campaign.conversation.detail_title')"
      :toggleable="true"
    >
      <div class="grid">
        <div class="sm:col-12 md:col-12 lg:col-6 xl:col-6">
          <span>
            <b> {{ $t("models.whatsapp.conversation.campaign") }}: </b>
            {{ agtWhatsCoversationInfo.campaignName }}
          </span>
        </div>
        <div class="sm:col-12 md:col-12 lg:col-6 xl:col-6">
          <span>
            <b> {{ $t("models.whatsapp.conversation.destination") }}: </b>
            <Tag
              icon="pi pi-phone"
              severity="info"
              :value="agtWhatsCoversationInfo.destination"
              rounded
            ></Tag>
          </span>
        </div>
        <div class="sm:col-12 md:col-12 lg:col-6 xl:col-6">
          <span>
            <b> {{ $t("models.whatsapp.conversation.line") }}: </b>
            {{ agtWhatsCoversationInfo.line.name }}
          </span>
        </div>
        <div class="sm:col-12 md:col-12 lg:col-6 xl:col-6">
          <span>
            <b> {{ $t("models.whatsapp.conversation.message") }}: </b>
            <Tag
              icon="pi pi-comments"
              severity="primary"
              :value="agtWhatsCoversationInfo.messageNumber"
              rounded
            ></Tag>
          </span>
        </div>
        <div class="sm:col-12 md:col-12 lg:col-6 xl:col-6">
          <span>
            <b> {{ $t("models.whatsapp.conversation.expire") }}: </b>
            <Tag
              :icon="getIcon(agtWhatsCoversationInfo.expire)"
              :severity="getColor(agtWhatsCoversationInfo.expire)"
              :value="getValue(agtWhatsCoversationInfo.expire)"
              rounded
            ></Tag>
          </span>
        </div>
        <div class="sm:col-12 md:col-12 lg:col-6 xl:col-6">
          <span>
            <b> {{ $t("models.whatsapp.conversation.is_active") }}: </b>
            <i
              v-if="agtWhatsCoversationInfo.isActive"
              class="pi pi-check-circle"
              style="color: green"
            ></i>
            <i v-else class="pi pi-times-circle" style="color: red"></i>
          </span>
        </div>
      </div>
    </Fieldset>
    <HeaderConversation
      :isExpired="isExpired"
      :viewAsReport="true"
      class="mt-4"
    />
    <div class="flex justify-content-between flex-wrap my-2">
      <div class="flex align-items-center justify-content-center">
        <Tag
          v-if="isExpired"
          icon="pi pi-clock"
          :value="`${$t('views.whatsapp.conversations.expired_conversation')}`"
          severity="warning"
          rounded
        ></Tag>
      </div>
      <div class="flex align-items-center justify-content-center">
        <Tag
          :style="{ background: whatsapp_color }"
          icon="pi pi-sitemap"
          :value="`${$t('globals.campaign')} (${
            agtWhatsCoversationInfo.campaignName
          })`"
          severity="info"
          rounded
        ></Tag>
      </div>
    </div>
    <ListMessages id="listMessages" class="scroll" />
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import HeaderConversation from '@/components/agent/whatsapp/conversation/HeaderConversation';
import ListMessages from '@/components/agent/whatsapp/conversation/ListMessages';
import { COLORS } from '@/globals';
export default {
    inject: ['$helpers'],
    components: {
        HeaderConversation,
        ListMessages
    },
    data () {
        return {
            whatsapp_color: COLORS.WHATSAPP.TealGreen,
            isExpired: false
        };
    },
    created () {
        this.scrollDown();
    },
    computed: {
        ...mapState(['agtWhatsCoversationInfo'])
    },
    beforeUnmount () {
        window.parent.removeEventListener('message', () => {});
    },
    methods: {
        ...mapActions([]),
        scrollDown () {
            const scroll = document.getElementById('listMessages');
            if (scroll) {
                scroll.scrollTop = scroll.scrollHeight;
            }
        },
        checkExpirationDate () {
            if (this.agtWhatsCoversationInfo.expire) {
                const now = new Date();
                const expire = new Date(this.agtWhatsCoversationInfo.expire);
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
        }
    },
    watch: {
        agtWhatsCoversationInfo: {
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
