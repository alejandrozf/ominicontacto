<template>
  <Toolbar>
    <template #start>
      <Button
        v-if="!viewAsReport"
        @click="back"
        v-tooltip.top="$t('globals.back')"
        icon="pi pi-arrow-left"
        class="p-button-rounded p-button-secondary p-button-text"
      />
      <Chip
        :label="clientInfo?.name + ' (' + clientInfo?.phone + ')'"
        icon="pi pi-user"
      />
    </template>
    <template #end>
      <div v-if="!viewAsReport && !agtWhatsCoversationInfo.error">
        <SplitButton
        icon="pi pi-paperclip"
        :model="attachOptions"
        v-tooltip.top="$t('globals.attach')"
        class="p-button-warning"
      />
        <Button
          v-if="!isExpired"
          icon="pi pi-arrows-h"
          class="p-button-secondary ml-2"
          @click="transfer"
          v-tooltip.top="$t('globals.transfer')"
        />
        <Button
          v-if="agtWhatsCoversationInfo.client.id"
          icon="pi pi-save"
          class="ml-2"
          @click="qualify"
          v-tooltip.top="$t('globals.save')"
        />
        <Button
          v-if="!isExpired"
          icon="pi pi-copy"
          class="p-button-info ml-2"
          @click="templates"
          v-tooltip.top="$tc('globals.whatsapp.template', 2)"
        />
        <Button
          v-if="agtWhatsCoversationInfo.client.id"
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
      <div v-if="!viewAsReport && agtWhatsCoversationInfo.error">
        <Button
          v-if="agtWhatsCoversationInfo.client.id"
          icon="pi pi-save"
          class="ml-2"
          @click="qualify"
          v-tooltip.top="$t('globals.save')"
        />
      </div>
    </template>
  </Toolbar>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { WHATSAPP_LOCALSTORAGE_EVENTS } from '@/globals/agent/whatsapp';

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
                phone: '',
                avatar:
          'https://www.primefaces.org/wp-content/uploads/2020/05/placeholder.png'
            }
        };
    },
    computed: {
        ...mapState(['agtWhatsCoversationInfo', 'agtWhatsCoversationMessages'])
    },
    methods: {
        ...mapActions(['agtWhatsSetCoversationMessages']),
        back () {
            this.$router.push({ name: 'agent_whatsapp' });
        },
        templates () {
            if (this.$helpers.isSocketConnected(this.$t)) {
                localStorage.setItem(
                    'agtWhatsappConversationMessages',
                    JSON.stringify(this.agtWhatsCoversationMessages)
                );
                localStorage.setItem(
                    'agtWhatsCoversationInfo',
                    JSON.stringify(this.agtWhatsCoversationInfo)
                );
                localStorage.setItem('onlyWhatsappTemplates', false);
                const event = new Event(
                    WHATSAPP_LOCALSTORAGE_EVENTS.TEMPLATES_INIT_EVENT
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
        },
        attach (fileType = 'img') {
            localStorage.setItem(
                    'agtWhatsappConversationMessages',
                    JSON.stringify(this.agtWhatsCoversationMessages)
            );
            localStorage.setItem(
                'agtWhatsCoversationInfo',
                JSON.stringify(this.agtWhatsCoversationInfo)
            );
            const event = new CustomEvent('onWhatsappMediaFormEvent', {
                detail: {
                    media_form: true,
                    fileType: fileType,
                }
            });
            window.parent.document.dispatchEvent(event);
        },
        showUserInfo () {
            const event = new CustomEvent('onWhatsappUserInfoEvent', {
                detail: {
                    user_info: true
                }
            });
            window.parent.document.dispatchEvent(event);
        },
        editUserInfo () {
            localStorage.setItem('agtWhatsInconmingConversation', false);
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
        qualify () {
            localStorage.setItem(
                'agtWhatsCoversationInfo',
                JSON.stringify(this.agtWhatsCoversationInfo)
            );
            localStorage.setItem(
                'agtWhatsDispositionChatFormToCreate',
                this.agtWhatsCoversationInfo.client.dispositionId === null
            );
            const event = new Event(
                WHATSAPP_LOCALSTORAGE_EVENTS.DISPOSITION.FORM_INIT_DATA
            );
            window.parent.document.dispatchEvent(event);
            const modalEvent = new CustomEvent('onWhatsappDispositionFormEvent', {
                detail: {
                    disposition_form: true
                }
            });
            window.parent.document.dispatchEvent(modalEvent);
        },
        transfer () {
            localStorage.setItem(
                'agtWhatsCoversationInfo',
                JSON.stringify(this.agtWhatsCoversationInfo)
            );
            const event = new Event(
                WHATSAPP_LOCALSTORAGE_EVENTS.TRANSFER.FORM_INIT_DATA
            );
            window.parent.document.dispatchEvent(event);
            const modalEvent = new CustomEvent('onWhatsappTransferChatEvent', {
                detail: {
                    transfer_chat: true
                }
            });
            window.parent.document.dispatchEvent(modalEvent);
        },
        close () {
            const event = new CustomEvent('onWhatsappCloseContainerEvent', {
                detail: {
                    whatsapp_container: false
                }
            });
            window.parent.document.dispatchEvent(event);
        }
    },
    watch: {
        agtWhatsCoversationInfo: {
            handler () {
                if (this.agtWhatsCoversationInfo) {
                    if (this.agtWhatsCoversationInfo.client.id) {
                        this.clientInfo.name =
              this.agtWhatsCoversationInfo.client.data.nombre ||
              this.agtWhatsCoversationInfo.client_alias
                        this.clientInfo.phone = this.agtWhatsCoversationInfo.client.phone;
                    } else {
                        this.clientInfo.name = this.agtWhatsCoversationInfo.client_alias;
                        this.clientInfo.phone = this.agtWhatsCoversationInfo.destination;
                    }
                }
            },
            deep: true,
            immediate: true
        },
        agtWhatsCoversationMessages: {
            handler () {},
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
