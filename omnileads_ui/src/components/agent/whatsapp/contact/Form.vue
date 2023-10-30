<template>
  <div class="card">
    <div class="grid formgrid mt-4">
      <div v-for="(field, index) in form" :key="index" class="field col-12">
        <div v-if="field.name !== 'id'">
          <div v-if="field.mandatory">
            <label
              v-if="field.is_phone_field"
              :class="{
                'p-error':
                  (isEmptyField(field.value) || !isPhoneValid(field.value)) &&
                  submitted,
              }"
              >{{ field.name }}*</label
            >
            <label
              v-else
              :class="{
                'p-error': isEmptyField(field.value) && submitted,
              }"
              >{{ field.name }}*</label
            >
            <div class="p-inputgroup mt-2">
              <span class="p-inputgroup-addon">
                <i v-if="field.is_phone_field" class="pi pi-phone"></i>
                <i v-else class="pi pi-list"></i>
              </span>
              <InputText
                v-if="field.is_phone_field"
                :class="{
                  'p-invalid':
                    (isEmptyField(field.value) || !isPhoneValid(field.value)) &&
                    submitted,
                }"
                v-model="field.value"
              />
              <InputText
                v-else
                :class="{
                  'p-invalid': isEmptyField(field.value) && submitted,
                }"
                v-model="field.value"
              />
            </div>
            <div v-if="isEmptyField(field.value) && submitted">
              <small class="p-error">{{
                $t("forms.whatsapp.contact.validations.field_is_required", {
                  field: field.name,
                })
              }}</small>
              <br />
            </div>
            <small
              v-if="
                field.is_phone_field && !isPhoneValid(field.value) && submitted
              "
              class="p-error"
              >{{
                $t("forms.whatsapp.contact.validations.invalid_field", {
                  field: field.name,
                })
              }}</small
            >
          </div>
          <div v-else>
            <label
              v-if="field.is_phone_field"
              :class="{
                'p-error':
                  field.mandatory && !isPhoneValid(field.value) && submitted,
              }"
              >{{ field.name }}</label
            >
            <label v-else>{{ field.name }}</label>
            <div class="p-inputgroup mt-2">
              <span class="p-inputgroup-addon">
                <i v-if="field.is_phone_field" class="pi pi-phone"></i>
                <i v-else class="pi pi-list"></i>
              </span>
              <InputText
                v-if="field.is_phone_field"
                :class="{
                  'p-invalid':
                    field.mandatory && !isPhoneValid(field.value) && submitted,
                }"
                v-model="field.value"
              />
              <InputText v-else v-model="field.value" />
            </div>
            <small
              v-if="
                field.mandatory &&
                field.is_phone_field &&
                !isPhoneValid(field.value) &&
                submitted
              "
              class="p-error"
              >{{
                $t("forms.whatsapp.contact.validations.invalid_field", {
                  field: field.name,
                })
              }}</small
            >
          </div>
        </div>
      </div>
    </div>
    <div class="flex justify-content-end flex-wrap">
      <div class="flex align-items-center">
        <Button
          class="p-button-danger p-button-outlined mr-2"
          :label="$t('globals.cancel')"
          @click="closeModal()"
        />
        <Button :label="$t('globals.save')" icon="pi pi-save" @click="save()" />
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
        formToCreate: {
            type: Boolean,
            default: true
        }
    },
    data () {
        return {
            form: {},
            submitted: false,
            filters: null,
            invalidForm: false,
            contact: {
                id: null,
                phone: '',
                data: []
            }
        };
    },
    async created () {
        await this.initializeData();
    },
    computed: {
        ...mapState(['agtWhatsContactDBFields', 'agtWhatsCoversationInfo'])
    },
    methods: {
        ...mapActions([
            'agtWhatsContactCreate',
            'agtWhatsContactUpdate',
            'agtWhatsSetCoversationClientInfo'
        ]),
        initializeData () {
            this.initFormData();
            this.submitted = false;
        },
        closeModal () {
            this.clearForm();
            this.$emit('clearForm');
            const event = new CustomEvent('onWhatsappContactFormEvent', {
                detail: {
                    contact_form: false
                }
            });
            window.parent.document.dispatchEvent(event);
        },
        clearForm () {
            for (const clave in this.form) {
                const field = this.form[clave];
                field.value = null;
            }
            this.submitted = false;
        },
        initFormData () {
            if (this.agtWhatsContactDBFields.length > 0) {
                this.form = {};
                for (let i = 0; i < this.agtWhatsContactDBFields.length; i++) {
                    const field = this.agtWhatsContactDBFields[i];
                    let value = null;
                    if (i === 0) {
                        value = this.contact.phone;
                    } else {
                        value = this.contact.id ? this.contact.data[i - 1] : null;
                    }
                    this.form[`${field.name}`] = {
                        ...field,
                        empty: false,
                        value,
                        invalid: false
                    };
                }
                this.form.id = {
                    name: 'id',
                    mandatory: false,
                    block: false,
                    hide: false,
                    is_phone_field: false,
                    invalid: false,
                    empty: false,
                    value: this.contact.id
                };
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
        isPhoneValid (phone = null) {
            return this.$helpers.isPhoneValid(phone);
        },
        getFormData () {
            const formData = {};
            for (const clave in this.form) {
                const field = this.form[clave];
                if (field.name !== 'id') {
                    formData[`${field.name}`] = field.value;
                }
            }
            return formData;
        },
        async save () {
            try {
                this.submitted = true;
                this.invalidForm = false;
                for (const clave in this.form) {
                    const field = this.form[clave];
                    this.form[`${field.name}`].empty = false;
                    this.form[`${field.name}`].invalid = false;
                    if (field.name !== 'id') {
                        if (field.mandatory) {
                            if (this.isEmptyField(field.value)) {
                                this.invalidForm = true;
                                this.form[`${field.name}`].empty = true;
                            } else if (
                                field.is_phone_field &&
                !this.isPhoneValid(field.value)
                            ) {
                                this.invalidForm = true;
                                this.form[`${field.name}`].invalid = true;
                            }
                        } else if (
                            field.is_phone_field &&
              !this.isPhoneValid(field.value)
                        ) {
                            this.form[`${field.name}`].invalid = true;
                        }
                    }
                }
                if (this.invalidForm) return null;
                let response = null;
                this.$swal.fire({
                    title: this.$t('globals.processing_request'),
                    timerProgressBar: true,
                    allowOutsideClick: false,
                    didOpen: () => {
                        this.$swal.showLoading();
                    }
                });
                if (this.formToCreate) {
                    response = await this.agtWhatsContactCreate({
                        campaignId: this.agtWhatsCoversationInfo.campaignId,
                        conversationId: this.agtWhatsCoversationInfo.id,
                        data: this.getFormData()
                    });
                } else {
                    response = await this.agtWhatsContactUpdate({
                        campaignId: this.agtWhatsCoversationInfo.campaignId,
                        conversationId: this.agtWhatsCoversationInfo.id,
                        data: this.getFormData(),
                        contactId: this.form.id.value
                    });
                }
                this.$swal.close();
                this.closeModal();
                const { status, message } = response;
                if (status === HTTP_STATUS.SUCCESS) {
                    await this.agtWhatsSetCoversationClientInfo(response.data);
                    window.parent.postMessage(
                        { type: 'refreshConversationInfo', data: null },
                        '*'
                    );
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
                console.error('ERROR Al crear contacto');
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
        agtWhatsContactDBFields: {
            handler () {
                if (this.agtWhatsContactDBFields.length > 0) {
                    this.initFormData();
                }
            },
            deep: true,
            immediate: true
        },
        agtWhatsCoversationInfo: {
            handler () {
                if (this.agtWhatsCoversationInfo.client) {
                    this.contact.id = this.agtWhatsCoversationInfo.client.id || null;
                    this.contact.phone = this.agtWhatsCoversationInfo.client.phone || '';
                    this.contact.data = this.agtWhatsCoversationInfo.client.data
                        ? JSON.parse(this.agtWhatsCoversationInfo.client.data)
                        : [];
                }
                this.initFormData();
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
