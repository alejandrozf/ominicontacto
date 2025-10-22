<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $tc("globals.whatsapp.message_template", 2) }}</h1>
      </template>
    </Toolbar>
    <MessageTemplatesTable @handleModalEvent="handleModal" />
    <ModalToHandleMessageTemplate
      :showModal="showModal"
      :formToCreate="formToCreate"
      @handleModalEvent="handleModal"
    />
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import MessageTemplatesTable from '@/components/supervisor/whatsapp/message_templates/MessageTemplatesTable';
import ModalToHandleMessageTemplate from '@/components/supervisor/whatsapp/message_templates/ModalToHandleMessageTemplate';

export default {
    data () {
        return {
            showModal: false,
            formToCreate: false
        };
    },
    components: {
        MessageTemplatesTable,
        ModalToHandleMessageTemplate
    },
    async created () {
        await this.initWhatsappMessageTemplates();
    },
    methods: {
        handleModal ({
            showModal = false,
            formToCreate = true,
            messageTemplate = null
        }) {
            this.showModal = showModal;
            this.formToCreate = formToCreate;
            this.initWhatsappMessageTemplate({ messageTemplate });
            if (messageTemplate) {
                this.initWhatsappMessageTemplateFormFields({ type: messageTemplate.tipo, config: messageTemplate.configuracion });
            } else {
                this.initWhatsappMessageTemplateFormFields({});
            }
        },
        ...mapActions([
            'initWhatsappMessageTemplate',
            'initWhatsappMessageTemplates',
            'initWhatsappMessageTemplateFormFields'
        ])
    }
};
</script>
