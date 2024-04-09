<template>
  <div class="card">
    <div class="grid formgrid">
      <div class="field col-6">
        <label
          id="whatsapp_message_template_nombre"
          :class="{
            'p-error':
              v$.supWhatsappMessageTemplateForm.nombre.$invalid && submitted,
          }"
          >{{ $t("models.whatsapp.message_template.nombre") }}*</label
        >
        <div class="p-inputgroup mt-1">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <InputText
            id="whatsapp_message_template_nombre"
            :class="{
              'p-invalid':
                v$.supWhatsappMessageTemplateForm.nombre.$invalid && submitted,
            }"
            v-model="v$.supWhatsappMessageTemplateForm.nombre.$model"
          />
        </div>
        <small
          v-if="
            (v$.supWhatsappMessageTemplateForm.nombre.$invalid && submitted) ||
            v$.supWhatsappMessageTemplateForm.nombre.$pending.$response
          "
          class="p-error"
          >{{
            v$.supWhatsappMessageTemplateForm.nombre.required.$message.replace(
              "Value",
              $t("models.whatsapp.message_template.nombre")
            )
          }}</small
        >
      </div>
      <div class="field col-6">
        <label
          :class="{
            'p-error':
              v$.supWhatsappMessageTemplateForm.tipo.$invalid && submitted,
          }"
          >{{ $t("models.whatsapp.message_template.tipo") }}*</label
        >
        <div class="p-inputgroup mt-1">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <Dropdown
            class="w-full"
            :class="{
              'p-invalid':
                v$.supWhatsappMessageTemplateForm.tipo.$invalid && submitted,
            }"
            v-model="v$.supWhatsappMessageTemplateForm.tipo.$model"
            :options="templateTypes"
            placeholder="-----"
            optionLabel="name"
            optionValue="value"
            @change="templateTypeChange"
            :emptyFilterMessage="$t('globals.without_data')"
            :filter="true"
            v-bind:filterPlaceholder="
              $t('globals.find_by', { field: $tc('globals.name') }, 1)
            "
          />
        </div>
        <small
          v-if="
            (v$.supWhatsappMessageTemplateForm.tipo.$invalid && submitted) ||
            v$.supWhatsappMessageTemplateForm.tipo.$pending.$response
          "
          class="p-error"
          >{{
            v$.supWhatsappMessageTemplateForm.tipo.required.$message.replace(
              "Value",
              $t("models.whatsapp.message_template.tipo")
            )
          }}</small
        >
      </div>
    </div>
    <div class="grid formgrid">
      <div class="field col-12">
        <FormText
          v-if="supWhatsappMessageTemplateForm.tipo === templates.TEXT"
          ref="formTextRef"
        />
        <FormImage
          v-if="supWhatsappMessageTemplateForm.tipo === templates.IMAGE"
          ref="formImageRef"
        />
        <FormFile
          v-if="supWhatsappMessageTemplateForm.tipo === templates.FILE"
          ref="formFileRef"
        />
        <FormAudio
          v-if="supWhatsappMessageTemplateForm.tipo === templates.AUDIO"
          ref="formAudioRef"
        />
        <FormVideo
          v-if="supWhatsappMessageTemplateForm.tipo === templates.VIDEO"
          ref="formVideoRef"
        />
        <FormSticker
          v-if="supWhatsappMessageTemplateForm.tipo === templates.STICKER"
          ref="formStickerRef"
        />
        <FormContact
          v-if="supWhatsappMessageTemplateForm.tipo === templates.CONTACT"
          ref="formContactRef"
        />
      </div>
    </div>
    <div class="flex justify-content-end flex-wrap mt-4">
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
import { HTTP_STATUS } from '@/globals';
import { TEMPLATE_TYPES } from '@/globals/supervisor/whatsapp/message_template';
import FormText from '@/components/supervisor/whatsapp/message_templates/forms/Text';
import FormContact from '@/components/supervisor/whatsapp/message_templates/forms/Contact';
import FormFile from '@/components/supervisor/whatsapp/message_templates/forms/File';
import FormImage from '@/components/supervisor/whatsapp/message_templates/forms/Image';
import FormAudio from '@/components/supervisor/whatsapp/message_templates/forms/Audio';
import FormVideo from '@/components/supervisor/whatsapp/message_templates/forms/Video';
import FormSticker from '@/components/supervisor/whatsapp/message_templates/forms/Sticker';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            supWhatsappMessageTemplateForm: {
                nombre: { required },
                tipo: { required }
            }
        };
    },
    components: {
        FormText,
        FormFile,
        FormImage,
        FormContact,
        FormAudio,
        FormVideo,
        FormSticker
    },
    inject: ['$helpers'],
    props: {
        formToCreate: {
            type: Boolean,
            default: true
        }
    },
    data () {
        return {
            supWhatsappMessageTemplateForm: {
                id: null,
                nombre: '',
                tipo: null,
                configuracion: null
            },
            templateTypes: [
                { name: '-----', value: null },
                {
                    name: this.$t('forms.whatsapp.message_template.types.text'),
                    value: TEMPLATE_TYPES.TEXT
                }
                // { name: this.$t('forms.whatsapp.message_template.types.image'), value: TEMPLATE_TYPES.IMAGE },
                // { name: this.$t('forms.whatsapp.message_template.types.file'), value: TEMPLATE_TYPES.FILE },
                // { name: this.$t('forms.whatsapp.message_template.types.audio'), value: TEMPLATE_TYPES.AUDIO },
                // { name: this.$t('forms.whatsapp.message_template.types.video'), value: TEMPLATE_TYPES.VIDEO },
                // { name: this.$t('forms.whatsapp.message_template.types.sticker'), value: TEMPLATE_TYPES.STICKER }
                // { name: this.$t('forms.whatsapp.message_template.types.location'), value: TEMPLATE_TYPES.LOCATION },
                // { name: this.$t('forms.whatsapp.message_template.types.contact'), value: TEMPLATE_TYPES.CONTACT }
            ],
            templates: {
                TEXT: TEMPLATE_TYPES.TEXT,
                IMAGE: TEMPLATE_TYPES.IMAGE,
                FILE: TEMPLATE_TYPES.FILE,
                AUDIO: TEMPLATE_TYPES.AUDIO,
                VIDEO: TEMPLATE_TYPES.VIDEO,
                STICKER: TEMPLATE_TYPES.STICKER,
                INTERACTIVE_LIST: TEMPLATE_TYPES.INTERACTIVE_LIST,
                QUICK_REPLY_TEXT: TEMPLATE_TYPES.QUICK_REPLY_TEXT,
                QUICK_REPLY_IMAGE: TEMPLATE_TYPES.QUICK_REPLY_IMAGE,
                QUICK_REPLY_FILE: TEMPLATE_TYPES.QUICK_REPLY_FILE,
                LOCATION: TEMPLATE_TYPES.LOCATION,
                CONTACT: TEMPLATE_TYPES.CONTACT
            },
            submitted: false,
            filters: null
        };
    },
    created () {
        this.initializeData();
    },
    computed: {
        ...mapState(['supWhatsappMessageTemplate'])
    },
    methods: {
        ...mapActions([
            'createWhatsappMessageTemplate',
            'updateWhatsappMessageTemplate',
            'initWhatsappMessageTemplates',
            'initWhatsappMessageTemplateFormFields'
        ]),
        closeModal () {
            this.$emit('closeModalEvent');
        },
        templateTypeChange () {
            this.initWhatsappMessageTemplateFormFields({
                type: this.supWhatsappMessageTemplateForm.tipo,
                config: this.supWhatsappMessageTemplateForm.configuracion
            });
        },
        initializeData () {
            this.initFormData();
            this.submitted = false;
        },
        initFormData () {
            this.supWhatsappMessageTemplateForm.id =
        this.supWhatsappMessageTemplate.id;
            this.supWhatsappMessageTemplateForm.nombre =
        this.supWhatsappMessageTemplate.nombre;
            this.supWhatsappMessageTemplateForm.tipo =
        this.supWhatsappMessageTemplate.tipo;
            this.supWhatsappMessageTemplateForm.configuracion = this.supWhatsappMessageTemplate.configuracion;
            this.initWhatsappMessageTemplateFormFields({
                type: this.supWhatsappMessageTemplateForm.tipo,
                config: this.supWhatsappMessageTemplateForm.configuracion
            });
        },
        clearFilter () {
            this.initFilters();
        },
        initFilters () {
            this.filters = {
                global: { value: null, matchMode: FilterMatchMode.CONTAINS }
            };
        },
        async save (isFormValid) {
            var config = null;
            if (this.supWhatsappMessageTemplateForm.tipo === TEMPLATE_TYPES.TEXT) {
                config = this.$refs.formTextRef.save();
            } else if (
                this.supWhatsappMessageTemplateForm.tipo === TEMPLATE_TYPES.FILE
            ) {
                config = this.$refs.formFileRef.save();
            } else if (
                this.supWhatsappMessageTemplateForm.tipo === TEMPLATE_TYPES.IMAGE
            ) {
                config = this.$refs.formImageRef.save();
            } else if (
                this.supWhatsappMessageTemplateForm.tipo === TEMPLATE_TYPES.AUDIO
            ) {
                config = this.$refs.formAudioRef.save();
            } else if (
                this.supWhatsappMessageTemplateForm.tipo === TEMPLATE_TYPES.VIDEO
            ) {
                config = this.$refs.formVideoRef.save();
            } else if (
                this.supWhatsappMessageTemplateForm.tipo === TEMPLATE_TYPES.STICKER
            ) {
                config = this.$refs.formStickerRef.save();
            } else if (
                this.supWhatsappMessageTemplateForm.tipo === TEMPLATE_TYPES.LOCATION
            ) {
                config = this.$refs.formLocationRef.save();
            } else if (
                this.supWhatsappMessageTemplateForm.tipo === TEMPLATE_TYPES.CONTACT
            ) {
                config = this.$refs.formContactRef.save();
            }
            this.submitted = true;
            if (!isFormValid) {
                return null;
            }
            this.supWhatsappMessageTemplateForm.configuracion = config;
            const form = {
                name: this.supWhatsappMessageTemplateForm.nombre,
                type: this.supWhatsappMessageTemplateForm.tipo,
                configuration: this.supWhatsappMessageTemplateForm.configuracion
            };
            var response = null;
            if (this.formToCreate) {
                response = await this.createWhatsappMessageTemplate(
                    form
                );
            } else {
                response = await this.updateWhatsappMessageTemplate({
                    id: this.supWhatsappMessageTemplate.id,
                    data: form
                });
            }
            const { status, message } = response;
            if (status === HTTP_STATUS.SUCCESS) {
                await this.initWhatsappMessageTemplates();
                this.$router.push({ name: 'supervisor_whatsapp_message_templates' });
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
            this.closeModal();
        }
    },
    watch: {
        supWhatsappMessageTemplate: {
            handler () {
                if (this.supWhatsappMessageTemplate) {
                    this.initFormData();
                }
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
