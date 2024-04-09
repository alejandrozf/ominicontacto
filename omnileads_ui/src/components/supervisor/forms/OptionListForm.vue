<template>
  <div class="mt-5 mb-5" v-if="isListType">
    <hr />
    <h3>{{ $t("forms.form.options_list") }}</h3>
    <div class="fluid grid formgrid">
      <div class="field col-6">
        <label
          id="optionlist_name"
          :class="{
            'p-error': v$.optionList.nombre.$invalid && submitted,
          }"
          >{{ $t("globals.option") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <InputText
            id="optionlist_name"
            class="w-full"
            :class="{
              'p-invalid': v$.optionList.nombre.$invalid && submitted,
            }"
            @input="optionListNameEvent"
            :placeholder="$t('forms.external_system.enter_name')"
            v-model="v$.optionList.nombre.$model"
          />
        </div>
        <small
          v-if="
            (v$.optionList.nombre.$invalid && submitted) ||
            v$.optionList.nombre.$pending.$response
          "
          class="p-error"
          >{{
            v$.optionList.nombre.required.$message.replace(
              "Value",
              $t("globals.option")
            )
          }}</small
        >
        <small v-if="duplicateOptionName" class="p-error">{{
          $t("forms.form.validations.option_already_in_list")
        }}</small>
        <div class="flex justify-content-start flex-wrap mt-4">
          <Button
            class="p-button-info"
            :label="$t('globals.add')"
            @click="saveOptionList(!v$.$invalid)"
          />
        </div>
      </div>
      <div class="field col-6">
        <DataTable :value="this.optionListValues" responsiveLayout="scroll">
          <Column header="Opcion">
            <template #body="slotProps">
              {{ slotProps.data.nombre }}
            </template>
          </Column>
          <Column
            :header="$tc('globals.option', 2)"
            style="max-width: 25rem"
            :exportable="false"
          >
            <template #body="slotProps">
              <Button
                icon="pi pi-trash"
                class="p-button-danger ml-2"
                @click="removeValueOption(slotProps.data.id)"
                v-tooltip.top="$t('globals.delete')"
              />
            </template>
          </Column>
        </DataTable>
      </div>
    </div>
    <hr />
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { useVuelidate } from '@vuelidate/core';
import { required } from '@vuelidate/validators';

export default {
    setup: () => ({ v$: useVuelidate({ $scope: false }) }),
    validations () {
        return {
            optionList: {
                nombre: { required }
            }
        };
    },
    props: {
        isListType: {
            type: Boolean,
            default: false
        }
    },
    data () {
        return {
            submitted: false,
            duplicateOptionName: false,
            optionList: {
                nombre: '',
                id: null
            }
        };
    },
    computed: {
        ...mapState(['optionListValues'])
    },
    methods: {
        ...mapActions([
            'addValueOption',
            'removeValueOption',
            'initOptionListValues'
        ]),
        initFormOptionData () {
            this.submitted = false;
            this.optionList = {
                nombre: '',
                id: null
            };
        },
        optionListNameEvent () {
            this.duplicateOptionName = this.optionListValues.find(
                (data) => data.nombre === this.optionList.nombre
            );
        },
        saveOptionList (isFormValid) {
            this.submitted = true;
            if (!isFormValid || this.duplicateOptionName) {
                return null;
            }
            this.addValueOption(this.optionList);
            this.initFormOptionData();
        }
    },
    watch: {
        isListType: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
