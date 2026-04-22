<template>
  <div class="h-full flex flex-column">
    <HeaderConversation :isExpired="isExpired" />
    <div v-if="showConversationError">
      <Message severity="error" :closable="true" class="mt-0 mb-3"
        >{{ $t("views.whatsapp.conversations.error_conversation_detail") }}
        <br>
        {{ agtWhatsCoversationInfo.errorEx.reason }} [{{ agtWhatsCoversationInfo.errorEx.code }}]
      </Message>
    </div>
    <div v-else-if="showAttachmentErrorBanner">
      <Message severity="warn" :closable="true" class="mt-0 mb-3">
        {{ $t('views.whatsapp.conversations.attachment_error_detail', {
          code: agtWhatsCoversationInfo.errorEx.code
        }) }}
      </Message>
    </div>
    <div>
      <Message
        v-if="!isLoading && !agtWhatsCoversationInfo.client.id"
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
    <div v-if="isLoading" class="flex flex-grow-1 justify-content-center align-items-center">
      <ProgressSpinner />
    </div>
    <template v-else>
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
          v-if="agtWhatsCoversationInfo && agtWhatsCoversationInfo.campaignName"
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
    </template>
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
import { isAttachmentDeliveryError } from '@/utils/conversationErrors';
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
            isExpired: false,
            isLoading: false
        };
    },
    async created () {
        await this.listenerEvents();
        await this.initData();
    },
    computed: {
        ...mapState(['agtWhatsCoversationInfo', 'agtWhatsCoversationMessages']),
        isAttachmentError () {
            return isAttachmentDeliveryError(this.agtWhatsCoversationInfo.errorEx);
        },
        showAttachmentErrorBanner () {
            return this.agtWhatsCoversationInfo.error && this.isAttachmentError;
        },
        showConversationError () {
            return this.agtWhatsCoversationInfo.error && !this.isAttachmentError;
        }
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
        window.parent.document.addEventListener(
            WHATSAPP_LOCALSTORAGE_EVENTS.DISPOSITION.DONE,
            this.dispositionDone
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
        window.parent.document.removeEventListener(
            WHATSAPP_LOCALSTORAGE_EVENTS.DISPOSITION.DONE,
            this.dispositionDone
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
            if (scroll) {
                scroll.scrollTop = scroll.scrollHeight;
            }
        },
        resetConversationState () {
            this.isDisposition = false;
            this.isTransferred = false;
            this.isExpired = false;
        },
        clearConversationStorage () {
            localStorage.setItem('agtWhatsappConversationAttending', null);
            localStorage.setItem('agtWhatsappConversationMessages', null);
            localStorage.setItem('agtWhatsCoversationInfo', JSON.stringify(null));
        },
        async initData () {
            this.isLoading = true;
            this.resetConversationState();
            
            // Fix race condition glitch by clearing current state during load
            this.agtWhatsSetCoversationInfo(null);
            this.agtWhatsSetCoversationMessages([]);

            await this.agtWhatsConversationDetail({
                conversationId: this.id
            });
            this.isLoading = false;
            const savedConversationInfo = JSON.parse(
                localStorage.getItem('agtWhatsCoversationInfo')
            );
            if (
                savedConversationInfo?.id === this.id &&
                savedConversationInfo?.transferAgent
            ) {
                await this.agtWhatsSetCoversationInfo({
                    ...this.agtWhatsCoversationInfo,
                    transferAgent: savedConversationInfo.transferAgent
                });
            }
            localStorage.setItem('agtWhatsappConversationAttending', this.id);
            localStorage.setItem(
                'agtWhatsCoversationInfo',
                JSON.stringify({
                    ...this.agtWhatsCoversationInfo,
                    transferAgent:
                        savedConversationInfo?.id === this.id
                            ? savedConversationInfo?.transferAgent || null
                            : null
                })
            );
            this.$nextTick(() => {
                this.scrollDown();
            });
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
                setTimeout(() => {
                    this.clearConversationStorage();
                    this.resetConversationState();
                    this.$router.push({ name: 'agent_whatsapp' });
                }, 2500);
            }
        },
        dispositionDone (event) {
            if (event.detail.conversationId === this.id) {
                this.clearConversationStorage();
                this.resetConversationState();
                this.$router.push({ name: 'agent_whatsapp' });
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
        '$route.params.id': {
            async handler (value) {
                const nextId = parseInt(value);
                if (!Number.isNaN(nextId) && nextId !== this.id) {
                    this.id = nextId;
                    await this.initData();
                }
            }
        },
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

a:hover {
  text-decoration: underline;
  cursor: pointer;
  font-size: 130%;
}

.btn-border {
  border-radius: 20px;
}
</style>
