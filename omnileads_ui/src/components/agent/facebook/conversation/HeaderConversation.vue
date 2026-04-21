<template>
  <Toolbar>
    <template #start>
      <div class="flex flex-column gap-2">
        <div class="flex align-items-center">
          <Button
            v-if="!viewAsReport"
            @click="back"
            v-tooltip.top="$t('globals.back')"
            icon="pi pi-arrow-left"
            class="p-button-rounded p-button-secondary p-button-text"
          />
          <Chip
            :label="clientInfo?.name  + ' (' + clientInfo?.page_client_id + ')'"
            icon="pi pi-user"
          />
        </div>
        <Tag
          v-if="agtFacebookConversationInfo.transferAgent"
          icon="pi pi-user-plus"
          :value="`Transferido por ${agtFacebookConversationInfo.transferAgent}`"
          severity="secondary"
          rounded
        />
      </div>
    </template>
    <template #end>
      <div v-if="!viewAsReport">
        <SplitButton
          v-if="!isExpired"
          icon="pi pi-paperclip"
          :model="attachOptions"
          :disabled="areConversationActionsDisabled"
          v-tooltip.top="$t('globals.attach')"
          class="p-button-warning"
        />
        <Button
          v-if="!isExpired"
          icon="pi pi-arrows-h"
          class="p-button-secondary ml-2"
          :disabled="areConversationActionsDisabled"
          @click="transfer"
          v-tooltip.top="$t('globals.transfer')"
        />
        <Button
          v-if="agtFacebookConversationInfo.client.id"
          icon="pi pi-save"
          class="ml-2"
          :disabled="areConversationActionsDisabled"
          @click="qualify"
          v-tooltip.top="$t('globals.save')"
        />
        <Button
          v-if="!isExpired"
          icon="pi pi-copy"
          class="p-button-info ml-2"
          :disabled="areConversationActionsDisabled"
          @click="templates"
          v-tooltip.top="$tc('globals.whatsapp.template', 2)"
        />
        <Button
          v-if="agtFacebookConversationInfo.client.id"
          icon="pi pi-user-edit"
          class="p-button-secondary ml-2"
          @click="editUserInfo"
          v-tooltip.top="$t('views.whatsapp.contact.settings.edit_info')"
        />
        <Button
          icon="pi pi-times"
          @click="close"
          class="p-button-danger ml-2"
          v-tooltip.top="$t('globals.close')"
        />
      </div>
    </template>
  </Toolbar>

</template>

<script>
import { mapActions, mapState } from 'vuex';
import { FACEBOOK_LOCALSTORAGE_EVENTS } from '@/globals/agent/facebook';

export default {
    inject: ['$helpers'],
    props: {
        isExpired: {
            type: Boolean,
            default: false
        },
        viewAsReport: {
            type: Boolean,
            default: false
        }
    },
    data () {
        return {
            attachOptions: [
                {
                    label: this.$tc('globals.media.image', 2),
                    icon: 'pi pi-image',
                    command: () => {
                        this.attach();
                    }
                },
                {
                    label: this.$tc('globals.media.doc', 2),
                    icon: 'pi pi-file-pdf',
                    command: () => {
                        this.attach('pdf');
                    }
                }
            ],
            settingOptions: [
                {
                    label: this.$t('views.whatsapp.contact.settings.edit_info'),
                    icon: 'pi pi-user-edit',
                    command: () => {
                        this.editUserInfo();
                    }
                },
                {
                    label: this.$t('views.whatsapp.contact.settings.show_info'),
                    icon: 'pi pi-info-circle',
                    command: () => {
                        this.showUserInfo();
                    }
                }
            ],
            conversationId: null,
            clientInfo: {
                name: '',
                page_client_id: '',
                avatar:
          'https://www.primefaces.org/wp-content/uploads/2020/05/placeholder.png'
            }
        };
    },
    computed: {
        ...mapState(['agtFacebookConversationInfo', 'agtFacebookConversationMessages']),
        areConversationActionsDisabled () {
            return Boolean(this.agtFacebookConversationInfo?.isDisposition);
        }
    },
    methods: {
        ...mapActions(['agtFacebookSetConversationMessages']),
        back () {
            this.$router.push({ name: 'agent_facebook' });
        },
        templates () {
            localStorage.setItem(
                'agtFacebookConversationMessages',
                JSON.stringify(this.agtFacebookConversationMessages)
            );
            localStorage.setItem(
                'agtFacebookConversationInfo',
                JSON.stringify(this.agtFacebookConversationInfo)
            );
            localStorage.setItem('onlyFacebookTemplates', false);
            const event = new Event(
                FACEBOOK_LOCALSTORAGE_EVENTS.TEMPLATES_INIT_EVENT
            );
            window.parent.document.dispatchEvent(event);
            const modalEvent = new CustomEvent('onFacebookTemplatesEvent', {
                detail: {
                    templates: true,
                    conversationId: parseInt(this.$route.params.id)
                }
            });
            window.parent.document.dispatchEvent(modalEvent);
        },
        attach (fileType = 'img') {
            localStorage.setItem(
                'agtFacebookConversationMessages',
                JSON.stringify(this.agtFacebookConversationMessages)
            );
            localStorage.setItem(
                'agtFacebookConversationInfo',
                JSON.stringify(this.agtFacebookConversationInfo)
            );
            const event = new CustomEvent('onFacebookMediaFormEvent', {
                detail: {
                    media_form: true,
                    fileType: fileType
                }
            });
            window.parent.document.dispatchEvent(event);
        },
        showUserInfo () {
            const event = new CustomEvent('onFacebookUserInfoEvent', {
                detail: {
                    user_info: true
                }
            });
            window.parent.document.dispatchEvent(event);
        },
        editUserInfo () {
            localStorage.setItem('agtFacebookInconmingConversation', false);
            localStorage.setItem(
                'agtFacebookConversationInfo',
                JSON.stringify(this.agtFacebookConversationInfo)
            );
            const event = new Event(
                FACEBOOK_LOCALSTORAGE_EVENTS.CONTACT.FORM_INIT_DATA
            );
            const modalEvent = new CustomEvent('onFacebookContactFormEvent', {
                detail: {
                    contact_form: true
                }
            });
            window.parent.document.dispatchEvent(event);
            window.parent.document.dispatchEvent(modalEvent);
        },
        qualify () {
            localStorage.setItem(
                'agtFacebookConversationInfo',
                JSON.stringify(this.agtFacebookConversationInfo)
            );
            localStorage.setItem(
                'agtFacebookDispositionChatFormToCreate',
                !this.agtFacebookConversationInfo.isDisposition
            );
            const event = new Event(
                FACEBOOK_LOCALSTORAGE_EVENTS.DISPOSITION.FORM_INIT_DATA
            );
            window.parent.document.dispatchEvent(event);
            const modalEvent = new CustomEvent('onFacebookDispositionFormEvent', {
                detail: {
                    disposition_form: true
                }
            });
            window.parent.document.dispatchEvent(modalEvent);
        },
        transfer () {
            localStorage.setItem(
                'agtFacebookConversationInfo',
                JSON.stringify(this.agtFacebookConversationInfo)
            );
            const event = new Event(
                FACEBOOK_LOCALSTORAGE_EVENTS.TRANSFER.FORM_INIT_DATA
            );
            window.parent.document.dispatchEvent(event);
            const modalEvent = new CustomEvent('onFacebookTransferChatEvent', {
                detail: {
                    transfer_chat: true
                }
            });
            window.parent.document.dispatchEvent(modalEvent);
        },
        close () {
            const event = new CustomEvent('onFacebookCloseContainerEvent', {
                detail: {
                    facebook_container: false
                }
            });
            window.parent.document.dispatchEvent(event);
        }
    },
    watch: {
        agtFacebookConversationInfo: {
            handler () {
                if (this.agtFacebookConversationInfo) {
                    if (this.agtFacebookConversationInfo.client.id) {
                        this.clientInfo.name = this.agtFacebookConversationInfo.client.data.nombre || this.agtFacebookConversationInfo.client.data.name || '';
                        this.clientInfo.page_client_id = this.agtFacebookConversationInfo.client.page_client_id;
                    } else {
                        this.clientInfo.name = this.agtFacebookConversationInfo.client_alias || '';
                        this.clientInfo.page_client_id = this.agtFacebookConversationInfo.page_client_id;
                    }
                }
            },
            deep: true,
            immediate: true
        },
        agtFacebookConversationMessages: {
            handler () {
                console.log('agtFacebookConversationMessages changed');
            },
            deep: true,
            immediate: true
        },
        isExpired: {
            handler () {},
            deep: true,
            immediate: true
        },
        viewAsReport: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
