<template>
  <div class="card">
    <div class="grid formgrid">
      <div v-for="(field, index) in form" :key="index" class="field col-12">
        <label
          :class="{
            'p-error': isEmptyField(field.value) && submitted,
          }"
          >{{ field.name }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <InputText
            :class="{
              'p-invalid': isEmptyField(field.value) && submitted,
            }"
            v-model="field.value"
          />
        </div>
        <small v-if="isEmptyField(field.value) && submitted" class="p-error">{{
          $t("globals.validations.field_is_required", {
            field: field.name,
          })
        }}</small>
      </div>
    </div>
    <Panel header="Vista previa" class="field col-12 bg-green-200">
        <p class="m-0">
            {{ getPreviewMessage }}
        </p>
    </Panel>
    <div class="flex justify-content-end flex-wrap mt-2">
      <div class="flex align-items-center">
        <Button
          class="p-button-danger p-button-outlined mr-2"
          :label="$t('globals.cancel')"
          @click="closeModal()"
        />
        <Button :label="$t('globals.send')" icon="pi pi-send" @click="send()" />
      </div>
    </div>
  </div>
</template>

<script>
import { FilterMatchMode } from 'primevue/api';
import { mapActions, mapState } from 'vuex';
import { HTTP_STATUS } from '@/globals';
import { notificationEvent, NOTIFICATION } from '@/globals/agent/whatsapp';

export default {
    inject: ['$helpers'],
    props: {
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
    data () {
        return {
            form: {},
            submitted: false,
            filters: null,
            invalidForm: false,
            previewMessage: '',
            conversationId: null
        };
    },
    async created () {
        await this.initializeData();
    },
    computed: {
        ...mapState(['agtWhatsCoversationId', 'agtWhatsCoversationInfo']),
        getPreviewMessage () {
            if (!this.template.configuration || this.form === {}) return this.template.configuration.text || '';
            const self = this;
            return this.template.configuration.text.replace(/{{(\d+)}}/g, function (match, numero) {
                const field = self.form[`param_${numero}`];
                return field.value || `${match}`;
            });
        }
    },
    methods: {
        ...mapActions(['agtWhatsCoversationSendWhatsappTemplateMessage']),
        initializeData () {
            this.initFormData();
            this.submitted = false;
        },
        closeModal () {
            this.clearForm();
            this.$emit('closeModalEvent');
            this.form = {};
        },
        clearForm () {
            for (const clave in this.form) {
                const field = this.form[clave];
                field.value = null;
            }
            this.submitted = false;
        },
        initFormData () {
            this.form = {};
            for (let i = 0; i < this.template.configuration.numParams; i++) {
                const name = `param_${i + 1}`;
                this.form[name] = { name, empty: false, value: null };
            }
        },
        clearFilter () {
            this.initFilters();
        },
        initFilters () {
            this.filters = {
                global: { value: null, matchMode: FilterMatchMode.CONTAINS }
            };
        },
        isEmptyField (field = null) {
            return field === null || field === undefined || field === '';
        },
        getFormData () {
            const formData = [];
            for (const clave in this.form) {
                const field = this.form[clave];
                formData.push(field.value);
            }
            return formData;
        },
        async send () {
            try {
                this.submitted = true;
                this.invalidForm = false;
                for (const clave in this.form) {
                    const field = this.form[clave];
                    if (this.isEmptyField(field.value)) {
                        this.invalidForm = true;
                        this.form[`${field.name}`].empty = true;
                    } else {
                        this.form[`${field.name}`].empty = false;
                    }
                }
                if (this.invalidForm) return null;
                const result = await this.agtWhatsCoversationSendWhatsappTemplateMessage({
                    conversationId: this.agtWhatsCoversationId,
                    templateId: this.template.id,
                    phoneLine: this.agtWhatsCoversationInfo.lineNumber,
                    params: this.getFormData()
                });
                this.closeModal();
                const { status, message } = result;
                if (status === HTTP_STATUS.SUCCESS) {
                    await notificationEvent(
                        NOTIFICATION.TITLES.SUCCESS,
                        message,
                        NOTIFICATION.ICONS.SUCCESS
                    );
                } else {
                    await notificationEvent(
                        NOTIFICATION.TITLES.ERROR,
                        message,
                        NOTIFICATION.ICONS.ERROR
                    );
                }
            } catch (error) {
                console.error('ERROR Al crear al enviar template');
                console.error(error);
                await notificationEvent(
                    NOTIFICATION.TITLES.ERROR,
                    this.$t('globals.error_to_process_form'),
                    NOTIFICATION.ICONS.ERROR
                );
            }
        }
    },
    watch: {
        template: {
            handler () {
                if (this.template) {
                    this.initFormData();
                }
            },
            deep: true,
            immediate: true
        },
        agtWhatsCoversationId: {
            handler () {},
            deep: true,
            immediate: true
        },
        agtWhatsCoversationInfo: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
