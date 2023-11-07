<template>
  <div class="card">
    <div class="grid formgrid mt-1">
      <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
        <label
          id="form_type"
          :class="{
            'p-error': v$.form.type.$invalid && submitted,
          }"
          >{{ $t("models.whatsapp.disposition_form.type") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <Dropdown
            id="form_type"
            v-model="v$.form.type.$model"
            class="w-full"
            :class="{
              'p-invalid': v$.form.type.$invalid && submitted,
            }"
            :options="types"
            @change="getOptionsByType"
            placeholder="-----"
            optionLabel="name"
            optionValue="value"
            :emptyFilterMessage="$t('globals.without_data')"
            :filter="true"
            v-bind:filterPlaceholder="
              $t('globals.find_by', { field: $tc('globals.name') }, 1)
            "
          />
        </div>
        <small
          v-if="
            (v$.form.type.$invalid && submitted) ||
            v$.form.type.$pending.$response
          "
          class="p-error"
        >
          {{
            v$.form.type.required.$message.replace(
              "Value",
              $t("models.whatsapp.disposition_form.type")
            )
          }}
        </small>
      </div>
      <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
        <label
          id="form_type"
          :class="{
            'p-error': v$.form.optionByType.$invalid && submitted,
          }"
          >{{ $t("models.whatsapp.disposition_form.option") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <Dropdown
            id="form_type"
            v-model="v$.form.optionByType.$model"
            class="w-full"
            :class="{
              'p-invalid': v$.form.optionByType.$invalid && submitted,
            }"
            @change="getFormFieldsByOption"
            :options="optionsByType"
            placeholder="-----"
            optionLabel="name"
            optionValue="value"
            :emptyFilterMessage="$t('globals.without_data')"
            :filter="true"
            v-bind:filterPlaceholder="
              $t('globals.find_by', { field: $tc('globals.name') }, 1)
            "
          />
        </div>
        <small
          v-if="
            (v$.form.optionByType.$invalid && submitted) ||
            v$.form.optionByType.$pending.$response
          "
          class="p-error"
        >
          {{
            v$.form.optionByType.required.$message.replace(
              "Value",
              $t("models.whatsapp.disposition_form.option")
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
              $t("forms.whatsapp.disposition_chat.validations.field_is_required", {
                field: field.name,
              })
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
import { notificationEvent, NOTIFICATION } from '@/globals/agent/whatsapp';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            form: {
                type: { required },
                optionByType: { required }
            }
        };
    },
    inject: ['$helpers'],
    data () {
        return {
            fieldTypes: FIELD_TYPES,
            form: {
                id: null,
                type: null,
                optionByType: null,
                comments: ''
            },
            formByType: {},
            submitted: false,
            invalidForm: false,
            filters: null,
            formResponseMetadata: null,
            types: [
                { name: '-------', value: null },
                {
                    name: this.$t('forms.whatsapp.disposition_chat.form_types.no_action'),
                    value: FORM_TYPES.OPT1
                },
                {
                    name: this.$t(
                        'forms.whatsapp.disposition_chat.form_types.management'
                    ),
                    value: FORM_TYPES.OPT2
                },
                {
                    name: this.$t('forms.whatsapp.disposition_chat.form_types.schedule'),
                    value: FORM_TYPES.OPT3
                }
            ],
            optionsByType: [{ name: '-------', value: null }],
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
                type: null,
                optionByType: null,
                comments: ''
            };
            this.submitted = false;
        },
        closeModal () {
            this.resetData();
            this.$emit('clearForm');
            const event = new CustomEvent('onWhatsappDispositionFormEvent', {
                detail: {
                    disposition_form: false
                }
            });
            window.parent.document.dispatchEvent(event);
        },
        initializeData () {
            this.initFormData();
            this.submitted = false;
        },
        initFormToUpdate () {
            const dispositionData = this.agtWhatsDispositionChatDetail.disposition_data || null;
            this.formResponseMetadata = JSON.parse(this.agtWhatsDispositionChatDetail.form_response.metadata) || null;
            this.form = {
                id: null,
                type: dispositionData ? dispositionData.type : null,
                optionByType: dispositionData ? dispositionData.id : null,
                comments: this.agtWhatsDispositionChatDetail.comments || ''
            };
            this.getOptionsByType();
            this.getFormFieldsByOption();
        },
        initFormToCreate () {
            this.form = {
                id: null,
                type: null,
                optionByType: null,
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
        getOptionsByType () {
            this.formByType = {};
            this.formFields = [];
            this.optionsByType = [{ name: '-------', value: null }];
            const options = this.agtWhatsDispositionChatOptions?.filter(
                (item) => item.type === this.form.type
            );
            if (options) {
                options.forEach((item) => {
                    this.optionsByType.push({
                        name: item.name || '',
                        value: item.id || null
                    });
                });
            }
        },
        getFormFieldsByOption () {
            this.formFields = [];
            const option = this.agtWhatsDispositionChatOptions?.find(
                (item) => item.id === this.form.optionByType
            );
            if (option) {
                this.formFields = option.form_fields || [];
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
                        if (field.type === this.fieldTypes.OPT2) {
                            value = new Date(this.formResponseMetadata[field.name] || null);
                        } else {
                            value = this.formResponseMetadata[field.name] || null;
                        }
                    } else {
                        value = field.type === this.fieldTypes.OPT2 ? new Date() : null;
                    }
                    this.formByType[`field_${i}`] = {
                        ...field,
                        selectOptions: this.getDropdownOptions(field.values_select),
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
                    idContact: this.agtWhatsCoversationInfo.client.id || null,
                    idAgente: this.agtWhatsCoversationInfo.agent || null,
                    idDispositionOption: this.form.optionByType || null,
                    comments: this.form.comments,
                    respuestaFormularioGestion: null
                };
                // Si es de GESTION hay que mandar respuestaFormularioGestion
                if (this.form.type === FORM_TYPES.OPT2) {
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
            handler () {},
            deep: true,
            immediate: true
        },
        agtWhatsDispositionChatOptions: {
            handler () {},
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
