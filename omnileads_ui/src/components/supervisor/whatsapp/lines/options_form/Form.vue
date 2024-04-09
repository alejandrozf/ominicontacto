<template>
  <div class="card">
    <div class="grid formgrid">
      <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
        <label
          :class="{
            'p-error': v$.form.value.$invalid && submitted,
          }"
          >{{ $t("models.whatsapp.line.options.value") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <InputText
            :class="{
              'p-invalid': v$.form.value.$invalid && submitted,
            }"
            v-model="v$.form.value.$model"
            @input="updateOption"
          />
        </div>
        <small
          v-if="
            (v$.form.value.$invalid && submitted) ||
            v$.form.value.$pending.$response
          "
          class="p-error"
          >{{
            v$.form.value.required.$message.replace(
              "Value",
              $t("models.whatsapp.line.options.value")
            )
          }}</small
        >
      </div>
      <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
        <label
          :class="{
            'p-error': v$.form.description.$invalid && submitted,
          }"
          >{{ $t("models.whatsapp.line.options.description") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <InputText
            :class="{
              'p-invalid': v$.form.description.$invalid && submitted,
            }"
            v-model="v$.form.description.$model"
            @input="updateOption"
          />
        </div>
        <small
          v-if="
            (v$.form.description.$invalid && submitted) ||
            v$.form.description.$pending.$response
          "
          class="p-error"
          >{{
            v$.form.description.required.$message.replace(
              "Value",
              $t("models.whatsapp.line.options.description")
            )
          }}</small
        >
      </div>
    </div>
    <div class="grid formgrid mt-4">
      <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
        <label
          :class="{
            'p-error': v$.form.destinationType.$invalid && submitted,
          }"
          >{{
            $t("models.whatsapp.line.options.destination_type")
          }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-sitemap"></i>
          </span>
          <Dropdown
            v-model="v$.form.destinationType.$model"
            class="w-full"
            :class="{
              'p-invalid': v$.form.destinationType.$invalid && submitted,
            }"
            :options="destinationTypes"
            placeholder="-----"
            optionLabel="name"
            optionValue="value"
            :emptyFilterMessage="$t('globals.without_data')"
            :filter="true"
            :disabled="true"
            v-bind:filterPlaceholder="
              $t('globals.find_by', { field: $tc('globals.name') }, 1)
            "
          />
        </div>
        <small
          v-if="
            (v$.form.destinationType.$invalid && submitted) ||
            v$.form.destinationType.$pending.$response
          "
          class="p-error"
        >
          {{
            v$.form.destinationType.required.$message.replace(
              "Value",
              $t("models.whatsapp.line.options.destination_type")
            )
          }}
        </small>
      </div>
      <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
        <label
          :class="{
            'p-error': v$.form.destination.$invalid && submitted,
          }"
          >{{ $t("models.whatsapp.line.options.destination") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-sign-in"></i>
          </span>
          <Dropdown
            v-model="v$.form.destination.$model"
            class="w-full"
            :class="{
              'p-invalid': v$.form.destination.$invalid && submitted,
            }"
            @change="findDuplicated()"
            :options="campaings"
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
            (v$.form.destination.$invalid && submitted) ||
            v$.form.destination.$pending.$response
          "
          class="p-error"
          >{{
            v$.form.destination.required.$message.replace(
              "Value",
              $t("models.whatsapp.line.options.destination")
            )
          }}</small
        >
      </div>
    </div>
    <div class="flex justify-content-end flex-wrap mt-4">
      <div class="flex align-items-center">
        <Button
          class="p-button-danger p-button-outlined mr-2"
          :label="$t('globals.cancel')"
          @click="closeModal()"
        />
        <Button
          :disabled="alreadyExists"
          :label="$t('globals.save')"
          icon="pi pi-save"
          @click="save(!v$.$invalid)"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { mapActions, mapState } from 'vuex';
import { DESTINATION_OPTION_TYPES } from '@/globals/supervisor/whatsapp/line';
import { CAMPAIGN_TYPES } from '@/globals/supervisor/campaign';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            form: {
                value: { required },
                description: { required },
                destinationType: { required },
                destination: { required }
            }
        };
    },
    inject: ['$helpers'],
    props: {
        formToCreate: {
            type: Boolean,
            default: false
        }
    },
    data () {
        return {
            form: {
                id: null,
                index: 0,
                value: '',
                description: '',
                destinationType: null,
                destination: null
            },
            alreadyExists: false,
            submitted: false,
            filters: null,
            destinationTypes: [
                { name: '-------', value: null },
                {
                    name: this.$t('forms.whatsapp.line.destination_types.campaign'),
                    value: DESTINATION_OPTION_TYPES.CAMPAIGN
                }
            ],
            campaings: [
                {
                    type: CAMPAIGN_TYPES.INBOUND,
                    label: this.$t('models.campaign.types.inbound'),
                    items: []
                },
                {
                    type: CAMPAIGN_TYPES.MANUAL,
                    label: this.$t('models.campaign.types.manual'),
                    items: []
                },
                {
                    type: CAMPAIGN_TYPES.PREVIEW,
                    label: this.$t('models.campaign.types.preview'),
                    items: []
                },
                {
                    type: CAMPAIGN_TYPES.DIALER,
                    label: this.$t('models.campaign.types.dialer'),
                    items: []
                }
            ]
        };
    },
    created () {
        this.initializeData();
    },
    computed: {
        ...mapState([
            'supWhatsappLineOptionForm',
            'supWhatsappLineCampaigns',
            'supWhatsappLineOptions'
        ])
    },
    methods: {
        ...mapActions([
            'createWhatsappLineOption',
            'updateWhatsappLineOption',
            'initWhatsappLineOptionForm'
        ]),
        updateOption (event) {
            const newValue = event.value;
            this.form.option = newValue;
            this.findDuplicated();
        },
        closeModal () {
            this.$emit('closeModalEvent');
        },
        initializeData () {
            this.initFormData();
            this.submitted = false;
        },
        initFormData () {
            this.form.id = this.supWhatsappLineOptionForm.id;
            this.form.index = this.supWhatsappLineOptionForm.index;
            this.form.value = this.supWhatsappLineOptionForm.value;
            this.form.description = this.supWhatsappLineOptionForm.description;
            this.form.destinationType = this.supWhatsappLineOptionForm.destinationType;
            this.form.destination = this.supWhatsappLineOptionForm.destination;
            this.findDuplicated();
        },
        findDuplicated () {
            const duplicated = this.supWhatsappLineOptions.find(
                (option) =>
                    option.value === this.form.value &&
          option.description === this.form.description &&
          option.destination === this.form.destination
            );
            if (duplicated) {
                this.alreadyExists = true;
            } else {
                this.alreadyExists = false;
            }
        },
        save (isFormValid) {
            this.submitted = true;
            if (!isFormValid) {
                return null;
            }
            if (this.formToCreate) {
                this.createWhatsappLineOption({
                    data: this.form
                });
            } else {
                this.updateWhatsappLineOption({
                    id: this.form.index,
                    data: this.form
                });
            }
            this.$swal(
                this.$helpers.getToasConfig(
                    this.$t('globals.success_notification'),
                    this.formToCreate
                        ? this.$t('forms.whatsapp.line.options.success_create')
                        : this.$t('forms.whatsapp.line.options.success_update'),
                    this.$t('globals.icon_success')
                )
            );
            this.closeModal();
        }
    },
    watch: {
        supWhatsappLineOptionForm: {
            handler () {
                this.initFormData();
            },
            deep: true,
            immediate: true
        },
        supWhatsappLineCampaigns: {
            handler () {
                if (this.supWhatsappLineCampaigns.length > 0) {
                    const manualCampaigns =
            this.supWhatsappLineCampaigns.filter(
                (c) => c.type === CAMPAIGN_TYPES.MANUAL
            ) || [];
                    const inboundCampaigns =
            this.supWhatsappLineCampaigns.filter(
                (c) => c.type === CAMPAIGN_TYPES.INBOUND
            ) || [];
                    const previewCampaigns =
            this.supWhatsappLineCampaigns.filter(
                (c) => c.type === CAMPAIGN_TYPES.PREVIEW
            ) || [];
                    const dialerCampaigns =
            this.supWhatsappLineCampaigns.filter(
                (c) => c.type === CAMPAIGN_TYPES.DIALER
            ) || [];
                    if (inboundCampaigns.length > 0) {
                        this.campaings.find(
                            (c) => c.type === CAMPAIGN_TYPES.INBOUND
                        ).items = inboundCampaigns;
                    } else {
                        this.campaings = this.campaings.filter(
                            (c) => c.type !== CAMPAIGN_TYPES.INBOUND
                        );
                    }
                    if (manualCampaigns.length > 0) {
                        this.campaings.find((c) => c.type === CAMPAIGN_TYPES.MANUAL).items =
              manualCampaigns;
                    } else {
                        this.campaings = this.campaings.filter(
                            (c) => c.type !== CAMPAIGN_TYPES.MANUAL
                        );
                    }
                    if (previewCampaigns.length > 0) {
                        this.campaings.find(
                            (c) => c.type === CAMPAIGN_TYPES.PREVIEW
                        ).items = previewCampaigns;
                    } else {
                        this.campaings = this.campaings.filter(
                            (c) => c.type !== CAMPAIGN_TYPES.PREVIEW
                        );
                    }
                    if (dialerCampaigns.length > 0) {
                        this.campaings.find((c) => c.type === CAMPAIGN_TYPES.DIALER).items =
              dialerCampaigns;
                    } else {
                        this.campaings = this.campaings.filter(
                            (c) => c.type !== CAMPAIGN_TYPES.DIALER
                        );
                    }
                }
            },
            deep: true,
            immediate: true
        },
        formToCreate: {
            handler () {},
            deep: true,
            immediate: true
        },
        supWhatsappLineOptions: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
