<template>
  <div>
    <HeaderConversation :isExpired="isExpired" />
    <div v-if="agtWhatsCoversationInfo.error">
      <Message severity="error" :closable="true" class="mt-0 mb-3"
        >{{ $t("views.whatsapp.conversations.error_conversation_detail") }}
        <br>
        {{ agtWhatsCoversationInfo.errorEx.reason }} [{{ agtWhatsCoversationInfo.errorEx.code }}]
      </Message>
    </div>
    <div>
      <Message
        v-if="!agtWhatsCoversationInfo.client.id"
        severity="warn"
        :closable="false"
        class="mt-0 mb-3"
        >{{ $t("views.whatsapp.contact.info") }}
        <b
          ><a @click="createContact">{{
            $t("globals.here").toUpperCase()
          }}</a></b
        >
      </Message>
    </div>
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
      <TextBox
        v-if="!isExpired && !isDisposition && !isTransferred"
        class="footer"
        :conversationId="id"
        @scrollDownEvent="scrollDown"
      />
      <Button
        v-if="isExpired"
        :label="
          $t('views.whatsapp.conversations.restart_conversation').toUpperCase()
        "
        class="w-full btn-border mt-2 p-button-warning"
        @click="openModalToRestart()"
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
import { WHATSAPP_LOCALSTORAGE_EVENTS } from '@/globals/agent/whatsapp';
export default {
    inject: ['$helpers'],
    components: {
        HeaderConversation,
        ListMessages,
        TextBox
    },
    data () {
        return {
            id: parseInt(this.$route.params.id),
            whatsapp_color: COLORS.WHATSAPP.TealGreen,
            isDisposition: false,
            isTransferred: false,
            isExpired: false
        };
    },
    async created () {
        await this.listenerEvents();
        await this.initData();
    },
    computed: {
        ...mapState(['agtWhatsCoversationInfo', 'agtWhatsCoversationMessages'])
    },
    mounted () {
        window.parent.document.addEventListener(
            WHATSAPP_LOCALSTORAGE_EVENTS.CONVERSATION.DETAIL_INIT_DATA,
            this.updatedLocalStorage
        );
        window.parent.document.addEventListener(
            WHATSAPP_LOCALSTORAGE_EVENTS.TRANSFER.DONE,
            this.transferDone
        );
    },
    beforeUnmount () {
        window.parent.document.removeEventListener(
            WHATSAPP_LOCALSTORAGE_EVENTS.CONVERSATION.DETAIL_INIT_DATA,
            this.updatedLocalStorage
        );
        window.parent.document.removeEventListener(
            WHATSAPP_LOCALSTORAGE_EVENTS.TRANSFER.DONE,
            this.transferDone
        );
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
        async initData () {
            await this.agtWhatsConversationDetail({
                conversationId: this.id,
                $t: this.$t
            });
            localStorage.setItem('agtWhatsappConversationAttending', this.id);
            this.scrollDown();
        },
        listenerEvents () {
            listenerStoreDataByAction(
                'agtWhatsSetCoversationMessages',
                this.agtWhatsSetCoversationMessages
            );
            listenerStoreDataByAction('agtWhatsCoversationDetailInit', this.initData);
        },
        async updatedLocalStorage () {
            await this.initData();
        },
        transferDone (event) {
            if (event.detail.conversationId === this.id) {
                this.isTransferred = true;
            }
        },
        createContact () {
            localStorage.setItem('agtWhatsInconmingConversation', true);
            localStorage.setItem(
                'agtWhatsCoversationInfo',
                JSON.stringify(this.agtWhatsCoversationInfo)
            );
            const event = new Event(
                WHATSAPP_LOCALSTORAGE_EVENTS.CONTACT.FORM_INIT_DATA
            );
            window.parent.document.dispatchEvent(event);
            const modalEvent = new CustomEvent('onWhatsappContactFormEvent', {
                detail: {
                    contact_form: true
                }
            });
            window.parent.document.dispatchEvent(modalEvent);
        },
        checkExpirationDate () {
            if (this.agtWhatsCoversationInfo?.expire) {
                const now = new Date();
                const expire = new Date(this.agtWhatsCoversationInfo?.expire);
                this.isExpired = now > expire;
            }
        },
        checkIsDisposition () {
            this.isDisposition = this.agtWhatsCoversationInfo?.isDisposition;
        },
        openModalToRestart () {
            if (this.$helpers.isSocketConnected(this.$t)) {
                localStorage.setItem(
                    'agtWhatsappConversationMessages',
                    JSON.stringify(this.agtWhatsCoversationMessages)
                );
                localStorage.setItem(
                    'agtWhatsCoversationInfo',
                    JSON.stringify(this.agtWhatsCoversationInfo)
                );
                localStorage.setItem('onlyWhatsappTemplates', true);
                const event = new Event(
                    WHATSAPP_LOCALSTORAGE_EVENTS.CONVERSATION.RESTART_EXPIRED_CHAT
                );
                window.parent.document.dispatchEvent(event);
                const modalEvent = new CustomEvent('onWhatsappTemplatesEvent', {
                    detail: {
                        templates: true,
                        conversationId: parseInt(this.$route.params.id)
                    }
                });
                window.parent.document.dispatchEvent(modalEvent);
            }
        }
    },
    watch: {
        agtWhatsCoversationInfo: {
            handler () {
                this.checkExpirationDate();
                this.checkIsDisposition();
            },
            deep: true,
            immediate: true
        },
        agtWhatsCoversationMessages: {
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

.btn-border {
  border-radius: 20px;
}
</style>
