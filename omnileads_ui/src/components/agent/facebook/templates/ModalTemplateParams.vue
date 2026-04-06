<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '70vw' }"
    :closable="false"
    :modal="false"
  >
    <template #header>
      <h2>
        {{
          $t("models.whatsapp.templates.whatsapp_template") +
          `: (${template.name})`
        }}
      </h2>
    </template>
    <ParamsForm
      @closeModalEvent="closeModal"
      :template="template"
      :onlyFacebookTemplates="onlyFacebookTemplates"
    />
  </Dialog>
</template>

<script>
import { mapActions } from 'vuex';
import ParamsForm from '@/components/agent/facebook/templates/ParamsForm';

export default {
    props: {
        showModal: {
            type: Boolean,
            default: false
        },
        onlyFacebookTemplates: {
            type: Boolean,
            default: false
        },
        template: {
            type: Object,
            default: () => {
                return {
                    id: null,
                    name: '',
                    configuration: {
                        text_header: '',
                        text: '',
                        type: '',
                        numParams_header: 0,
                        numParams_text: 0
                    }
                };
            }
        }
    },
    components: {
        ParamsForm
    },
    methods: {
        closeModal () {
            this.$emit('handleModalEvent', {});
            const event = new CustomEvent('onFacebookTemplatesEvent', {
                detail: {
                    templates: false,
                    conversationId: null
                }
            });
            window.parent.document.dispatchEvent(event);
        }
    },
    watch: {
        showModal: {
            handler () {},
            deep: true,
            immediate: true
        },
        template: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
