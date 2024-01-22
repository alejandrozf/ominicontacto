<template>
  <div class="card">
    <div class="grid formgrid mt-1">
      <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
        <label
          :class="{
            'p-error': v$.form.dispositionOption.$invalid && submitted,
          }"
          >{{ $t("models.whatsapp.disposition_form.disposition_option") }} *
        </label>
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <Dropdown
            v-model="v$.form.dispositionOption.$model"
            class="w-full"
            :class="{
              'p-invalid': v$.form.dispositionOption.$invalid && submitted,
            }"
            @change="getFormFieldsByOption"
            :options="dispositionOptions"
            placeholder="-----"
            optionLabel="name"
            optionValue="id"
            optionGroupLabel="label"
            optionGroupChildren="items"
            :emptyFilterMessage="$t('globals.without_data')"
            :filter="true"
            v-bind:filterPlaceholder="
              $t('globals.find_by', { field: $tc('globals.name') }, 1)
            "
          />
        </div>
        <small
          v-if="
            (v$.form.dispositionOption.$invalid && submitted) ||
            v$.form.dispositionOption.$pending.$response
          "
          class="p-error"
        >
          {{
            v$.form.dispositionOption.required.$message.replace(
              "Value",
              $t("models.whatsapp.disposition_form.disposition_option")
            )
          }}
        </small>
      </div>
    </div>

    <div class="grid formgrid mt-2">
      <div
        v-for="(field, index) in formByType"
        :key="index"
        class="field col-6 mt-4"
      >
        <div v-if="field.is_required">
          <label
            :class="{
              'p-error': isEmptyField(field.value) && submitted,
            }"
            >{{ field.name }}*</label
          >
          <div class="p-inputgroup mt-2">
            <span class="p-inputgroup-addon">
              <i class="pi" :class="getIconByFieldType(field.type)"></i>
            </span>
            <InputText
              v-model="field.value"
              :class="{
                'p-invalid': isEmptyField(field.value) && submitted,
              }"
              class="w-full"
              v-if="field.type == fieldTypes.OPT1"
            />
            <Calendar
              v-model="field.value"
              :class="{
                'p-invalid': isEmptyField(field.value) && submitted,
              }"
              class="w-full"
              v-else-if="field.type == fieldTypes.OPT2"
            />
            <Dropdown
              v-model="field.value"
              :class="{
                'p-invalid': isEmptyField(field.value) && submitted,
              }"
              class="w-full"
              v-else-if="field.type == fieldTypes.OPT3"
              optionLabel="name"
              optionValue="value"
              :options="field.selectOptions"
            />
            <Textarea
              v-model="field.value"
              :class="{
                'p-invalid': isEmptyField(field.value) && submitted,
              }"
              class="w-full"
              v-else
              rows="5"
              cols="30"
            />
          </div>
          <div v-if="isEmptyField(field.value) && submitted">
            <small class="p-error">{{
              $t(
                "forms.whatsapp.disposition_chat.validations.field_is_required",
                {
                  field: field.name,
                }
              )
            }}</small>
            <br />
          </div>
        </div>
        <div v-else>
          <label>{{ field.name }}</label>
          <div class="p-inputgroup mt-2">
            <span class="p-inputgroup-addon">
              <i class="pi" :class="getIconByFieldType(field.type)"></i>
            </span>
            <InputText
              v-model="field.value"
              class="w-full"
              v-if="field.type == fieldTypes.OPT1"
            />
            <Calendar
              v-model="field.value"
              class="w-full"
              v-else-if="field.type == fieldTypes.OPT2"
            />
            <Dropdown
              v-model="field.value"
              class="w-full"
              v-else-if="field.type == fieldTypes.OPT3"
              optionLabel="name"
              optionValue="value"
              :options="field.selectOptions"
            />
            <Textarea
              v-model="field.value"
              class="w-full"
              v-else
              rows="5"
              cols="30"
            />
          </div>
        </div>
      </div>
    </div>
    <div class="grid formgrid mt-1">
      <div class="field sm:col-12 md:col-12 lg:col-12 xl:col-12">
        <label id="comments">{{
          $t("models.whatsapp.disposition_form.observations")
        }}</label>
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-comments"></i>
          </span>
          <Textarea v-model="form.comments" class="w-full" rows="5" cols="30" />
        </div>
      </div>
    </div>
    <div class="flex justify-content-end flex-wrap mt-2">
      <div class="flex align-items-center">
        <Button
          class="p-button-danger p-button-outlined mr-2"
          :label="$t('globals.cancel')"
          @click="closeModal"
        />
        <Button
          :label="$t('globals.save')"
          icon="pi pi-save"
          @click="save(!v$.$invalid)"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { FilterMatchMode } from 'primevue/api';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { mapActions, mapState } from 'vuex';
import { FORM_TYPES, FIELD_TYPES } from '@/globals/agent/whatsapp/disposition';
import { HTTP_STATUS } from '@/globals';
import { notificationEvent, NOTIFICATION, WHATSAPP_LOCALSTORAGE_EVENTS } from '@/globals/agent/whatsapp';
export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            form: {
                dispositionOption: { required }
            }
        };
    },
    inject: ['$helpers'],
    data () {
        return {
            fieldTypes: FIELD_TYPES,
            form: {
                id: null,
                dispositionOption: null,
                comments: ''
            },
            formByType: {},
            submitted: false,
            invalidForm: false,
            filters: null,
            formResponseMetadata: null,
            dispositionOptions: [
                {
                    type: FORM_TYPES.OPT1,
                    label: this.$t(
                        'forms.whatsapp.disposition_chat.form_types.no_action'
                    ),
                    items: []
                },
                {
                    type: FORM_TYPES.OPT2,
                    label: this.$t(
                        'forms.whatsapp.disposition_chat.form_types.management'
                    ),
                    items: []
                },
                {
                    type: FORM_TYPES.OPT3,
                    label: this.$t('forms.whatsapp.disposition_chat.form_types.schedule'),
                    items: []
                }
            ],
            formFields: [],
            dropdownOptions: [{ name: '-------', value: null }]
        };
    },
    created () {
        this.initializeData();
    },
    computed: {
        ...mapState([
            'agtWhatsDispositionChatOptions',
            'agtWhatsCoversationInfo',
            'agtWhatsDispositionChatFormToCreate',
            'agtWhatsDispositionChatDetail'
        ])
    },
    methods: {
        ...mapActions([
            'agtWhatsDispositionChatUpdate',
            'agtWhatsDispositionChatCreate'
        ]),
        resetData () {
            this.form = {
                id: null,
                dispositionOption: null,
                comments: ''
            };
            this.submitted = false;
        },
        closeModal () {
            this.resetData();
            this.$emit('clearForm');
            const modalEvent = new CustomEvent('onWhatsappDispositionFormEvent', {
                detail: {
                    disposition_form: false
                }
            });
            window.parent.document.dispatchEvent(modalEvent);
        },
        initializeData () {
            this.initFormData();
            this.submitted = false;
        },
        initFormToUpdate () {
            const dispositionData =
        this.agtWhatsDispositionChatDetail?.disposition_data || null;
            this.formResponseMetadata = this.agtWhatsDispositionChatDetail
                ?.form_response?.metadata
                ? JSON.parse(
            this.agtWhatsDispositionChatDetail?.form_response?.metadata
                )
                : null;
            this.form = {
                id: null,
                dispositionOption: dispositionData?.id || null,
                comments: this.agtWhatsDispositionChatDetail?.comments || ''
            };
            this.getFormFieldsByOption();
        },
        initFormToCreate () {
            this.form = {
                id: null,
                dispositionOption: null,
                comments: ''
            };
        },
        initFormData () {
            if (this.agtWhatsDispositionChatFormToCreate) {
                this.initFormToCreate();
            } else {
                this.initFormToUpdate();
            }
        },
        getIconByFieldType (type) {
            if (type === FIELD_TYPES.OPT1) {
                return 'pi-bars';
            } else if (type === FIELD_TYPES.OPT2) {
                return 'pi-calendar';
            } else if (type === FIELD_TYPES.OPT3) {
                return 'pi-list';
            } else {
                return 'pi-comment';
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
        getDropdownOptions (data = null) {
            if (!data) {
                return null;
            }
            const options = JSON.parse(data);
            const dropdownOptions = [
                { name: '-------', value: null },
                ...options.map((item) => {
                    return {
                        name: item,
                        value: item
                    };
                })
            ];
            return dropdownOptions;
        },
        getFormFieldsByOption () {
            this.formFields = [];
            const option = this.agtWhatsDispositionChatOptions?.find(
                (item) => item.id === this.form.dispositionOption
            );
            if (option) {
                this.formFields = option?.form_fields || [];
            }
            this.initFormByTypeData();
        },
        initFormByTypeData () {
            this.formByType = {};
            if (this.formFields.length > 0) {
                for (let i = 0; i < this.formFields.length; i++) {
                    const field = this.formFields[i];
                    let value = null;
                    if (!this.agtWhatsDispositionChatFormToCreate) {
                        const response = this.formResponseMetadata
                            ? this.formResponseMetadata[field?.name] || null
                            : null;
                        if (field?.type === this.fieldTypes.OPT2) {
                            value = response ? new Date(response) : null;
                        } else {
                            value = response;
                        }
                    } else {
                        value = field?.type === this.fieldTypes.OPT2 ? new Date() : null;
                    }
                    this.formByType[`field_${i}`] = {
                        ...field,
                        selectOptions: this.getDropdownOptions(field?.values_select),
                        empty: false,
                        invalid: false,
                        value
                    };
                }
            }
        },
        validateFormByType () {
            this.invalidForm = false;
            const keysArray = Object.keys(this.formByType);
            for (let i = 0; i < keysArray.length; i++) {
                const key = keysArray[i];
                const field = this.formByType[key];
                this.formByType[`field_${i}`].empty = false;
                if (field.is_required && this.isEmptyField(field.value)) {
                    this.invalidForm = true;
                    this.formByType[`field_${i}`].empty = true;
                }
            }
        },
        getManageFormResponse () {
            const outputObj = {};
            const inputObj = this.formByType;
            Object.keys(inputObj).forEach((key) => {
                outputObj[inputObj[key].name] = inputObj[key].value;
            });
            return outputObj;
        },
        async save (isFormValid) {
            try {
                this.submitted = true;
                this.validateFormByType();
                if (!isFormValid || this.invalidForm) {
                    return null;
                }
                const formData = {
                    idContact: this.agtWhatsCoversationInfo?.client?.id || null,
                    idAgente: this.agtWhatsCoversationInfo?.agent || null,
                    idDispositionOption: this.form?.dispositionOption || null,
                    comments: this.form?.comments || null,
                    idConversation: this.agtWhatsCoversationInfo.id
                };
                // Si es de GESTION hay que mandar respuestaFormularioGestion
                const dispositionType = this.agtWhatsDispositionChatOptions?.find(
                    (c) => c?.id === this.form?.dispositionOption
                )?.type;
                if (dispositionType === FORM_TYPES.OPT2) {
                    formData.respuestaFormularioGestion = this.getManageFormResponse();
                }
                let response = null;
                this.$swal.fire({
                    title: this.$t('globals.processing_request'),
                    timerProgressBar: true,
                    allowOutsideClick: false,
                    didOpen: () => {
                        this.$swal.showLoading();
                    }
                });
                if (this.agtWhatsDispositionChatFormToCreate) {
                    response = await this.agtWhatsDispositionChatCreate({
                        data: formData
                    });
                } else {
                    response = await this.agtWhatsDispositionChatUpdate({
                        id: this.agtWhatsDispositionChatDetail.id,
                        data: formData
                    });
                }
                this.$swal.close();
                const { status, message } = response;
                this.closeModal();
                if (status === HTTP_STATUS.SUCCESS) {
                    const event = new Event(WHATSAPP_LOCALSTORAGE_EVENTS.CONVERSATION.DETAIL_INIT_DATA);
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
                console.error('ERROR Al calificar conversacion');
                console.error(error);
                await notificationEvent(
                    NOTIFICATION.TITLES.ERROR,
                    'Error Al calificar conversacion',
                    NOTIFICATION.ICONS.ERROR
                );
            }
        }
    },
    watch: {
        agtWhatsDispositionChatDetail: {
            handler () {
                this.initFormData();
            },
            deep: true,
            immediate: true
        },
        agtWhatsDispositionChatOptions: {
            handler () {
                if (this.agtWhatsDispositionChatOptions.length > 0) {
                    const noAction =
            this.agtWhatsDispositionChatOptions.filter(
                (c) => c.type === FORM_TYPES.OPT1
            ) || [];
                    const management =
            this.agtWhatsDispositionChatOptions.filter(
                (c) => c.type === FORM_TYPES.OPT2
            ) || [];
                    const schedule =
            this.agtWhatsDispositionChatOptions.filter(
                (c) => c.type === FORM_TYPES.OPT3
            ) || [];
                    if (noAction.length > 0) {
                        this.dispositionOptions.find(
                            (c) => c.type === FORM_TYPES.OPT1
                        ).items = noAction;
                    } else {
                        this.dispositionOptions = this.dispositionOptions.filter(
                            (c) => c.type !== FORM_TYPES.OPT1
                        );
                    }

                    if (management.length > 0) {
                        this.dispositionOptions.find(
                            (c) => c.type === FORM_TYPES.OPT2
                        ).items = management;
                    } else {
                        this.dispositionOptions = this.dispositionOptions.filter(
                            (c) => c.type !== FORM_TYPES.OPT2
                        );
                    }

                    if (schedule.length > 0) {
                        this.dispositionOptions.find(
                            (c) => c.type === FORM_TYPES.OPT3
                        ).items = schedule;
                    } else {
                        this.dispositionOptions = this.dispositionOptions.filter(
                            (c) => c.type !== FORM_TYPES.OPT3
                        );
                    }
                }
            },
            deep: true,
            immediate: true
        },
        agtWhatsCoversationInfo: {
            handler () {},
            deep: true,
            immediate: true
        },
        agtWhatsDispositionChatFormToCreate: {
            handler () {
                if (this.agtWhatsDispositionChatFormToCreate) {
                    this.initFormToCreate();
                } else {
                    this.initFormToUpdate();
                }
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
