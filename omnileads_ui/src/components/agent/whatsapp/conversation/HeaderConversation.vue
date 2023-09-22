<template>
  <Toolbar>
    <template #start>
    <Button
        @click="back"
        v-tooltip.top="$t('globals.back')"
        icon="pi pi-arrow-left"
        class="p-button-rounded p-button-secondary p-button-text"
    />
    <Chip
        :label="clientInfo?.name"
        icon="pi pi-user"
    />
    </template>
    <template #end>
      <!-- <SplitButton
        icon="pi pi-paperclip"
        :model="attachOptions"
        v-tooltip.top="$t('globals.attach')"
        class="p-button-warning"
        disabled
      />
      <Button
        icon="pi pi-save"
        class="ml-2"
        @click="save"
        v-tooltip.top="$t('globals.save')"
        disabled
      />
      <Button
        icon="pi pi-arrows-h"
        class="p-button-secondary ml-2"
        @click="transfer"
        v-tooltip.top="$t('globals.transfer')"
        disabled
      /> -->
      <Button
        icon="pi pi-copy"
        class="p-button-info ml-2"
        @click="templates"
        v-tooltip.top="$tc('globals.whatsapp.template', 2)"
      />
      <Button
        icon="pi pi-times"
        @click="close"
        class="p-button-danger ml-2"
        v-tooltip.top="$t('globals.close')"
      />
    </template>
  </Toolbar>
</template>

<script>
import { mapActions, mapState } from 'vuex';
export default {
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
            conversationId: null,
            clientInfo: {
                name: '',
                phone: '',
                avatar: 'https://www.primefaces.org/wp-content/uploads/2020/05/placeholder.png'
            }
        };
    },
    computed: {
        ...mapState(['agtWhatsCoversationInfo', 'agtWhatsCoversationMessages'])
    },
    methods: {
        ...mapActions(['agtWhatsTransferChatInitData', 'agtWhatsSetCoversationId', 'agtWhatsSetCoversationMessages', 'agtWhatsSetCoversationCampaignId']),
        back () {
            this.$router.push({ name: 'agent_whatsapp' });
        },
        templates () {
            localStorage.setItem('agtWhatsappConversationMessages', JSON.stringify(this.agtWhatsCoversationMessages));
            localStorage.setItem('agtWhatsCoversationCampaignId', this.agtWhatsCoversationInfo.campaignId);
            const event = new CustomEvent('onWhatsappTemplatesEvent', {
                detail: {
                    templates: true,
                    conversationId: parseInt(this.$route.params.id)
                }
            });
            window.parent.document.dispatchEvent(event);
        },
        attach (fileType = 'img') {
            const event = new CustomEvent('onWhatsappMediaFormEvent', {
                detail: {
                    media_form: true,
                    fileType
                }
            });
            window.parent.document.dispatchEvent(event);
        },
        save () {
            const event = new CustomEvent('onWhatsappDispositionFormEvent', {
                detail: {
                    disposition_form: true
                }
            });
            window.parent.document.dispatchEvent(event);
        },
        async transfer () {
            await this.agtWhatsTransferChatInitData(1);
            const event = new CustomEvent('onWhatsappTransferChatEvent', {
                detail: {
                    transfer_chat: true
                }
            });
            window.parent.document.dispatchEvent(event);
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
                    this.clientInfo.name = this.agtWhatsCoversationInfo.client ? this.agtWhatsCoversationInfo.client.name : this.agtWhatsCoversationInfo.destination;
                    this.clientInfo.phone = this.agtWhatsCoversationInfo.client ? this.agtWhatsCoversationInfo.client.phone : this.agtWhatsCoversationInfo.destination;
                }
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
