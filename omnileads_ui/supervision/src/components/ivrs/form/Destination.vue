<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '40vw' }"
    :closable="false"
    :modal="false"
  >
    <template #header>
      <h3>{{ modalTitle }}</h3>
    </template>
    <div class="card">
      <div class="grid formgrid mt-2">
        <div class="field col-12">
          <label
            id="destination_type"
            :class="{
              'p-error': v$.destination_type.$invalid && submitted,
            }"
            >{{ $t("models.destination_option.destination_type") }}*</label
          >
          <Dropdown
            v-model="destination_type"
            class="w-full mt-2"
            :class="{
              'p-invalid': v$.destination_type.$invalid && submitted,
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
              (v$.destination_type.$invalid && submitted) ||
              v$.destination_type.$pending.$response
            "
            class="p-error"
            >{{
              v$.destination_type.required.$message.replace(
                "Value",
                $t("models.destination_option.destination_type")
              )
            }}</small
          >
        </div>
        <div class="field col-12">
          <label
            id="destination"
            :class="{
              'p-error': v$.destination.$invalid && submitted,
            }"
            >{{ $t("models.destination_option.destination") }}*</label
          >
          <Dropdown
            v-model="destination"
            class="w-full mt-2"
            :class="{
              'p-invalid': v$.destination.$invalid && submitted,
            }"
            :options="destinations_filter"
            placeholder="-----"
            optionLabel="nombre"
            optionValue="id"
            :emptyFilterMessage="$t('globals.without_data')"
          />
          <small
            v-if="
              (v$.destination.$invalid && submitted) ||
              v$.destination.$pending.$response
            "
            class="p-error"
            >{{
              v$.destination.required.$message.replace(
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
        <Button
          :label="$t('globals.save')"
          class="p-button-info"
          @click="save"
        />
      </div>
    </template>
  </Dialog>
</template>

<script>
import { useVuelidate } from '@vuelidate/core';
import { required } from '@vuelidate/validators';
import { mapActions, mapState } from 'vuex';
import {
    TIME_OUT_DEST,
    CAMPAIGN,
    VALIDATION_DATE,
    IVR,
    HANGUP,
    ID_CLIENT,
    CUSTOM_DST
} from '@/globals/ivr';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            destination_type: { required },
            destination: { required }
        };
    },
    props: {
        modalTitle: {
            type: String,
            default: 'Destino para time out'
        },
        showModal: {
            type: Boolean,
            default: false
        },
        formToCreate: {
            type: Boolean,
            default: true
        },
        form: {
            type: Object,
            default: null
        },
        optionDestination: {
            type: Number,
            default: TIME_OUT_DEST
        }
    },
    inject: ['$helpers'],
    data () {
        return {
            submitted: false,
            destination_type: null,
            destination: null,
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
    methods: {
        ...mapActions(['updateDestination']),
        initializeData () {
            this.submitted = false;
            this.destination_type = null;
            this.destination = null;
            this.destinations_filter = [];
        },
        getDestinations () {
            if (this.ivrDestinations.length > 0 || this.ivrDestinations !== null) {
                this.destinations_filter =
          this.destination_type !== null
              ? this.ivrDestinations[`${this.destination_type}`]
              : [];
            }
        },
        closeModal () {
            this.$emit('handleDestinationModalEvent', {
                option: this.optionDestination
            });
            this.initializeData();
        },
        async save (isFormValid) {
            this.submitted = true;
            if (!isFormValid) {
                return null;
            }
            this.updateDestination({
                data: {
                    type: this.destination_type,
                    destination: this.destination
                },
                option: this.optionDestination
            });
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
        form: {
            handler () {
                if (this.form !== null) {
                    this.destination_type = this.form.destination_type;
                    this.destination = this.form.destination;
                    this.getDestinations();
                }
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
