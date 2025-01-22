<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '60vw' }"
    :closable="false"
    :modal="false"
  >
    <template #header>
      <h2>{{ $t("forms.form.new_field") }}</h2>
    </template>
    <div class="card">
      <div class="fluid grid formgrid">
        <div class="field col-5">
          <label
            id="form_field_type"
            :class="{
              'p-error': v$.newFormField.tipo.$invalid && submitted,
            }"
            >{{ $t("models.form_field.type") }}*</label
          >
          <Dropdown
            v-model="v$.newFormField.tipo.$model"
            :options="fieldTypes"
            optionLabel="option"
            optionValue="value"
            @change="changeTypeEvent"
            placeholder="--------"
            :emptyFilterMessage="$t('globals.without_data')"
            :filter="true"
            class="mt-2 w-full"
            :class="{
              'p-invalid': v$.newFormField.tipo.$invalid && submitted,
            }"
            v-bind:filterPlaceholder="
              $t('globals.find_by', { field: $tc('globals.name') }, 1)
            "
          />
          <small
            v-if="
              (v$.newFormField.tipo.$invalid && submitted) ||
              v$.newFormField.tipo.$pending.$response
            "
            class="p-error"
            >{{
              v$.newFormField.tipo.required.$message.replace(
                "Value",
                $t("models.form_field.type")
              )
            }}</small
          >
          <small v-if="checkEmptyList" class="p-error mt-2">{{
            $t("forms.form.validations.not_empty_list")
          }}</small>
        </div>
        <div class="field col-5">
          <label
            id="form_field_name"
            :class="{
              'p-error': v$.newFormField.nombre_campo.$invalid && submitted,
            }"
            >{{ $t("models.form_field.name") }}*</label
          >
          <div class="p-inputgroup mt-2">
            <span class="p-inputgroup-addon">
              <i class="pi pi-list"></i>
            </span>
            <InputText
              id="form_field_name"
              class="w-full"
              @input="fieldNameEvent"
              :class="{
                'p-invalid': v$.newFormField.nombre_campo.$invalid && submitted,
              }"
              :placeholder="$t('forms.form.enter_name')"
              v-model="v$.newFormField.nombre_campo.$model"
            />
          </div>
          <small
            v-if="
              (v$.newFormField.nombre_campo.$invalid && submitted) ||
              v$.newFormField.nombre_campo.$pending.$response
            "
            class="p-error"
            >{{
              v$.newFormField.nombre_campo.required.$message.replace(
                "Value",
                $t("models.form_field.name")
              )
            }}</small
          >
          <small v-if="duplicateFieldName" class="p-error mt-2">{{
            $t("forms.form.validations.field_already_in_form")
          }}</small>
        </div>
        <div class="field col-2">
          <label id="form_field_required">{{
            $t("models.form_field.required")
          }}</label>
          <br />
          <Checkbox
            id="form_field_required"
            class="mt-2"
            v-model="newFormField.is_required"
            :binary="true"
          />
        </div>
        <div class="field mt-3" v-if="newFormField.tipo == 5">
          <div class="flex flex-col gap-4">
            <div v-for="tipo of fieldTypesNumero" :key="tipo.value" class="flex items-center">
              <RadioButton v-model="newFormField.tipo_numero" :inputId="tipo.value" name="dynamic" :value="tipo.value" />
              <label :for="tipo.value" class="ml-2">{{ tipo.option }}</label>
            </div>
            <div>
              <InputNumber v-if="newFormField.tipo_numero == 2"
                id="form_field_digitos_significativos"
                :placeholder="$t('forms.form.sig_digits')"
                v-model="newFormField.cifras_significativas"
                :useGrouping="false"
                :min="1"
                :max="3"
              />
            </div>
          </div>
        </div>

        <div class="field mt-3" v-if="newFormField.tipo == 6">
          <div class="flex flex-col gap-4">
            <label
              id="form_field_sitio_externo"
              >{{ $t("models.form_field.sitio_externo") }}*</label
            >
            <Dropdown
              v-model="newFormField.sitio_externo"
              :options="externalSitesDynamicList"
              optionLabel="nombre"
              optionValue="id"
              placeholder="--------"
              class="mt-2 w-full"
              v-bind:filterPlaceholder="
                $t('globals.find_by', { field: $tc('globals.name') }, 1)
              "
            />
          </div>
        </div>
      </div>
      <OptionListForm :isListType="isListType" />
    </div>
    <template #footer>
      <div class="flex justify-content-end flex-wrap">
        <Button
          class="p-button-danger p-button-outlined mr-2"
          :label="$t('globals.cancel')"
          @click="closeModal"
        />
        <Button :label="$t('globals.save')" @click="save(!v$.$invalid)" />
      </div>
    </template>
  </Dialog>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { useVuelidate } from '@vuelidate/core';
import { required } from '@vuelidate/validators';
import OptionListForm from './OptionListForm';

export default {
    setup: () => ({ v$: useVuelidate({ $scope: false }) }),
    validations () {
        return {
            newFormField: {
                nombre_campo: { required },
                tipo: { required }
            }
        };
    },
    props: {
        showModal: {
            type: Boolean,
            default: false
        }
    },
    components: {
        OptionListForm
    },
    data () {
        return {
            submitted: false,
            isListType: false,
            duplicateFieldName: false,
            fieldTypes: [
                { option: this.$t('forms.form.field.type.text'), value: 1 },
                { option: this.$t('forms.form.field.type.date'), value: 2 },
                { option: this.$t('forms.form.field.type.list'), value: 3 },
                { option: this.$t('forms.form.field.type.text_box'), value: 4 },
                { option: this.$t('forms.form.field.type.numero'), value: 5 },
                { option: this.$t('forms.form.field.type.dynamic_list'), value: 6 }
            ],
            fieldTypesNumero: [
                { option: this.$t('forms.form.field.numero_type.entero_type'), value: 1 },
                { option: this.$t('forms.form.field.numero_type.decimal_type'), value: 2 }
            ]
        };
    },
    created () {
        this.initFormData();
    },
    computed: {
        ...mapState(['newFormField', 'optionListValues', 'formDetail', 'newForm', 'externalSitesDynamicList']),
        checkEmptyList () {
            return this.optionListValues.length === 0 && this.newFormField.tipo === 3;
        }
    },
    methods: {
        ...mapActions(['initNewFormField', 'initOptionListValues', 'addFormField', 'initExternalSitesDynamicList']),
        initFormData () {
            this.submitted = false;
            this.initNewFormField();
            this.duplicateFieldName = false;
            this.isListType = this.newFormField.tipo === 3;
        },
        save (isFormValid) {
            this.submitted = true;
            if (!isFormValid || this.duplicateFieldName) {
                return null;
            }
            if (this.newFormField.tipo === 3) {
                if (this.optionListValues.length === 0) {
                    return null;
                }
                this.newFormField.values_select = JSON.stringify(
                    this.optionListValues.map((data) => data.nombre)
                );
            } else {
                this.newFormField.values_select = null;
            }
            this.newFormField.orden = this.newForm.campos.length + 1;
            this.$emit('addFieldEvent', this.newFormField);
            this.initFormData();
        },
        closeModal () {
            this.$emit('handleModalEvent', false);
            this.initFormData();
        },
        changeTypeEvent () {
            this.isListType = this.newFormField.tipo === 3;
            this.initOptionListValues();
            this.initExternalSitesDynamicList();
        },
        fieldNameEvent () {
            this.duplicateFieldName = this.newForm.campos.find(
                (data) => data.nombre_campo === this.newFormField.nombre_campo
            );
        }
    }
};
</script>
