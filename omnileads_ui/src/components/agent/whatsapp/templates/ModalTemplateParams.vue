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
            `Template de Whatsapp: (${template.name})`
        }}
      </h2>
    </template>
    <ParamsForm @closeModalEvent="closeModal" :template="template" />
  </Dialog>
</template>

<script>
import { mapActions } from 'vuex';
import ParamsForm from '@/components/agent/whatsapp/templates/ParamsForm';

export default {
    props: {
        showModal: {
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
                        text: '',
                        type: '',
                        numParams: 0
                    }
                };
            }
        }
    },
    components: {
        ParamsForm
    },
    methods: {
        ...mapActions(['initWhatsappProvider']),
        closeModal () {
            this.$emit('handleModalEvent', {});
            const event = new CustomEvent('onWhatsappTemplatesEvent', {
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
