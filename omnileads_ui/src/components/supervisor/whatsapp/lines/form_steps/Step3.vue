<template>
  <div class="card">
    <div class="grid mt-4">
      <div class="sm:col-12 md:col-8 lg:col-6 xl:col-6">
        <Fieldset>
          <template #legend>
            {{ $t("views.whatsapp.line.step3.time_group") }}
          </template>
          <div class="grid formgrid">
            <div class="field col-12">
              <label
                :class="{
                  'p-error': v$.form.horario.$invalid && submitted,
                }"
                >{{ $t("models.whatsapp.line.horario") }}*</label
              >
              <div class="p-inputgroup mt-2">
                <Button
                icon="pi pi-clock"
                :label="$t('globals.create')"
                severity="secondary"
                @click="createGroupOfHours"
                />
              </div>
              <div class="p-inputgroup mt-2">
                <span class="p-inputgroup-addon">
                  <i class="pi pi-clock"></i>
                </span>
                <Dropdown
                  v-model="v$.form.horario.$model"
                  class="w-full"
                  :class="{
                    'p-invalid': v$.form.horario.$invalid && submitted,
                  }"
                  :filter="true"
                  :showClear="true"
                  :options="groupOfHours"
                  placeholder="-----"
                  optionLabel="nombre"
                  optionValue="id"
                  :emptyFilterMessage="$t('globals.without_data')"
                />
              </div>
              <small
                v-if="
                  (v$.form.horario.$invalid && submitted) ||
                  v$.form.horario.$pending.$response
                "
                class="p-error"
                >{{
                  v$.form.horario.required.$message.replace(
                    "Value",
                    $t("models.whatsapp.line.horario")
                  )
                }}</small
              >
            </div>
          </div>
        </Fieldset>
      </div>
    </div>
    <div class="grid mt-4">
      <div class="col-12">
        <Fieldset :toggleable="true" :collapsed="false">
          <template #legend>
            {{ $t("views.whatsapp.line.step3.message") }}
          </template>
          <div class="grid">
            <div class="field sm:col-12 md:col-6 lg:col-4 xl:col-4">
              <div class="grid">
                <div class="field col-12">
                  <div>
                    <label
                      >{{ $tc("globals.whatsapp.message_template") }}*</label
                    >
                    <div class="p-inputgroup mt-2">
                      <span class="p-inputgroup-addon">
                        <i class="pi pi-file"></i>
                      </span>
                      <Dropdown
                        v-model="v$.form.mensaje_bienvenida.$model"
                        class="w-full"
                        :options="messageTemplates"
                        @change="msgBienvenidaChange"
                        :filter="true"
                        :resetFilterOnHide="true"
                        :showClear="true"
                        placeholder="-----"
                        optionLabel="name"
                        optionValue="id"
                        optionGroupLabel="label"
                        optionGroupChildren="items"
                        :emptyFilterMessage="$t('globals.without_data')"
                      />
                    </div>
                  </div>
                  <div class="mt-4">
                    <label>{{
                      $t("models.whatsapp.line.mensaje_bienvenida")
                    }}</label>
                    <div class="p-inputgroup mt-2">
                      <Button
                      icon="pi pi-comment"
                      :label="$t('globals.new')"
                      severity="secondary"
                      @click="createNewMessageBienvenida"
                      />
                    </div>
                    <div class="p-inputgroup mt-2">
                      <span class="p-inputgroup-addon">
                        <i class="pi pi-comment"></i>
                      </span>
                      <Textarea
                        v-model="msgBienvenidaContent"
                        :disabled="true"
                        :autoResize="true"
                        rows="15"
                        cols="30"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="field sm:col-12 md:col-6 lg:col-4 xl:col-4">
              <div class="grid">
                <div class="field col-12">
                  <div>
                    <label
                      >{{ $tc("globals.whatsapp.message_template") }}*</label
                    >
                    <div class="p-inputgroup mt-2">
                      <span class="p-inputgroup-addon">
                        <i class="pi pi-file"></i>
                      </span>
                      <Dropdown
                        v-model="v$.form.mensaje_fueradehora.$model"
                        class="w-full"
                        :options="messageTemplates"
                        @change="msgFueraHoraChange"
                        :filter="true"
                        :resetFilterOnHide="true"
                        :showClear="true"
                        placeholder="-----"
                        optionLabel="name"
                        optionValue="id"
                        optionGroupLabel="label"
                        optionGroupChildren="items"
                        :emptyFilterMessage="$t('globals.without_data')"
                      />
                    </div>
                  </div>
                  <div class="mt-4">
                    <label>{{
                      $t("models.whatsapp.line.mensaje_fueradehora")
                    }}</label>
                    <div class="p-inputgroup mt-2">
                      <Button
                      icon="pi pi-comment"
                      :label="$t('globals.new')"
                      severity="secondary"
                      @click="createNewMessageFueraHora"
                      />
                    </div>
                    <div class="p-inputgroup mt-2">
                      <span class="p-inputgroup-addon">
                        <i class="pi pi-comment"></i>
                      </span>
                      <Textarea
                        v-model="msgFueraHoraContent"
                        :disabled="true"
                        :autoResize="true"
                        rows="15"
                        cols="30"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="field sm:col-12 md:col-6 lg:col-4 xl:col-4">
              <div class="grid">
                <div class="field col-12">
                  <div>
                    <label
                      >{{ $tc("globals.whatsapp.message_template") }}*</label
                    >
                    <div class="p-inputgroup mt-2">
                      <span class="p-inputgroup-addon">
                        <i class="pi pi-file"></i>
                      </span>
                      <Dropdown
                        v-model="v$.form.mensaje_despedida.$model"
                        class="w-full"
                        :options="messageTemplates"
                        @change="msgDespedidaChange"
                        :filter="true"
                        :resetFilterOnHide="true"
                        :showClear="true"
                        placeholder="-----"
                        optionLabel="name"
                        optionValue="id"
                        optionGroupLabel="label"
                        optionGroupChildren="items"
                        :emptyFilterMessage="$t('globals.without_data')"
                      />
                    </div>
                  </div>
                  <div class="mt-4">
                    <label>{{
                      $t("models.whatsapp.line.mensaje_despedida")
                    }}</label>
                    <div class="p-inputgroup mt-2">
                      <Button
                      icon="pi pi-comment"
                      :label="$t('globals.new')"
                      severity="secondary"
                      @click="createNewMessageDespedida"
                      />
                    </div>
                    <div class="p-inputgroup mt-2">
                      <span class="p-inputgroup-addon">
                        <i class="pi pi-comment"></i>
                      </span>
                      <Textarea
                        v-model="msgDespedidaContent"
                        :disabled="true"
                        :autoResize="true"
                        rows="15"
                        cols="30"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Fieldset>
      </div>
    </div>
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
            <div class="flex justify-content-between flex-wrap mt-4">
              <div class="flex align-items-center justify-content-center">
              </div>
              <div class="flex align-items-center justify-content-center">
              <Button
                :label="$t('globals.new')"
                icon="pi pi-plus"
                @click="addInteractiveMenuItem"
              />
              </div>
            </div>
              <FormMenuInteractivo :data="menu" :submitted="submitted" v-for="menu in supWhatsappLine.destination.data" :key="menu.id"></FormMenuInteractivo>
            </div>
          </div>
        </Fieldset>
      </div>
    </div>
    <div class="flex justify-content-between flex-wrap mt-4">
      <div class="flex align-items-center justify-content-center">
        <Button
          :label="$t('globals.back')"
          icon="pi pi-angle-left"
          icon-pos="right"
          class="p-button-secondary"
          @click="prevPage"
        />
      </div>
      <div class="flex align-items-center justify-content-center">
        <Button
          :label="$t('globals.save')"
          icon="pi pi-save"
          @click="save(!v$.$invalid)"
        />
      </div>
    </div>
    <ModalNewGroupOfHour
    :showModal="showModalNewGroupOfHour"
    @handleModalEvent="handleModalNewGroupOfHour"
    />
    <ModalNewMessageTemplate
    :showModal="showModalNewMessage"
    @handleModalEvent="handleModalNewMessage"
    />
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { TEMPLATE_TYPES } from '@/globals/supervisor/whatsapp/message_template';
import {
    DESTINATION_TYPES_BACK,
    DESTINATION_FORM_TYPES
} from '@/globals/supervisor/whatsapp/line';
import { CAMPAIGN_TYPES } from '@/globals/supervisor/campaign';
import { HTTP_STATUS } from '@/globals';
import ModalToHandleOption from '@/components/supervisor/whatsapp/lines/options_form/ModalToHandleOption';
import ModalNewGroupOfHour from '@/components/supervisor/whatsapp/lines/options_form/ModalNewGroupOfHour';
import ModalNewMessageTemplate from '@/components/supervisor/whatsapp/lines/options_form/ModalNewMessageTemplate';
import FormMenuInteractivo from '@/components/supervisor/whatsapp/lines/options_form/FormMenuInteractivo';

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
        ModalToHandleOption,
        ModalNewGroupOfHour,
        ModalNewMessageTemplate
    },
    data () {
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
            messageTemplates: [
                {
                    type: TEMPLATE_TYPES.TEXT,
                    label: this.$t('forms.whatsapp.message_template.types.text'),
                    items: []
                }
            ],
            formErrors: [],
            submitted: false,
            msgBienvenidaContent: '',
            msgFueraHoraContent: '',
            msgDespedidaContent: '',
            msgBienvenidaRequired: false,
            msgFueraHoraRequired: false,
            isEmptyOptions: false,
            showModalNewGroupOfHour: false,
            showModalNewMessage: false,
            cratedNewmsgBienvenida: false,
            cratedNewmsgFueraHora: false,
            cratedNewmsgDespedida: false,
        };
    },
    mounted() {
      this.initFormBase()
    },
    computed: {
        ...mapState([
            'supWhatsappLine',
            'groupOfHours',
            'groupOfHour',
            'isFormToCreate',
            'supWhatsappMessageTemplates',
            'supWhatsappLineCampaigns',
            'supWhatsappLineOptions',
            'supWhatsappLineIteractiveForm'
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
        addInteractiveMenuItem() {
          this.supWhatsappLine.destination.data.push({ options: [], id_tmp: +new Date()})
        },
        handleModal ({ showModal = false, formToCreate = false, option = null }) {
            this.showModal = showModal;
            this.formToCreate = formToCreate;
            this.initWhatsappLineOptionForm(option);
        },
        prevPage () {
            this.$emit('prev-page', { pageIndex: 2 });
        },
        msgBienvenidaChange () {
            const messageTemplate = this.supWhatsappMessageTemplates.find(
                (mt) => mt.id === this.form.mensaje_bienvenida
            );
            if (messageTemplate) {
                this.msgBienvenidaContent = JSON.stringify(
                    messageTemplate.configuration
                );
            } else {
                this.msgBienvenidaContent = '';
            }
        },
        msgFueraHoraChange () {
            const messageTemplate = this.supWhatsappMessageTemplates.find(
                (mt) => mt.id === this.form.mensaje_fueradehora
            );
            if (messageTemplate) {
                this.msgFueraHoraContent = JSON.stringify(
                    messageTemplate.configuration
                );
            } else {
                this.msgFueraHoraContent = '';
            }
        },
        msgDespedidaChange () {
            const messageTemplate = this.supWhatsappMessageTemplates.find(
                (mt) => mt.id === this.form.mensaje_despedida
            );
            if (messageTemplate) {
                this.msgDespedidaContent = JSON.stringify(
                    messageTemplate.configuration
                );
            } else {
                this.msgDespedidaContent = '';
            }
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
         this.supWhatsappLine.destination.type = this.destinationType.INTERACTIVE
         if (this.supWhatsappLine.destination.data === null || typeof(this.supWhatsappLine.destination.data) === 'number'){
          this.supWhatsappLine.destination.data = [this.supWhatsappLineIteractiveForm]
         }
        },
        campaignOption () {
            this.supWhatsappLine.destination.type = this.destinationType.CAMPAIGN
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
            const form = {
                name: this.supWhatsappLine.nombre,
                number: this.supWhatsappLine.numero,
                provider: this.supWhatsappLine.proveedor,
                configuration: {
                    app_name: this.supWhatsappLine.configuracion.app_name,
                    app_id: this.supWhatsappLine.configuracion.app_id,
                },
                destination: this.getDestinationData(),
                schedule: this.form.horario,
                welcome_message: this.form.mensaje_bienvenida,
                farewell_message: this.form.mensaje_despedida,
                afterhours_message: this.form.mensaje_fueradehora
            };
            if (this.isFormToCreate) {
              response = await this.createWhatsappLine(form);
            } else {
                response = await this.updateWhatsappLine({
                    id: this.supWhatsappLine.id,
                    data: form
                });
            }
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
                        this.$t('globals.icon_error'),
                    )
                );
            }
        },
        handleModalNewGroupOfHour ({ showModal = false }) {
            this.showModalNewGroupOfHour = showModal;
        },
        createGroupOfHours () {
            this.showModalNewGroupOfHour = true;
            this.handleModalNewGroupOfHour({
                showModal: true
            });
        },
        handleModalNewMessage ({ showModal = false }) {
            this.showModalNewMessage = showModal;
        },
        createNewMessageBienvenida () {
            this.cratedNewmsgBienvenida = true;
            this.showModalNewMessage = true;
            this.handleModalNewMessage({
                showModal: true
            });
        },
        createNewMessageFueraHora () {
            this.cratedNewmsgFueraHora = true;
            this.showModalNewMessage = true;
            this.handleModalNewMessage({
                showModal: true
            });
        },
        createNewMessageDespedida () {
            this.cratedNewmsgDespedida = true;
            this.showModalNewMessage = true;
            this.handleModalNewMessage({
                showModal: true
            });
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
            else {
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
          if (this.form.destination){
            const campaign_selected =this.supWhatsappLineCampaigns.find((c) => c.id === this.form.destination)
            if(campaign_selected.whatsapp_habilitado === false){
              this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.warning_notification'),
                        this.$t(
                            'forms.whatsapp.line.validations.whatsapp_habilitado'
                        ),
                        this.$t('globals.icon_warning'),
                    )
                );
            }
          }
        }
    },
    watch: {
        supWhatsappMessageTemplates: {
            handler () {
                if (this.supWhatsappMessageTemplates.length > 0) {
                    this.messageTemplates.find(
                        (mt) => mt.type === TEMPLATE_TYPES.TEXT
                    ).items = this.supWhatsappMessageTemplates.filter(
                        (mt) => mt.type === TEMPLATE_TYPES.TEXT
                    );
                    this.msgBienvenidaChange();
                    this.msgDespedidaChange();
                    this.msgFueraHoraChange();
                }
            },
            deep: true,
            immediate: true
        },
        isFormToCreate: {
            handler () {},
            deep: true,
            immediate: true
        },
        groupOfHours: {
            handler () {
                if (this.groupOfHours.length > 0 && this.groupOfHour.nombre !== '') {
                    this.form.horario = this.groupOfHours[this.groupOfHours.length - 1].id;
                }
            },
            deep: true,
            immediate: true
        },
        messageTemplates: {
            handler () {
                if (this.messageTemplates[0].items.length > 0) {
                    if (this.cratedNewmsgBienvenida) {
                      this.form.mensaje_bienvenida = this.messageTemplates[0].items[this.messageTemplates[0].items.length - 1].id;
                      this.cratedNewmsgBienvenida = false;
                      this.msgBienvenidaChange();
                    }
                    else if (this.cratedNewmsgFueraHora) {
                      this.form.mensaje_fueradehora = this.messageTemplates[0].items[this.messageTemplates[0].items.length - 1].id;
                      this.cratedNewmsgFueraHora = false;
                      this.msgFueraHoraChange();
                    }
                    else if (this.cratedNewmsgDespedida){
                      this.form.mensaje_despedida = this.messageTemplates[0].items[this.messageTemplates[0].items.length - 1].id;
                      this.cratedNewmsgDespedida = false;
                      this.msgDespedidaChange();
                    }
                }
            },
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
        }
    }
};
</script>
