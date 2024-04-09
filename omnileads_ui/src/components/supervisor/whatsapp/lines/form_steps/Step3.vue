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
                    v$.form.configuracion.tipo_de_destino.$invalid && submitted,
                }"
                >{{ $t("models.whatsapp.line.tipo_de_destino") }}*</label
              >
              <div class="field-radiobutton">
                <RadioButton
                  :value="0"
                  v-model="form.configuracion.tipo_de_destino"
                  @change="campaignOption()"
                />
                <label>{{
                  $t("views.whatsapp.line.tipos_de_destino.campana")
                }}</label>
              </div>
              <div class="field-radiobutton">
                <RadioButton
                  :value="1"
                  v-model="form.configuracion.tipo_de_destino"
                  @change="interactiveOption()"
                />
                <label>{{
                  $t("views.whatsapp.line.tipos_de_destino.interactivo")
                }}</label>
              </div>
              <small
                v-if="
                  (v$.form.configuracion.tipo_de_destino.$invalid &&
                    submitted) ||
                  v$.form.configuracion.tipo_de_destino.$pending.$response
                "
                class="p-error"
                >{{
                  v$.form.configuracion.tipo_de_destino.required.$message.replace(
                    "Value",
                    $t("models.whatsapp.line.tipo_de_destino")
                  )
                }}</small
              >
            </div>
            <div
              class="field col-8"
              v-if="
                form.configuracion.tipo_de_destino === destinationType.CAMPAIGN
              "
            >
              <label
                :class="{
                  'p-error':
                    v$.form.configuracion.destino.$invalid && submitted,
                }"
                >{{ $t("models.whatsapp.line.destino") }}*</label
              >
              <div class="p-inputgroup">
                <span class="p-inputgroup-addon">
                  <i class="pi pi-sign-in"></i>
                </span>
                <Dropdown
                  v-model="v$.form.configuracion.destino.$model"
                  class="w-full"
                  :class="{
                    'p-invalid':
                      v$.form.configuracion.destino.$invalid && submitted,
                  }"
                  :options="campaings"
                  :filter="true"
                  :showClear="true"
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
                  (v$.form.configuracion.destino.$invalid && submitted) ||
                  v$.form.configuracion.destino.$pending.$response
                "
                class="p-error"
                >{{
                  v$.form.configuracion.destino.required.$message.replace(
                    "Value",
                    $t("models.whatsapp.line.destino")
                  )
                }}</small
              >
            </div>
            <div
              class="field col-12"
              v-if="
                form.configuracion.tipo_de_destino ===
                destinationType.INTERACTIVE
              "
            >
              <label
                :class="{
                  'p-error':
                    v$.form.configuracion.destino.$invalid && submitted,
                }"
                >{{ $t("models.whatsapp.line.destino") }}*</label
              >
              <div class="card mt-2">
                <div class="grid formgrid">
                  <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
                    <label
                      :class="{
                        'p-error':
                          isEmptyField(interactiveForm.text) && submitted,
                      }"
                      >{{
                        $t("models.whatsapp.line.interactive_form.text")
                      }}*</label
                    >
                    <div class="p-inputgroup mt-2">
                      <span class="p-inputgroup-addon">
                        <i class="pi pi-comment"></i>
                      </span>
                      <InputText
                        :class="{
                          'p-invalid':
                            isEmptyField(interactiveForm.text) && submitted,
                        }"
                        v-model="interactiveForm.text"
                      />
                    </div>
                    <small
                      v-if="isEmptyField(interactiveForm.text) && submitted"
                      class="p-error"
                    >
                      {{
                        $t(
                          "forms.whatsapp.line.validations.field_is_required",
                          {
                            field: $t(
                              "models.whatsapp.line.interactive_form.text"
                            ),
                          }
                        )
                      }}
                    </small>
                  </div>
                  <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
                    <label
                      :class="{
                        'p-error':
                          isEmptyField(interactiveForm.timeout) && submitted,
                      }"
                      >{{
                        $t("models.whatsapp.line.interactive_form.timeout")
                      }}*</label
                    >
                    <div class="p-inputgroup mt-2">
                      <span class="p-inputgroup-addon">
                        <i class="pi pi-clock"></i>
                      </span>
                      <InputNumber
                        :class="{
                          'p-invalid':
                            isEmptyField(interactiveForm.timeout) && submitted,
                        }"
                        :showButtons="true"
                        :min="0"
                        :max="100"
                        v-model="interactiveForm.timeout"
                      />
                    </div>
                    <small>
                      {{ $t("globals.in_seconds") }}
                    </small>
                    <div
                      v-if="isEmptyField(interactiveForm.timeout) && submitted"
                    >
                      <br />
                      <small class="p-error">
                        {{
                          $t(
                            "forms.whatsapp.line.validations.field_is_required",
                            {
                              field: $t(
                                "models.whatsapp.line.interactive_form.timeout"
                              ),
                            }
                          )
                        }}
                      </small>
                    </div>
                  </div>
                </div>
                <div class="grid formgrid">
                  <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
                    <label
                      :class="{
                        'p-error':
                          isEmptyField(interactiveForm.wrongAnswer) &&
                          submitted,
                      }"
                      >{{
                        $t(
                          "models.whatsapp.line.interactive_form.wrong_answer"
                        )
                      }}*</label
                    >
                    <div class="p-inputgroup mt-2">
                      <span class="p-inputgroup-addon">
                        <i class="pi pi-times-circle"></i>
                      </span>
                      <InputText
                        :class="{
                          'p-invalid':
                            isEmptyField(interactiveForm.wrongAnswer) &&
                            submitted,
                        }"
                        v-model="interactiveForm.wrongAnswer"
                      />
                    </div>
                    <small
                      v-if="
                        isEmptyField(interactiveForm.wrongAnswer) && submitted
                      "
                      class="p-error"
                    >
                      {{
                        $t(
                          "forms.whatsapp.line.validations.field_is_required",
                          {
                            field: $t(
                              "models.whatsapp.line.interactive_form.wrong_answer"
                            ),
                          }
                        )
                      }}
                    </small>
                  </div>
                  <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
                    <label
                      :class="{
                        'p-error':
                          isEmptyField(interactiveForm.successAnswer) &&
                          submitted,
                      }"
                      >{{
                        $t(
                          "models.whatsapp.line.interactive_form.success_answer"
                        )
                      }}*</label
                    >
                    <div class="p-inputgroup mt-2">
                      <span class="p-inputgroup-addon">
                        <i class="pi pi-check-circle"></i>
                      </span>
                      <InputText
                        :class="{
                          'p-invalid':
                            isEmptyField(interactiveForm.successAnswer) &&
                            submitted,
                        }"
                        v-model="interactiveForm.successAnswer"
                      />
                    </div>
                    <small
                      v-if="
                        isEmptyField(interactiveForm.successAnswer) && submitted
                      "
                      class="p-error"
                    >
                      {{
                        $t(
                          "forms.whatsapp.line.validations.field_is_required",
                          {
                            field: $t(
                              "models.whatsapp.line.interactive_form.success_answer"
                            ),
                          }
                        )
                      }}
                    </small>
                  </div>
                </div>
              </div>
              <Message
                v-if="isEmptyOptions"
                class="mt-2 p-0"
                :closable="false"
                severity="warn"
              >
                {{ $t("views.whatsapp.line.step3.empty_options") }}
              </Message>
              <OptionsTable @handleModalEvent="handleModal" />
              <ModalToHandleOption
                :showModal="showModal"
                :formToCreate="formToCreate"
                @handleModalEvent="handleModal"
              />
              <small
                v-if="
                  (v$.form.configuracion.destino.$invalid && submitted) ||
                  v$.form.configuracion.destino.$pending.$response
                "
                class="p-error"
                >{{
                  v$.form.configuracion.destino.required.$message.replace(
                    "Value",
                    $t("models.whatsapp.line.destino")
                  )
                }}</small
              >
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
import OptionsTable from '@/components/supervisor/whatsapp/lines/options_form/OptionsTable';
import ModalToHandleOption from '@/components/supervisor/whatsapp/lines/options_form/ModalToHandleOption';

export default {
    inject: ['$helpers'],
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            form: {
                configuracion: {
                    destino: { required },
                    tipo_de_destino: { required }
                },
                horario: { required },
                mensaje_bienvenida: { required },
                mensaje_despedida: { required },
                mensaje_fueradehora: { required },
            }
        };
    },
    components: {
        ModalToHandleOption,
        OptionsTable
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
                configuracion: {
                    destino: null,
                    tipo_de_destino: 0
                },
                horario: null,
                mensaje_bienvenida: null,
                mensaje_despedida: null,
                mensaje_fueradehora: null,
            },
            showModal: false,
            formToCreate: false,
            destinationType: {
                CAMPAIGN: DESTINATION_FORM_TYPES.CAMPAIGN,
                INTERACTIVE: DESTINATION_FORM_TYPES.INTERACTIVE
            },
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
            isEmptyOptions: false
        };
    },
    computed: {
        ...mapState([
            'supWhatsappLine',
            'groupOfHours',
            'isFormToCreate',
            'supWhatsappMessageTemplates',
            'supWhatsappLineCampaigns',
            'supWhatsappLineOptions'
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
            this.form.configuracion.tipo_de_destino =
        this.supWhatsappLine.configuracion.tipo_de_destino;
            this.form.configuracion.destino =
        this.supWhatsappLine.configuracion.destino;
        },
        initInteractiveForm () {
            this.interactiveForm.text = this.supWhatsappLine.destination.data.text;
            this.interactiveForm.wrongAnswer =
        this.supWhatsappLine.destination.data.wrong_answer;
            this.interactiveForm.successAnswer =
        this.supWhatsappLine.destination.data.success;
            this.interactiveForm.timeout =
        this.supWhatsappLine.destination.data.timeout;
        },
        validateInteractiveForm () {
            this.invalidInteractiveForm = false;
            if (
                this.form.configuracion.tipo_de_destino ===
        this.destinationType.INTERACTIVE
            ) {
                if (
                    this.isEmptyField(this.interactiveForm.text) ||
          this.isEmptyField(this.interactiveForm.wrongAnswer) ||
          this.isEmptyField(this.interactiveForm.successAnswer) ||
          this.isEmptyField(this.interactiveForm.timeout)
                ) {
                    this.invalidInteractiveForm = true;
                }
            }
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
            this.isEmptyOptions =
        this.form.configuracion.tipo_de_destino ===
          this.destinationType.INTERACTIVE &&
        this.supWhatsappLineOptions.length === 0;
            if (this.isEmptyOptions) {
                this.formErrors.push(
                    this.$t('forms.whatsapp.line.options.empty_options')
                );
            }
        },
        interactiveOption () {
            this.isEmptyOptions =
        this.form.configuracion.tipo_de_destino ===
          this.destinationType.INTERACTIVE &&
        this.supWhatsappLineOptions.length === 0;
        },
        campaignOption () {
            this.isEmptyOptions = false;
        },
        getDestinationData () {
            if (
                this.form.configuracion.tipo_de_destino ===
        this.destinationType.CAMPAIGN
            ) {
                return {
                    type: DESTINATION_TYPES_BACK.CAMPAIGN,
                    data: this.form.configuracion.destino
                };
            } else if (
                this.form.configuracion.tipo_de_destino ===
        this.destinationType.INTERACTIVE
            ) {
                return {
                    type: DESTINATION_TYPES_BACK.INTERACTIVE,
                    data: {
                        text: this.interactiveForm.text,
                        wrong_answer: this.interactiveForm.wrongAnswer,
                        success: this.interactiveForm.successAnswer,
                        timeout: this.interactiveForm.timeout,
                        options: this.supWhatsappLineOptions.map((o) => {
                            return {
                                value: o.value,
                                description: o.description,
                                destination: o.destination
                            };
                        })
                    }
                };
            }
        },
        async save (isFormValid) {
            this.submitted = true;
            this.form.configuracion.destino = this.getDestinationData();
            this.validateInteractiveForm();
            if (!isFormValid || this.invalidInteractiveForm) {
                return null;
            }
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
                    destino: this.form.configuracion.destino,
                    tipo_de_destino: this.form.configuracion.tipo_de_destino
                },
                destination: this.form.configuracion.destino,
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
                        this.$t('globals.icon_error')
                    )
                );
            }
        }
    },
    watch: {
        supWhatsappLine: {
            handler () {
                this.initFormBase();
                if (
                    this.form.configuracion.tipo_de_destino ===
          this.destinationType.INTERACTIVE
                ) {
                    this.initInteractiveForm();
                }
            },
            deep: true,
            immediate: true
        },
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
            handler () {},
            deep: true,
            immediate: true
        },
        supWhatsappLineOptions: {
            handler () {
                if (
                    this.form.configuracion.tipo_de_destino ===
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
