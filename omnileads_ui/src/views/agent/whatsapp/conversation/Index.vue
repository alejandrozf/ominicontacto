<template>
  <div>
    <HeaderConversation />
    <Message
      v-if="!agtWhatsCoversationInfo.client.id"
      severity="warn"
      :closable="false"
      class="mt-0 mb-3"
      >{{ $t("views.whatsapp.contact.info") }}
      <b
        ><a @click="createContact">{{ $t("globals.here").toUpperCase() }}</a></b
      >
    </Message>
    <div class="flex justify-content-end flex-wrap my-2">
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
    <TextBox
      class="footer"
      :conversationId="id"
      @scrollDownEvent="scrollDown"
    />
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import HeaderConversation from '@/components/agent/whatsapp/conversation/HeaderConversation';
import TextBox from '@/components/agent/whatsapp/conversation/TextBox';
import ListMessages from '@/components/agent/whatsapp/conversation/ListMessages';
import { listenerStoreDataByAction } from '@/utils';
import { COLORS } from '@/globals';
export default {
    components: {
        HeaderConversation,
        ListMessages,
        TextBox
    },
    data () {
        return {
            id: parseInt(this.$route.params.id),
            whatsapp_color: COLORS.WHATSAPP.TealGreen
        };
    },
    async created () {
        window.parent.addEventListener('message', this.refreshConversationInfo);
        await this.listenerEvents();
        await this.agtWhatsConversationDetail({
            conversationId: this.id,
            $t: this.$t
        });
        await this.scrollDown();
    },
    computed: {
        ...mapState(['agtWhatsCoversationInfo'])
    },
    beforeUnmount () {
        window.parent.removeEventListener('message', () => {});
    },
    methods: {
        ...mapActions([
            'agtWhatsConversationDetail',
            'agtWhatsSetCoversationMessages',
            'agtWhatsSetCoversationInfo'
        ]),
        scrollDown () {
            const scroll = document.getElementById('listMessages');
            scroll.scrollTop = scroll.scrollHeight;
        },
        listenerEvents () {
            listenerStoreDataByAction(
                'agtWhatsSetCoversationMessages',
                this.agtWhatsSetCoversationMessages
            );
        },
        createContact () {
            localStorage.setItem(
                'agtWhatsCoversationInfo',
                JSON.stringify(this.agtWhatsCoversationInfo)
            );
            const event = new CustomEvent('onWhatsappContactFormEvent', {
                detail: {
                    contact_form: true
                }
            });
            window.parent.document.dispatchEvent(event);
        },
        async refreshConversationInfo (event) {
            if (event.data.type === 'refreshConversationInfo') {
                const info =
          JSON.parse(localStorage.getItem('agtWhatsCoversationInfo')) || null;
                await this.agtWhatsSetCoversationInfo(info);
            }
        }
    },
    watch: {
        agtWhatsCoversationInfo: {
            handler () {},
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

.footer {
  bottom: 0px;
  position: fixed;
  width: 100%;
}

a:hover {
  text-decoration: underline;
  cursor: pointer;
  font-size: 130%;
}
</style>
