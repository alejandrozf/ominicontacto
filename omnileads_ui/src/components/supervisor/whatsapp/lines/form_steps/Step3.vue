<template>
  <div class="card">
    <div class="grid formgrid mt-4">
      <div class="col-6">
        <Fieldset>
          <template #legend>
            {{ $t("views.whatsapp.line.step3.destination") }}
          </template>
          <div class="grid formgrid">
            <div class="field col-4">
              <label
                :class="{
                  'p-error':
                    v$.supWhatsappLine.configuracion.tipo_de_destino.$invalid &&
                    submitted,
                }"
                >{{ $t("models.whatsapp.line.tipo_de_destino") }}*</label
              >
              <div class="field-radiobutton">
                <RadioButton
                  :value="0"
                  v-model="supWhatsappLine.configuracion.tipo_de_destino"
                  @click="campaignOption"
                />
                <label>{{
                  $t("views.whatsapp.line.tipos_de_destino.campana")
                }}</label>
              </div>
              <div class="field-radiobutton">
                <RadioButton
                  :value="1"
                  v-model="supWhatsappLine.configuracion.tipo_de_destino"
                  @click="interactiveOption"
                />
                <label>{{
                  $t("views.whatsapp.line.tipos_de_destino.interactivo")
                }}</label>
              </div>
              <small
                v-if="
                  (v$.supWhatsappLine.configuracion.tipo_de_destino.$invalid &&
                    submitted) ||
                  v$.supWhatsappLine.configuracion.tipo_de_destino.$pending
                    .$response
                "
                class="p-error"
                >{{
                  v$.supWhatsappLine.configuracion.tipo_de_destino.required.$message.replace(
                    "Value",
                    $t("models.whatsapp.line.tipo_de_destino")
                  )
                }}</small
              >
            </div>
            <div class="field col-8">
              <label
                :class="{
                  'p-error':
                    v$.supWhatsappLine.configuracion.destino.$invalid &&
                    submitted,
                }"
                >{{ $t("models.whatsapp.line.destino") }}*</label
              >
              <div v-if="supWhatsappLine.configuracion.tipo_de_destino === 0">
                <div class="p-inputgroup">
                  <span class="p-inputgroup-addon">
                    <i class="pi pi-sign-in"></i>
                  </span>
                  <Dropdown
                    v-model="v$.supWhatsappLine.configuracion.destino.$model"
                    class="w-full"
                    :class="{
                      'p-invalid':
                        v$.supWhatsappLine.configuracion.destino.$invalid &&
                        submitted,
                    }"
                    :options="campaings"
                    :filter="true"
                    :showClear="true"
                    placeholder="-----"
                    optionLabel="nombre"
                    optionValue="id"
                    optionGroupLabel="label"
                    optionGroupChildren="items"
                    :emptyFilterMessage="$t('globals.without_data')"
                  />
                </div>
              </div>
              <div v-if="supWhatsappLine.configuracion.tipo_de_destino === 1">
                <div class="p-inputgroup mt-2">
                  <span class="p-inputgroup-addon">
                    <i class="pi pi-comment"></i>
                  </span>
                  <Textarea
                    v-model="v$.supWhatsappLine.configuracion.destino.$model"
                    class="w-full"
                    :class="{
                      'p-invalid':
                        v$.supWhatsappLine.configuracion.destino.$invalid &&
                        submitted,
                    }"
                    rows="5"
                    cols="30"
                  />
                </div>
              </div>
              <small
                v-if="
                  (v$.supWhatsappLine.configuracion.destino.$invalid &&
                    submitted) ||
                  v$.supWhatsappLine.configuracion.destino.$pending.$response
                "
                class="p-error"
                >{{
                  v$.supWhatsappLine.configuracion.destino.required.$message.replace(
                    "Value",
                    $t("models.whatsapp.line.destino")
                  )
                }}</small
              >
            </div>
            <div class="field col-12">
              <label
                :class="{
                  'p-error': v$.supWhatsappLine.horario.$invalid && submitted,
                }"
                >{{ $t("models.whatsapp.line.horario") }}*</label
              >
              <div class="p-inputgroup mt-2">
                <span class="p-inputgroup-addon">
                  <i class="pi pi-clock"></i>
                </span>
                <Dropdown
                  v-model="v$.supWhatsappLine.horario.$model"
                  class="w-full"
                  :class="{
                    'p-invalid':
                      v$.supWhatsappLine.horario.$invalid && submitted,
                  }"
                  :options="groupOfHours"
                  placeholder="-----"
                  optionLabel="nombre"
                  optionValue="id"
                  :emptyFilterMessage="$t('globals.without_data')"
                />
              </div>
              <small
                v-if="
                  (v$.supWhatsappLine.horario.$invalid && submitted) ||
                  v$.supWhatsappLine.horario.$pending.$response
                "
                class="p-error"
                >{{
                  v$.supWhatsappLine.horario.required.$message.replace(
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
    <div class="grid formgrid mt-4">
      <div class="col-12">
        <Fieldset>
          <template #legend>
            {{ $t("views.whatsapp.line.step3.message") }}
          </template>
          <div class="grid">
            <div class="field col-12">
              <div class="grid">
                <div class="field col-6">
                  <label>{{ $tc("globals.whatsapp.message_template") }}*</label>
                  <div class="p-inputgroup">
                    <span class="p-inputgroup-addon">
                      <i class="pi pi-file"></i>
                    </span>
                    <Dropdown
                      v-model="supWhatsappLine.mensaje_bienvenida"
                      class="w-full"
                      :options="messageTemplates"
                      @change="msgBienvenidaChange"
                      :filter="true"
                      :resetFilterOnHide="true"
                      :showClear="true"
                      placeholder="-----"
                      optionLabel="nombre"
                      optionValue="id"
                      optionGroupLabel="label"
                      optionGroupChildren="items"
                      :emptyFilterMessage="$t('globals.without_data')"
                    />
                  </div>
                </div>
                <div class="field col-6">
                  <label>{{
                    $t("models.whatsapp.line.mensaje_bienvenida")
                  }}</label>
                  <div class="p-inputgroup">
                    <span class="p-inputgroup-addon">
                      <i class="pi pi-comment"></i>
                    </span>
                    <Textarea
                      v-model="msgBienvenidaContent"
                      :disabled="true"
                      rows="7"
                      cols="30"
                    />
                  </div>
                </div>
              </div>
            </div>
            <div class="field col-12">
              <div class="grid">
                <div class="field col-6">
                  <label>{{ $tc("globals.whatsapp.message_template") }}*</label>
                  <div class="p-inputgroup">
                    <span class="p-inputgroup-addon">
                      <i class="pi pi-file"></i>
                    </span>
                    <Dropdown
                      v-model="supWhatsappLine.mensaje_fueradehora"
                      class="w-full"
                      :options="messageTemplates"
                      @change="msgFueraHoraChange"
                      :filter="true"
                      :resetFilterOnHide="true"
                      :showClear="true"
                      placeholder="-----"
                      optionLabel="nombre"
                      optionValue="id"
                      optionGroupLabel="label"
                      optionGroupChildren="items"
                      :emptyFilterMessage="$t('globals.without_data')"
                    />
                  </div>
                </div>
                <div class="field col-6">
                  <label>{{
                    $t("models.whatsapp.line.mensaje_fueradehora")
                  }}</label>
                  <div class="p-inputgroup">
                    <span class="p-inputgroup-addon">
                      <i class="pi pi-comment"></i>
                    </span>
                    <Textarea
                      v-model="msgFueraHoraContent"
                      :disabled="true"
                      rows="7"
                      cols="30"
                    />
                  </div>
                </div>
              </div>
            </div>
            <div class="field col-12">
              <div class="grid">
                <div class="field col-6">
                  <label>{{ $tc("globals.whatsapp.message_template") }}*</label>
                  <div class="p-inputgroup">
                    <span class="p-inputgroup-addon">
                      <i class="pi pi-file"></i>
                    </span>
                    <Dropdown
                      v-model="supWhatsappLine.mensaje_despedida"
                      class="w-full"
                      :options="messageTemplates"
                      @change="msgDespedidaChange"
                      :filter="true"
                      :resetFilterOnHide="true"
                      :showClear="true"
                      placeholder="-----"
                      optionLabel="nombre"
                      optionValue="id"
                      optionGroupLabel="label"
                      optionGroupChildren="items"
                      :emptyFilterMessage="$t('globals.without_data')"
                    />
                  </div>
                </div>
                <div class="field col-6">
                  <label>{{
                    $t("models.whatsapp.line.mensaje_despedida")
                  }}</label>
                  <div class="p-inputgroup">
                    <span class="p-inputgroup-addon">
                      <i class="pi pi-comment"></i>
                    </span>
                    <Textarea
                      v-model="msgDespedidaContent"
                      :disabled="true"
                      rows="7"
                      cols="30"
                    />
                  </div>
                </div>
              </div>
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
import { CAMPAIGN_TYPES } from '@/globals/supervisor/campaign';
import { HTTP_STATUS } from '@/globals';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            supWhatsappLine: {
                configuracion: {
                    destino: { required },
                    tipo_de_destino: { required }
                },
                horario: { required }
            }
        };
    },
    inject: ['$helpers'],
    data () {
        return {
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
                },
                {
                    type: TEMPLATE_TYPES.IMAGE,
                    label: this.$t('forms.whatsapp.message_template.types.image'),
                    items: []
                }
            ],
            formErrors: [],
            submitted: false,
            msgBienvenidaContent: '',
            msgFueraHoraContent: '',
            msgDespedidaContent: '',
            msgBienvenidaRequired: false,
            msgFueraHoraRequired: false
        };
    },
    computed: {
        ...mapState([
            'supWhatsappLine',
            'groupOfHours',
            'isFormToCreate',
            'supWhatsappMessageTemplates',
            'supWhatsappLineCampaigns'
        ])
    },
    methods: {
        ...mapActions([
            'createWhatsappLine',
            'updateWhatsappLine',
            'initWhatsappLines'
        ]),
        prevPage () {
            this.$emit('prev-page', { pageIndex: 2 });
        },
        msgBienvenidaChange () {
            const messageTemplate = this.supWhatsappMessageTemplates.find(
                (mt) => mt.id === this.supWhatsappLine.mensaje_bienvenida
            );
            if (messageTemplate) {
                this.msgBienvenidaContent = JSON.stringify(
                    messageTemplate.configuracion
                );
            } else {
                this.msgBienvenidaContent = '';
            }
        },
        msgFueraHoraChange () {
            const messageTemplate = this.supWhatsappMessageTemplates.find(
                (mt) => mt.id === this.supWhatsappLine.mensaje_fueradehora
            );
            if (messageTemplate) {
                this.msgFueraHoraContent = JSON.stringify(
                    messageTemplate.configuracion
                );
            } else {
                this.msgFueraHoraContent = '';
            }
        },
        msgDespedidaChange () {
            const messageTemplate = this.supWhatsappMessageTemplates.find(
                (mt) => mt.id === this.supWhatsappLine.mensaje_despedida
            );
            if (messageTemplate) {
                this.msgDespedidaContent = JSON.stringify(
                    messageTemplate.configuracion
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
        interactiveOption () {},
        campaignOption () {},
        async save (isFormValid) {
            this.submitted = true;
            if (!isFormValid) {
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
            var response = null;
            if (this.isFormToCreate) {
                response = await this.createWhatsappLine(this.supWhatsappLine);
            } else {
                response = await this.updateWhatsappLine({
                    id: this.supWhatsappLine.id,
                    data: this.supWhatsappLine
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
            handler () {},
            deep: true,
            immediate: true
        },
        supWhatsappMessageTemplates: {
            handler () {
                if (this.supWhatsappMessageTemplates.length > 0) {
                    this.messageTemplates.find(
                        (mt) => mt.type === TEMPLATE_TYPES.TEXT
                    ).items = this.supWhatsappMessageTemplates.filter(
                        (mt) => mt.tipo === TEMPLATE_TYPES.TEXT
                    );
                    this.messageTemplates.find(
                        (mt) => mt.type === TEMPLATE_TYPES.IMAGE
                    ).items = this.supWhatsappMessageTemplates.filter(
                        (mt) => mt.tipo === TEMPLATE_TYPES.IMAGE
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
        supWhatsappLineCampaigns: {
            handler () {
                if (this.supWhatsappLineCampaigns.length > 0) {
                    this.campaings.find((c) => c.type === CAMPAIGN_TYPES.INBOUND).items =
            this.supWhatsappLineCampaigns.filter(
                (c) => c.type === CAMPAIGN_TYPES.INBOUND
            );
                    this.campaings.find((c) => c.type === CAMPAIGN_TYPES.MANUAL).items =
            this.supWhatsappLineCampaigns.filter(
                (c) => c.type === CAMPAIGN_TYPES.MANUAL
            );
                    this.campaings.find((c) => c.type === CAMPAIGN_TYPES.PREVIEW).items =
            this.supWhatsappLineCampaigns.filter(
                (c) => c.type === CAMPAIGN_TYPES.PREVIEW
            );
                    this.campaings.find((c) => c.type === CAMPAIGN_TYPES.DIALER).items =
            this.supWhatsappLineCampaigns.filter(
                (c) => c.type === CAMPAIGN_TYPES.DIALER
            );
                }
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
