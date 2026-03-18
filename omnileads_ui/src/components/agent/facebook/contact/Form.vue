<template>
  <div class="card">
    <div class="grid formgrid mt-4">
      <div
        v-for="(field, index) in form"
        :key="index"
        class="field sm:col-12 md:col-6 lg:col-6 xl:col-6"
      >
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
                :disabled="isFieldReadonly(field)"
                :readonly="isFieldReadonly(field)"
              />
              <InputText
                v-else
                :class="{
                  'p-invalid': isEmptyField(field.value) && submitted,
                }"
                v-model="field.value"
                :disabled="isFieldReadonly(field)"
                :readonly="isFieldReadonly(field)"
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
                :disabled="isFieldReadonly(field)"
                :readonly="isFieldReadonly(field)"
              />
              <InputText
                v-else
                v-model="field.value"
                :disabled="isFieldReadonly(field)"
                :readonly="isFieldReadonly(field)"
              />
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
import {
    notificationEvent,
    NOTIFICATION,
    FACEBOOK_LOCALSTORAGE_EVENTS
} from '@/globals/agent/facebook';
export default {
    inject: ['$helpers'],
    props: {
        formToCreate: {
            type: Boolean,
            default: true
        },
        formToCreateFromNewConversation: {
            type: Boolean,
            default: false
        },
        previewContact: {
            type: Object,
            default: () => {
                return {
                    id: null,
                    phone: '',
                    page_client_id: '',
                    data: []
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
            contact: {
                id: null,
                phone: '',
                page_client_id: '',
                data: []
            }
        };
    },
    async created () {
        await this.initializeData();
    },
    computed: {
        ...mapState(['agtFacebookContactDBFields', 'agtFacebookConversationInfo'])
    },
    methods: {
        ...mapActions([
            'agtFacebookContactCreateFromConversation',
            'agtFacebookContactCreate',
            'agtFacebookContactUpdate'
        ]),
        initializeData () {
            this.initFormData();
            this.submitted = false;
        },
        closeModal () {
            this.clearForm();
            this.$emit('clearForm');
            this.$emit('cleanFilterSearchEvent');
            this.$emit('closeModalEvent');
            const event = new CustomEvent('onFacebookContactFormEvent', {
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
            if (this.agtFacebookContactDBFields?.length > 0) {
                this.form = {};
                for (let i = 0; i < this.agtFacebookContactDBFields.length; i++) {
                    const field = this.agtFacebookContactDBFields[i];
                    let value = null;
                    if (i === 0) {
                        value = this.contact?.phone;
                    } else {
                        value = this.contact?.id ? this.contact?.data[field.name] : null;
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
                    value: this.contact?.id
                };
                this.form.page_client_id = {
                    name: 'page_client_id',
                    mandatory: true,
                    block: true,
                    hide: false,
                    is_phone_field: false,
                    invalid: false,
                    empty: false,
                    value: this.contact?.page_client_id
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
        isFieldReadonly (field = {}) {
            return field.block === true || field.name === 'page_client_id';
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
                    this.form[`${field?.name}`].empty = false;
                    this.form[`${field?.name}`].invalid = false;
                    if (field?.name !== 'id') {
                        if (field?.mandatory) {
                            if (this.isEmptyField(field?.value)) {
                                this.invalidForm = true;
                                this.form[`${field?.name}`].empty = true;
                            } else if (
                field?.is_phone_field &&
                !this.isPhoneValid(field?.value)
                            ) {
                                this.invalidForm = true;
                                this.form[`${field?.name}`].invalid = true;
                            }
                        } else if (
              field?.is_phone_field &&
              !this.isPhoneValid(field?.value)
                        ) {
                            this.form[`${field?.name}`].invalid = true;
                        }
                    }
                }
                if (this.invalidForm) return null;
                let response = null;
                this.$helpers.openLoader(this.$t);
                const formData = {
                    campaignId: this.agtFacebookConversationInfo.campaignId,
                    conversationId: this.agtFacebookConversationInfo.id,
                    data: this.getFormData(),
                    contactId: null
                };
                if (this.formToCreate && this.formToCreate != null) {
                    response = await this.agtFacebookContactCreateFromConversation(formData);
                }else if(this.formToCreateFromNewConversation != null && this.formToCreateFromNewConversation) {
                  const formData = {
                    campaignId: localStorage.getItem('agtFacebookCampaingId'),
                    fdata: this.getFormData(),
                  };
                  console.log("formData >>", formData)
                  response = await this.agtFacebookContactCreate(formData);
                }
                else {
                    formData.contactId = this.form.id.value;
                    response = await this.agtFacebookContactUpdate(formData);
                }
                this.$helpers.closeLoader();
                this.closeModal();
                const { status, message } = response;
                if (status === HTTP_STATUS.SUCCESS) {
                    let contacts = []
                    contacts.push(JSON.stringify(response.data))
                    localStorage.setItem(
                        'newContant',
                        contacts
                    );
                    const event = new Event(
                        FACEBOOK_LOCALSTORAGE_EVENTS.CONVERSATION.DETAIL_INIT_DATA
                    );
                    window.parent.document.dispatchEvent(event);
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
        agtFacebookContactDBFields: {
            handler () {
                if (this.agtFacebookContactDBFields.length > 0) {
                    this.initFormData();
                }
            },
            deep: true,
            immediate: true
        },
        agtFacebookConversationInfo: {
            handler () {
                console.log("agtFacebookConversationInfo >>2", this.agtFacebookConversationInfo);
                if (this.agtFacebookConversationInfo.client.id !== null) {
                    this.contact.id = this.agtFacebookConversationInfo.client.id;
                    this.contact.phone =
                        this.agtFacebookConversationInfo.client.phone || '';
                    this.contact.page_client_id = this.agtFacebookConversationInfo.client.page_client_id || this.agtFacebookConversationInfo.page_client_id;
                    this.contact.data = this.agtFacebookConversationInfo.client.data || [];
                } else {
                    if (this.agtFacebookConversationInfo.page_client_id !== null) {
                        this.contact.id = null;
                        this.contact.phone = '';
                        this.contact.page_client_id = this.agtFacebookConversationInfo.page_client_id;
                        this.contact.data = [];
                    }
                }
                this.initFormData();
            },
            deep: true,
            immediate: true
        },
        previewContact: {
            handler () {
                this.contact.id = this.previewContact?.id || null;
                this.contact.page_client_id = this.previewContact?.page_client_id || '';
                this.contact.phone = this.previewContact?.phone || '';
                this.contact.data = this.previewContact?.data || [];
                this.initFormData();
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
