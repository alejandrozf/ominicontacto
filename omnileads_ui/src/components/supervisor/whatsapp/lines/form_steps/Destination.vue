<template>
  <div class="card">
    <div class="grid mt-4">
      <div class="sm:col-12 md:col-12 lg:col-12 xl:col-12">
        <Fieldset :toggleable="true" :collapsed="false">
          <template #legend>
            {{ $t("views.whatsapp.line.step3.destination") }}
          </template>
          <div class="grid formgrid">
            <div class="field col-4">
              <label
                :class="{
                  'p-error':
                    v$.form.destination_type.$invalid && submitted,
                }"
                >{{ $t("models.whatsapp.line.tipo_de_destino") }}*</label
              >
              <div class="field-radiobutton">
                <RadioButton
                  :value="destinationType.CAMPAIGN"
                  v-model="form.destination_type"
                  @change="campaignOption()"
                />
                <label>{{
                  $t("views.whatsapp.line.tipos_de_destino.campana")
                }}</label>
              </div>
              <div class="field-radiobutton">
                <RadioButton
                  :value="destinationType.INTERACTIVE"
                  v-model="form.destination_type"
                  @change="interactiveOption()"
                />
                <label>{{
                  $t("views.whatsapp.line.tipos_de_destino.interactivo")
                }}</label>
              </div>
              <small
                v-if="
                  (v$.form.destination_type.$invalid &&
                    submitted) ||
                  v$.form.destination_type.$pending.$response
                "
                class="p-error"
                >{{
                  v$.form.destination_type.required.$message.replace(
                    "Value",
                    $t("models.whatsapp.line.destination_type")
                  )
                }}</small
              >
            </div>
            <div
              class="field col-8"
              v-if="
                form.destination_type === destinationType.CAMPAIGN
              "
            >
              <label
                :class="{
                  'p-error':
                    v$.form.destination.$invalid && submitted,
                }"
                >{{ $t("models.whatsapp.line.destino") }}*</label
              >
              <div class="p-inputgroup">
                <Checkbox v-model="only_whatsapp_habilitado" binary @change="onlyWhatsappHabilitadoChange"/>
                <label> {{ $t("forms.whatsapp.line.only_whatsapp_habilitado") }}</label>
              </div>
              <div class="p-inputgroup">
                <span class="p-inputgroup-addon">
                  <i class="pi pi-sign-in"></i>
                </span>
                <Dropdown
                  v-model="v$.form.destination.$model"
                  class="w-full"
                  :class="{
                    'p-invalid':
                      v$.form.destination.$invalid && submitted,
                  }"
                  :options="campaings"
                  :filter="true"
                  :showClear="true"
                  @change="ckeckingCampaign()"
                  placeholder="-----"
                  optionLabel="name"
                  optionValue="id"
                  optionGroupLabel="label"
                  optionGroupChildren="items"
                  :emptyFilterMessage="$t('globals.without_data')"
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
                    $t("models.whatsapp.line.destino")
                  )
                }}</small
              >
            </div>
            <div
              class="field col-12"
              v-if="
                form.destination_type === destinationType.INTERACTIVE
              "
            >
            <div class="flex justify-content-between flex-wrap mt-4 mb-4">
              <div class="flex align-items-center justify-content-center">
                <Button
                  :label="$t('views.whatsapp.line.flow.open_builder')"
                  icon="pi pi-sitemap"
                  class="p-button-outlined"
                  @click="openFlowBuilder"
                />
              </div>
              <div class="flex align-items-center justify-content-center">
              <Button
                :label="$t('globals.new')"
                icon="pi pi-plus"
                @click="addInteractiveMenuItem"
              />
              </div>
            </div>
            <div class="mt-4 pt-2">
              <FormMenuInteractivo :data="menu" :submitted="submitted" v-for="menu in supWhatsappLine.destination.data" :key="menu.id"></FormMenuInteractivo>
            </div>
            </div>
          </div>
        </Fieldset>
      </div>
    </div>
    <div class="flex justify-content-between flex-wrap mt-4">
      <div class="flex align-items-center justify-content-center">
      </div>
      <div class="flex align-items-center justify-content-center">
        <Button
          :label="$t('globals.save')"
          icon="pi pi-save"
          @click="save(!v$.$invalid)"
        />
      </div>
    </div>
    <FlowBuilderModal
      :showModal="showFlowBuilderModal"
      :nodes="supWhatsappLine.destination.data || []"
      :campaigns="campaings"
      :messageTemplates="messageTemplates"
      @handleModalEvent="handleFlowBuilderModal"
      @saveFlow="save(!v$.$invalid)"
    />
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import {
    DESTINATION_TYPES_BACK,
    DESTINATION_FORM_TYPES
} from '@/globals/supervisor/whatsapp/line';
import { CAMPAIGN_TYPES } from '@/globals/supervisor/campaign';
import { HTTP_STATUS } from '@/globals';
import ModalToHandleOption from '@/components/supervisor/whatsapp/lines/options_form/ModalToHandleOption';
import FormMenuInteractivo from '@/components/supervisor/whatsapp/lines/options_form/FormMenuInteractivo';
import FlowBuilderModal from '@/components/supervisor/whatsapp/lines/options_form/FlowBuilderModal';
import { PROVIDER_TYPES } from '@/globals/supervisor/whatsapp/provider';
import { TEMPLATE_TYPES } from '@/globals/supervisor/whatsapp/message_template';

export default {
    inject: ['$helpers'],
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            form: {
                destination: { required },
                destination_type: { required },
                horario: { required },
                mensaje_bienvenida: { required },
                mensaje_despedida: { required },
                mensaje_fueradehora: { required }
            }
        };
    },
    components: {
        FormMenuInteractivo,
        FlowBuilderModal,
        ModalToHandleOption
    },
    data () {
        console.log('asdfadasdsa');
        return {
            invalidInteractiveForm: false,
            interactiveForm: {
                text: '',
                wrongAnswer: '',
                successAnswer: '',
                timeout: 0,
                options: []
            },
            form: {
                destination: null,
                destination_type: null,
                horario: null,
                mensaje_bienvenida: null,
                mensaje_despedida: null,
                mensaje_fueradehora: null
            },
            showModal: false,
            formToCreate: false,
            destinationType: {
                CAMPAIGN: DESTINATION_FORM_TYPES.CAMPAIGN,
                INTERACTIVE: DESTINATION_FORM_TYPES.INTERACTIVE
            },
            only_whatsapp_habilitado: false,
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
            ],
            formErrors: [],
            submitted: false,
            isEmptyOptions: false,
            showFlowBuilderModal: false,
            messageTemplates: [
                {
                    type: TEMPLATE_TYPES.TEXT,
                    label: this.$t('forms.whatsapp.message_template.types.text'),
                    items: []
                },
                {
                    type: TEMPLATE_TYPES.IMAGE,
                    label: this.$t('forms.whatsapp.message_template.types.image'),
                    items: []
                },
                {
                    type: TEMPLATE_TYPES.VIDEO,
                    label: this.$t('forms.whatsapp.message_template.types.video'),
                    items: []
                },
                {
                    type: TEMPLATE_TYPES.FILE,
                    label: this.$t('forms.whatsapp.message_template.types.file'),
                    items: []
                },
                {
                    type: TEMPLATE_TYPES.STICKER,
                    label: this.$t('forms.whatsapp.message_template.types.sticker'),
                    items: []
                },
                {
                    type: TEMPLATE_TYPES.LOCATION,
                    label: this.$t('forms.whatsapp.message_template.types.location'),
                    items: []
                },
                {
                    type: TEMPLATE_TYPES.CONTACT,
                    label: this.$t('forms.whatsapp.message_template.types.contact'),
                    items: []
                }
            ]
        };
    },
    mounted () {
        this.initFormBase();
    },
    computed: {
        ...mapState([
            'supWhatsappLine',
            'isFormToCreate',
            'supWhatsappLineCampaigns',
            'supWhatsappLineOptions',
            'supWhatsappLineIteractiveForm',
            'supWhatsappMessageTemplates'
        ])
    },
    methods: {
        ...mapActions([
            'createWhatsappLine',
            'updateWhatsappLine',
            'initWhatsappLines',
            'initWhatsappLineOptionForm'
        ]),
        isEmptyField (field = null) {
            return field === null || field === undefined || field === '';
        },
        initFormBase () {
            this.form.horario = this.supWhatsappLine.horario;
            this.form.mensaje_bienvenida = this.supWhatsappLine.mensaje_bienvenida;
            this.form.mensaje_despedida = this.supWhatsappLine.mensaje_despedida;
            this.form.mensaje_fueradehora = this.supWhatsappLine.mensaje_fueradehora;
            this.form.destination_type = this.supWhatsappLine.destination.type;
            this.form.destination = this.supWhatsappLine.destination.data;
        },
        addInteractiveMenuItem () {
            this.ensureInteractiveDestinationData();
            this.supWhatsappLine.destination.data.push({
                id_tmp: +new Date() + Math.floor(Math.random() * 1000),
                is_main: false,
                menu_header: '',
                menu_body: '',
                menu_footer: '',
                menu_button: '',
                wrong_answer: '',
                success: '',
                timeout: 0,
                options: []
            });
        },
        openFlowBuilder () {
            this.ensureInteractiveDestinationData();
            this.showFlowBuilderModal = true;
        },
        handleFlowBuilderModal ({ showModal = false }) {
            this.showFlowBuilderModal = showModal;
        },
        ensureInteractiveDestinationData () {
            if (
                this.supWhatsappLine.destination.data === null ||
                typeof (this.supWhatsappLine.destination.data) === 'number'
            ) {
                this.supWhatsappLine.destination.data = [{
                    id_tmp: +new Date() + Math.floor(Math.random() * 1000),
                    is_main: true,
                    menu_header: '',
                    menu_body: '',
                    menu_footer: '',
                    menu_button: '',
                    wrong_answer: '',
                    success: '',
                    timeout: 0,
                    options: []
                }];
            }
            if (!Array.isArray(this.supWhatsappLine.destination.data)) {
                this.supWhatsappLine.destination.data = [{
                    id_tmp: +new Date() + Math.floor(Math.random() * 1000),
                    is_main: true,
                    menu_header: '',
                    menu_body: '',
                    menu_footer: '',
                    menu_button: '',
                    wrong_answer: '',
                    success: '',
                    timeout: 0,
                    options: []
                }];
            }
            this.supWhatsappLine.destination.data.forEach((menu) => {
                if (menu.menu_header === undefined) menu.menu_header = '';
                if (menu.menu_body === undefined) menu.menu_body = '';
                if (menu.menu_footer === undefined) menu.menu_footer = '';
                if (menu.menu_button === undefined) menu.menu_button = '';
                if (menu.wrong_answer === undefined) menu.wrong_answer = menu.wrongAnswer || '';
                if (menu.success === undefined) menu.success = menu.successAnswer || '';
                if (menu.timeout === undefined) menu.timeout = 0;
                if (!Array.isArray(menu.options)) menu.options = [];
            });
            if (!this.supWhatsappLine.destination.data.some((menu) => menu.is_main)) {
                this.supWhatsappLine.destination.data[0].is_main = true;
            }
        },
        handleModal ({ showModal = false, formToCreate = false, option = null }) {
            this.showModal = showModal;
            this.formToCreate = formToCreate;
            this.initWhatsappLineOptionForm(option);
        },
        validateFormData () {
            this.formErrors = [];
            if (!this.supWhatsappLine.nombre || this.supWhatsappLine.nombre === '') {
                this.formErrors.push(
                    this.$tc('forms.whatsapp.line.validations.field_is_required', {
                        field: this.$t('models.whatsapp.line.nombre')
                    })
                );
            }
            if (!this.supWhatsappLine.proveedor) {
                this.formErrors.push(
                    this.$tc('forms.whatsapp.line.validations.field_is_required', {
                        field: this.$t('models.whatsapp.line.proveedor')
                    })
                );
            }
            if (this.supWhatsappLine.numero === '') {
                this.formErrors.push(
                    this.$tc('forms.whatsapp.line.validations.field_is_required', {
                        field: this.$t('models.whatsapp.line.numero')
                    })
                );
            }
            if (this.supWhatsappLine.configuracion.app_name === '') {
                this.formErrors.push(
                    this.$tc('forms.whatsapp.line.validations.field_is_required', {
                        field: this.$t('models.whatsapp.line.configuracion.app_name')
                    })
                );
            }
            if (this.supWhatsappLine.configuracion.app_id === '') {
                this.formErrors.push(
                    this.$tc('forms.whatsapp.line.validations.field_is_required', {
                        field: this.$t('models.whatsapp.line.configuracion.app_id')
                    })
                );
            }
        },
        interactiveOption () {
            this.supWhatsappLine.destination.type = this.destinationType.INTERACTIVE;
            if (this.supWhatsappLine.destination.data === null || typeof (this.supWhatsappLine.destination.data) === 'number') {
                this.supWhatsappLine.destination.data = [this.supWhatsappLineIteractiveForm];
            }
        },
        campaignOption () {
            this.supWhatsappLine.destination.type = this.destinationType.CAMPAIGN;
        },
        getDestinationData () {
            if (
                this.form.destination_type ===
        this.destinationType.CAMPAIGN
            ) {
                return {
                    type: DESTINATION_TYPES_BACK.CAMPAIGN,
                    data: this.form.destination
                };
            } else if (
                this.form.destination_type ===
        this.destinationType.INTERACTIVE
            ) {
                return {
                    type: DESTINATION_TYPES_BACK.INTERACTIVE,
                    data: this.supWhatsappLine.destination.data,
                    id_tmp: this.supWhatsappLine.destination.id_tmp
                };
            } else if (
                this.form.destination_type ===
        this.destinationType.CLOSING_MESSAGE
            ) {
                return {
                    type: DESTINATION_TYPES_BACK.CLOSING_MESSAGE,
                    data: this.form.destination
                };
            }
        },
        async save (isFormValid) {
            this.submitted = true;
            this.validateFormData();
            if (this.formErrors.length > 0) {
                var errors = '';
                this.formErrors.forEach((e) => {
                    errors += `<li>${e}</li>`;
                });
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.warning_notification'),
                        null,
                        this.$t('globals.icon_warning'),
                        null,
                        `<ul>${errors}</ul>`
                    )
                );
                return null;
            }
            let response = null;
            var form = null;
            if (this.supWhatsappLine.provider_type == PROVIDER_TYPES.GUPSHUP) {
                form = {
                    name: this.supWhatsappLine.nombre,
                    number: this.supWhatsappLine.numero,
                    provider: this.supWhatsappLine.proveedor,
                    configuration: {
                        app_name: this.supWhatsappLine.configuracion.app_name,
                        app_id: this.supWhatsappLine.configuracion.app_id
                    },
                    destination: this.getDestinationData(),
                    schedule: this.form.horario,
                    welcome_message: this.form.mensaje_bienvenida,
                    farewell_message: this.form.mensaje_despedida,
                    afterhours_message: this.form.mensaje_fueradehora
                };
            }
            if (this.supWhatsappLine.provider_type == PROVIDER_TYPES.META) {
                form = {
                    name: this.supWhatsappLine.nombre,
                    number: this.supWhatsappLine.numero,
                    provider: this.supWhatsappLine.proveedor,
                    configuration: {
                        waba_id: this.supWhatsappLine.configuracion.app_name,
                        app_id: this.supWhatsappLine.configuracion.app_id,
                        verification_token: this.supWhatsappLine.configuracion.verification_token
                    },
                    destination: this.getDestinationData(),
                    schedule: this.form.horario,
                    welcome_message: this.form.mensaje_bienvenida,
                    farewell_message: this.form.mensaje_despedida,
                    afterhours_message: this.form.mensaje_fueradehora
                };
            }
            response = await this.updateWhatsappLine({
                id: this.supWhatsappLine.id,
                data: form
            });
            const { status, message } = response;
            if (status === HTTP_STATUS.SUCCESS) {
                await this.initWhatsappLines();
                this.$router.push({ name: 'supervisor_whatsapp_lines' });
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.success_notification'),
                        message,
                        this.$t('globals.icon_success')
                    )
                );
            } else {
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.error_notification'),
                        message,
                        this.$t('globals.icon_error')
                    )
                );
            }
        },
        onlyWhatsappHabilitadoChange () {
            if (this.supWhatsappLineCampaigns.length > 0) {
                if (this.only_whatsapp_habilitado) {
                    const manualCampaigns =
                  this.supWhatsappLineCampaigns.filter(
                      (c) => c.type === CAMPAIGN_TYPES.MANUAL && c.whatsapp_habilitado
                  ) || [];
                    const inboundCampaigns =
                  this.supWhatsappLineCampaigns.filter(
                      (c) => c.type === CAMPAIGN_TYPES.INBOUND && c.whatsapp_habilitado
                  ) || [];
                    const previewCampaigns =
                  this.supWhatsappLineCampaigns.filter(
                      (c) => c.type === CAMPAIGN_TYPES.PREVIEW && c.whatsapp_habilitado
                  ) || [];
                    const dialerCampaigns =
                  this.supWhatsappLineCampaigns.filter(
                      (c) => c.type === CAMPAIGN_TYPES.DIALER && c.whatsapp_habilitado
                  ) || [];
                    this.campaings.find((c) => c.type === CAMPAIGN_TYPES.INBOUND).items = inboundCampaigns;
                    this.campaings.find((c) => c.type === CAMPAIGN_TYPES.MANUAL).items = manualCampaigns;
                    this.campaings.find((c) => c.type === CAMPAIGN_TYPES.PREVIEW).items = previewCampaigns;
                    this.campaings.find((c) => c.type === CAMPAIGN_TYPES.DIALER).items = dialerCampaigns;
                } else {
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
                    }
                    if (manualCampaigns.length > 0) {
                        this.campaings.find((c) => c.type === CAMPAIGN_TYPES.MANUAL
                        ).items = manualCampaigns;
                    }
                    if (previewCampaigns.length > 0) {
                        this.campaings.find((c) => c.type === CAMPAIGN_TYPES.PREVIEW
                        ).items = previewCampaigns;
                    }
                    if (dialerCampaigns.length > 0) {
                        this.campaings.find((c) => c.type === CAMPAIGN_TYPES.DIALER
                        ).items = dialerCampaigns;
                    }
                }
            }
        },
        ckeckingCampaign () {
            if (this.form.destination) {
                const campaign_selected = this.supWhatsappLineCampaigns.find((c) => c.id === this.form.destination);
                if (campaign_selected.whatsapp_habilitado === false) {
                    this.$swal(
                        this.$helpers.getToasConfig(
                            this.$t('globals.warning_notification'),
                            this.$t(
                                'forms.whatsapp.line.validations.whatsapp_habilitado'
                            ),
                            this.$t('globals.icon_warning')
                        )
                    );
                }
            }
        }
    },
    watch: {
        isFormToCreate: {
            handler () {},
            deep: true,
            immediate: true
        },
        supWhatsappLineOptions: {
            handler () {
                if (
                    this.form.destination_type ===
            this.destinationType.INTERACTIVE &&
          this.supWhatsappLineOptions.length === 0
                ) {
                    this.isEmptyOptions = true;
                } else {
                    this.isEmptyOptions = false;
                }
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
        supWhatsappMessageTemplates: {
            handler () {
                this.messageTemplates.forEach((group) => {
                    group.items = this.supWhatsappMessageTemplates.filter(
                        (template) => template.type === group.type
                    );
                });
            },
            deep: true,
            immediate: true
        },
        supWhatsappLine: {
            handler (val) {
                if (val && val.destination) {
                    this.initFormBase();
                }
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
