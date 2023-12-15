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
      :contactPhone="contactPhone"
      :campaignId="campaignId"
    />
  </Dialog>
</template>

<script>
import { mapActions } from 'vuex';
import ParamsForm from '@/components/agent/whatsapp/conversation/new/ParamsForm';

export default {
    props: {
        showModal: {
            type: Boolean,
            default: false
        },
        contactPhone: {
            type: String,
            default: ''
        },
        campaignId: {
            type: Number,
            default: null
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
        ...mapActions(['']),
        closeModal (response) {
            this.$emit('handleModalEvent', { response });
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
        },
        contactPhone: {
            handler () {},
            deep: true,
            immediate: true
        },
        campaignId: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
