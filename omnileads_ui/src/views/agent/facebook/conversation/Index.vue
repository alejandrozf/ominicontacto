<template>
  <div class="h-full flex flex-column">
    <HeaderConversation :isExpired="isExpired" />
    <div v-if="agtFacebookConversationInfo.error">
      <Message severity="error" :closable="true" class="mt-0 mb-3"
        >{{ $t("views.whatsapp.conversations.error_conversation_detail") }}
        <br>
        {{ agtFacebookConversationInfo.errorEx.reason }} [{{ agtFacebookConversationInfo.errorEx.code }}]
      </Message>
    </div>
    <div>
      <Message
        v-if="!agtFacebookConversationInfo.client.id"
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
          :value="`${$t('views.facebook.conversations.expired_conversation')}`"
          severity="warning"
          rounded
        ></Tag>
      </div>
      <div class="flex align-items-center justify-content-center">
        <Tag
          :style="{ background: facebook_color }"
          icon="pi pi-sitemap"
          :value="`${$t('globals.campaign')} (${
            agtFacebookConversationInfo.campaignName
          })`"
          severity="info"
          rounded
        ></Tag>
      </div>
    </div>
    <ListMessages id="listMessages" class="flex-grow-1 overflow-y-scroll" />
      <TextBox
        v-if="!isExpired && !isDisposition && !isTransferred"
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
import HeaderConversation from '@/components/agent/facebook/conversation/HeaderConversation';
import TextBox from '@/components/agent/facebook/conversation/TextBox';
import ListMessages from '@/components/agent/facebook/conversation/ListMessages';
import { listenerStoreDataByAction } from '@/utils';
import { COLORS } from '@/globals';
import { FACEBOOK_LOCALSTORAGE_EVENTS } from '@/globals/agent/facebook';
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
            facebook_color: COLORS.FACEBOOK.TealGreen,
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
        ...mapState(['agtFacebookConversationInfo', 'agtFacebookConversationMessages'])
    },
    mounted () {
        window.parent.document.addEventListener(
            FACEBOOK_LOCALSTORAGE_EVENTS.CONVERSATION.DETAIL_INIT_DATA,
            this.updatedLocalStorage
        );
        window.parent.document.addEventListener(
            FACEBOOK_LOCALSTORAGE_EVENTS.TRANSFER.DONE,
            this.transferDone
        );
    },
    beforeUnmount () {
        window.parent.document.removeEventListener(
            FACEBOOK_LOCALSTORAGE_EVENTS.CONVERSATION.DETAIL_INIT_DATA,
            this.updatedLocalStorage
        );
        window.parent.document.removeEventListener(
            FACEBOOK_LOCALSTORAGE_EVENTS.TRANSFER.DONE,
            this.transferDone
        );
    },
    methods: {
        ...mapActions([
            'agtFacebookConversationDetail',
            'agtFacebookSetConversationMessages',
            'agtFacebookSetConversationInfo'
        ]),
        scrollDown () {
            const scroll = document.getElementById('listMessages');
            scroll.scrollTop = scroll.scrollHeight;
        },
        async initData () {
            await this.agtFacebookConversationDetail({
                conversationId: this.id,
                $t: this.$t
            });
            localStorage.setItem('agtFacebookConversationAttending', this.id);
            console.log('SCROLL DOWN ON INIT DATA');
            this.scrollDown();
        },
        listenerEvents () {
            listenerStoreDataByAction(
                'agtFacebookSetCoversationMessages',
                this.agtFacebookSetCoversationMessages
            );
            listenerStoreDataByAction('agtFacebookCoversationDetailInit', this.initData);
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
            localStorage.setItem('agtFacebookInconmingConversation', true);
            localStorage.setItem(
                'agtFacebookConversationInfo',
                JSON.stringify(this.agtFacebookConversationInfo)
            );
            const event = new Event(
                FACEBOOK_LOCALSTORAGE_EVENTS.CONTACT.FORM_INIT_DATA
            );
            window.parent.document.dispatchEvent(event);
            const modalEvent = new CustomEvent('onFacebookContactFormEvent', {
                detail: {
                    contact_form: true
                }
            });
            window.parent.document.dispatchEvent(modalEvent);
        },
        checkExpirationDate () {
            if (this.agtFacebookConversationInfo?.expire) {
                const now = new Date();
                const expire = new Date(this.agtFacebookConversationInfo?.expire);
                this.isExpired = now > expire;
            }
        },
        checkIsDisposition () {
            this.isDisposition = this.agtFacebookConversationInfo?.isDisposition;
        },
        openModalToRestart () {
            localStorage.setItem(
                'agtFacebookConversationMessages',
                JSON.stringify(this.agtFacebookConversationMessages)
            );
            localStorage.setItem(
                'agtFacebookConversationInfo',
                JSON.stringify(this.agtFacebookConversationInfo)
            );
            localStorage.setItem('onlyFacebookTemplates', true);
            const event = new Event(
                FACEBOOK_LOCALSTORAGE_EVENTS.CONVERSATION.RESTART_EXPIRED_CHAT
            );
            window.parent.document.dispatchEvent(event);
            const modalEvent = new CustomEvent('onFacebookTemplatesEvent', {
                detail: {
                    templates: true,
                    conversationId: parseInt(this.$route.params.id)
                }
            });
            window.parent.document.dispatchEvent(modalEvent);
        }
    },
    watch: {
        agtFacebookConversationInfo: {
            handler () {
                this.checkExpirationDate();
                this.checkIsDisposition();
            },
            deep: true,
            immediate: true
        },
        agtFacebookConversationMessages: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>

<style scoped>

a:hover {
  text-decoration: underline;
  cursor: pointer;
  font-size: 130%;
}

.btn-border {
  border-radius: 20px;
}
</style>
