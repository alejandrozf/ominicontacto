<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '40vw' }"
    :closable="false"
    :modal="false"
  >
    <template #header>
      <h2>
        {{
          formToCreate
            ? $t("views.destination_option.new_title")
            : $t("views.destination_option.edit_title")
        }}
      </h2>
    </template>
    <div class="card">
      <div class="grid formgrid">
        <div class="field col-12">
          <label
            id="dtmf"
            :class="{
              'p-error': (v$.destinationOptionForm.dtmf.$invalid && submitted) || repeatedDTMF || invalidDTMF,
            }"
            >{{ $t("models.destination_option.dtmf") }}*</label
          >
          <div class="p-inputgroup mt-2">
            <InputText
              v-model="v$.destinationOptionForm.dtmf.$model"
              @input="inputDTMFEvent"
              :class="{
                'p-invalid':
                  (v$.destinationOptionForm.dtmf.$invalid && submitted) || repeatedDTMF || invalidDTMF,
              }"
            />
          </div>
          <small
            v-if="
              (v$.destinationOptionForm.dtmf.$invalid && submitted) ||
              v$.destinationOptionForm.dtmf.$pending.$response
            "
            class="p-error"
            >{{
              v$.destinationOptionForm.dtmf.required.$message.replace(
                "Value",
                $t("models.destination_option.dtmf")
              )
            }}</small
          >
          <small v-if="repeatedDTMF" class="p-error"
            >{{ $t('forms.destination_option.validations.repeated_dtmf') }}</small
          >
          <small
            v-if="invalidDTMF"
            class="p-error"
            >{{
              $t('forms.destination_option.validations.invalid_dtmf')
            }}</small
          >
        </div>
        <div class="field col-12">
          <label
            id="pause_type"
            :class="{
              'p-error':
                v$.destinationOptionForm.destination_type.$invalid && submitted,
            }"
            >{{ $t("models.destination_option.destination_type") }}*</label
          >
          <Dropdown
            v-model="destinationOptionForm.destination_type"
            class="w-full mt-2"
            :class="{
              'p-invalid':
                v$.destinationOptionForm.destination_type.$invalid && submitted,
            }"
            :options="destination_types"
            placeholder="-----"
            optionLabel="option"
            optionValue="value"
            @change="getDestinations"
            :emptyFilterMessage="$t('globals.without_data')"
          />
          <small
            v-if="
              (v$.destinationOptionForm.destination_type.$invalid &&
                submitted) ||
              v$.destinationOptionForm.destination_type.$pending.$response
            "
            class="p-error"
            >{{
              v$.destinationOptionForm.destination_type.required.$message.replace(
                "Value",
                $t("models.destination_option.destination_type")
              )
            }}</small
          >
        </div>
        <div class="field col-12">
          <label
            id="pause_type"
            :class="{
              'p-error':
                v$.destinationOptionForm.destination.$invalid && submitted,
            }"
            >{{ $t("models.destination_option.destination") }}*</label
          >
          <Dropdown
            v-model="destinationOptionForm.destination"
            class="w-full mt-2"
            :class="{
              'p-invalid':
                v$.destinationOptionForm.destination.$invalid && submitted,
            }"
            :options="destinations_filter"
            placeholder="-----"
            optionLabel="nombre"
            optionValue="id"
            :emptyFilterMessage="$t('globals.without_data')"
          />
          <small
            v-if="
              (v$.destinationOptionForm.destination.$invalid && submitted) ||
              v$.destinationOptionForm.destination.$pending.$response
            "
            class="p-error"
            >{{
              v$.destinationOptionForm.destination.required.$message.replace(
                "Value",
                $t("models.destination_option.destination")
              )
            }}</small
          >
        </div>
      </div>
    </div>
    <template #footer>
      <div class="flex justify-content-end flex-wrap">
        <Button
          class="p-button-danger p-button-outlined mr-2"
          :label="$t('globals.cancel')"
          @click="closeModal"
        />
        <Button :label="$t('globals.save')" class="p-button-info" @click="save(!v$.$invalid)" />
      </div>
    </template>
  </Dialog>
</template>

<script>
import { useVuelidate } from '@vuelidate/core';
import { required } from '@vuelidate/validators';
import { mapActions, mapState } from 'vuex';
import {
    CAMPAIGN,
    VALIDATION_DATE,
    IVR,
    HANGUP,
    ID_CLIENT,
    CUSTOM_DST
} from '@/globals/ivr';
import { isDTMFValid } from '@/helpers/ivr_helper';

export default {
    setup: () => ({ v$: useVuelidate({ $scope: false }) }),
    validations () {
        return {
            destinationOptionForm: {
                dtmf: { required },
                destination: { required },
                destination_type: { required }
            }
        };
    },
    inject: ['$helpers'],
    props: {
        destinationOptions: {
            type: Array,
            default: () => []
        },
        destinationOption: {
            type: Object,
            default: () => null
        },
        showModal: {
            type: Boolean,
            default: false
        },
        formToCreate: {
            type: Boolean,
            default: true
        }
    },
    data () {
        return {
            submitted: false,
            repeatedDTMF: false,
            invalidDTMF: false,
            destinationOptionForm: {
                id: null,
                destination: null,
                destination_type: null,
                dtmf: null
            },
            destination_types: [
                {
                    option: this.$t('forms.ivr.destination_types.campaign'),
                    value: CAMPAIGN
                },
                {
                    option: this.$t('forms.ivr.destination_types.validation_date'),
                    value: VALIDATION_DATE
                },
                {
                    option: this.$t('forms.ivr.destination_types.ivr'),
                    value: IVR
                },
                {
                    option: this.$t('forms.ivr.destination_types.hangup'),
                    value: HANGUP
                },
                {
                    option: this.$t('forms.ivr.destination_types.id_client'),
                    value: ID_CLIENT
                },
                {
                    option: this.$t('forms.ivr.destination_types.custom_dst'),
                    value: CUSTOM_DST
                }
            ],
            destinations_filter: []
        };
    },
    computed: {
        ...mapState(['ivrDestinations'])
    },
    created () {
        this.initializeData();
    },
    methods: {
        ...mapActions(['addDestinationOption', 'editDestinationOption']),
        initializeData () {
            this.submitted = false;
            this.repeatedDTMF = false;
            this.invalidDTMF = false;
            this.destinationOptionForm = {
                id: null,
                destination: null,
                destination_type: null,
                dtmf: null
            };
        },
        initForm () {
            if (this.destinationOption) {
                this.destinationOptionForm.id = this.destinationOption.id;
                this.destinationOptionForm.destination =
          this.destinationOption.destination;
                this.destinationOptionForm.destination_type =
          this.destinationOption.destination_type;
                this.destinationOptionForm.dtmf = this.destinationOption.dtmf;
                this.getDestinations();
            } else {
                this.destinationOptionForm = {
                    id: null,
                    destination: null,
                    destination_type: null,
                    dtmf: null
                };
            }
        },
        closeModal () {
            this.$emit('handleDestinationOptionModalEvent', {});
            this.initializeData();
        },
        inputDTMFEvent () {
            this.repeatedDTMF = this.destinationOptions.find(
                (d) => d.dtmf === this.destinationOptionForm.dtmf
            );
            this.invalidDTMF = !isDTMFValid(this.destinationOptionForm.dtmf);
        },
        getDestinations () {
            if (this.ivrDestinations.length > 0 || this.ivrDestinations !== null) {
                this.destinations_filter =
          this.destinationOptionForm.destination_type !== null
              ? this.ivrDestinations[
                  `${this.destinationOptionForm.destination_type}`
              ]
              : [];
            }
        },
        save (isFormValid) {
            this.submitted = true;
            if (!isFormValid || this.repeatedDTMF || this.invalidDTMF) {
                return null;
            }
            if (this.formToCreate) {
                this.addDestinationOption(this.destinationOptionForm);
            } else {
                this.editDestinationOption(this.destinationOptionForm);
            }
            this.closeModal();
        }
    },
    watch: {
        ivrDestinations: {
            handler () {
                this.getDestinations();
            },
            deep: true,
            immediate: true
        },
        destinationOptions: {
            handler () {},
            deep: true,
            immediate: true
        },
        destinationOption: {
            handler () {
                this.initForm();
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
