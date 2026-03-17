<template>
  <div class="card">
    <div class="grid formgrid">
      <div v-for="(field, index) in form" :key="index" class="field col-12">
        <label
          :class="{
            'p-error': isEmptyField(field.value) && submitted,
          }"
          >{{ field.name }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <InputText
            :class="{
              'p-invalid': isEmptyField(field.value) && submitted,
            }"
            v-model="field.value"
          />
        </div>
        <small v-if="isEmptyField(field.value) && submitted" class="p-error">{{
          $t("globals.validations.field_is_required", {
            field: field.name,
          })
        }}</small>
      </div>
    </div>
    <Panel header="Vista previa" class="field col-12">
    <div class="bg-gray-100 p-4 border-round-lg flex justify-content-center">
        <div class="bg-white border-round-2xl p-3 shadow-3 w-18rem">
            <!-- HEADER -->
            <!-- HEADER MEDIA -->
            <div v-if="template.configuration.type==='IMAGE'">
                <a :href="template.configuration.link_media" style="text-decoration: none; color: inherit;" target="_blank" download>
                <Image :src="template.configuration.link_media" width="250" />
                </a>
            </div>
            <div v-if="template.configuration.type==='DOCUMENT'">
                <embed
                    :src="template.configuration.link_media"
                    frameBorder="0"
                    scrolling="auto"
                    height="100%"
                    width="100%"
                >
            </div>
            <div v-if="template.configuration.type==='VIDEO'">
                <video width="320" height="240" controls>
                <source :src="template.configuration.link_media" type="video/mp4">
                </video>
            </div>
            <!-- HEADER TEXTO -->
            <p class="m-0 font-bold mb-2">
               {{ getPreviewMessageHeader }}
            </p>
            <!-- BODY -->
            <p class="m-0 mb-3 text-sm line-height-3">
                {{ getPreviewMessage }}
            </p>
            <!-- BUTTONS -->
            <div
            v-if="template.configuration.type === 'BUTTONS' && getPreviewButtons.length"
            class="flex flex-column gap-2 mt-3"
            >
                <button
                    v-for="(btn, index) in getPreviewButtons"
                    :key="index"
                    class="w-full text-center py-3 px-3
                        bg-white
                        border-round-2xl
                        shadow-1
                        text-blue-600
                        border-1 border-200"
                    disabled
                >
                    <div class="font-medium">
                    {{ btn.text }}
                    </div>

                    <div
                    v-if="btn.type === 'URL' && btn.previewUrl"
                    class="text-xs text-500 mt-1"
                    style="overflow-wrap: anywhere;"
                    >
                    {{ btn.previewUrl }}
                    </div>
                </button>
            </div>
        </div>
    </div>

    </Panel>
    <div class="flex justify-content-end flex-wrap mt-2">
      <div class="flex align-items-center">
        <Button
          class="p-button-danger p-button-outlined mr-2"
          :label="$t('globals.cancel')"
          @click="closeModal()"
        />
        <Button :label="$t('globals.send')" icon="pi pi-send" @click="send()" />
      </div>
    </div>
  </div>
</template>

<script>
import { FilterMatchMode } from 'primevue/api';
import { mapActions, mapState } from 'vuex';
import { HTTP_STATUS } from '@/globals';
import { notificationEvent, NOTIFICATION } from '@/globals/agent/whatsapp';

export default {
    inject: ['$helpers'],
    props: {
        template: {
            type: Object,
            default: () => {
                return {
                    id: null,
                    name: '',
                    configuration: {
                        text_header: '',
                        text: '',
                        buttons: [],
                        type: '',
                        numParams_header: 0,
                        numParams_text: 0,
                        numParams_buttons: 0
                    }
                };
            }
        },
        onlyWhatsappTemplates: {
            type: Boolean,
            default: false
        }
    },
    data () {
        return {
            form: {},
            submitted: false,
            filters: null,
            invalidForm: false,
            previewMessage: '',
            conversationId: null
        };
    },
    async created () {
        await this.initializeData();
    },
    computed: {
        ...mapState(['agtWhatsCoversationInfo']),
        getPreviewMessage () {
            if (!this.template.configuration || Object.keys(this.form).length === 0) {
                return this.template.configuration.text;
            }
            const self = this;
            return this.template.configuration.text.replace(
                /{{(\d+)}}/g,
                function (match, numero) {
                    const field = self.form[`param_${numero}`];
                    return field?.value || `${match}`;
                }
            );
        },
        getPreviewMessageHeader () {
            if (!this.template.configuration ||  Object.keys(this.form).length === 0) {
                return this.template.configuration.text_header
            }
            const self = this;
            return this.template.configuration.text_header.replace(
                /{{(\d+)}}/g,
                function (match, numero) {
                    const field = self.form[`param_header_${numero}`];
                    return field?.value || `${match}`;
                }
            );
        },
        getPreviewButtons () {
            if (
            !this.template.configuration ||
            !this.template.configuration.buttons
            ) {
            return [];
            }
            return this.template.configuration.buttons.map((btn) => {
            console.log("btn", btn);
            if (btn.type === 'URL' && btn.url) {
                const parsedUrl = btn.url.replace(/{{(\d+)}}/g, (match, numero) => {
                const field = this.form[`param_buttons_${numero}`];
                console.log("field", field);
                return field?.value || `${match}`;
                });

                return {
                ...btn,
                previewUrl: parsedUrl
                };
            }

            return btn;
            });
        }
    },
    methods: {
        ...mapActions([
            'agtWhatsCoversationSendWhatsappTemplateMessage',
            'agtWhatsCoversationReactiveExpiredConversation'
        ]),
        initializeData () {
            this.initFormData();
            this.submitted = false;
        },
        closeModal () {
            this.clearForm();
            this.$emit('closeModalEvent');
            this.form = {};
        },
        clearForm () {
            for (const clave in this.form) {
                const field = this.form[clave];
                field.value = null;
            }
            this.submitted = false;
        },
        initFormData () {
            this.form = {};
            for (let i = 0; i < this.template.configuration.numParams_text; i++) {
                const name = `param_${i + 1}`;
                this.form[name] = { name, empty: false, value: null };
            }
            for (let i = 0; i < this.template.configuration.numParams_header; i++) {
                const name = `param_header_${i + 1}`;
                this.form[name] = { name, empty: false, value: null };
            }
            for (let i = 0; i < this.template.configuration.numParams_buttons; i++) {
                const name = `param_buttons_${i + 1}`;
                this.form[name] = { name, empty: false, value: null };
            }
        },
        clearFilter () {
            this.initFilters();
        },
        initFilters () {
            this.filters = {
                global: { value: null, matchMode: FilterMatchMode.CONTAINS }
            };template.configuration.text.replace
        },
        isEmptyField (field = null) {
            return field === null || field === undefined || field === '';
        },
        getFormData () {
            const formData = [];
            for (const clave in this.form) {
                if (!clave.startsWith("param_header") && !clave.startsWith("param_buttons")) {
                    const field = this.form[clave];
                    formData.push(field.value);
                }
            }
            return formData;
        },
        getFormDataHeader () {
            const formData = [];
            for (const clave in this.form) {
                if (clave.startsWith("param_header")){
                    const field = this.form[clave];
                    formData.push(field.value);
                }
            }
            return formData;
        },
        getFormDataButtons () {
            const formData = [];
            for (const clave in this.form) {
                if (clave.startsWith("param_buttons")){
                    const field = this.form[clave];
                    formData.push(field.value);
                }
            }
            return formData;
        },
        async send () {
            try {
                this.submitted = true;
                this.invalidForm = false;
                for (const clave in this.form) {
                    const field = this.form[clave];
                    if (this.isEmptyField(field.value)) {
                        this.invalidForm = true;
                        this.form[`${field.name}`].empty = true;
                    } else {
                        this.form[`${field.name}`].empty = false;
                    }
                }
                if (this.invalidForm) return null;
                const messages = JSON.parse(
                    localStorage.getItem('agtWhatsappConversationMessages')
                );
                let result = null;
                const reqData = {
                    conversationId: this.agtWhatsCoversationInfo.id,
                    templateId: this.template.id,
                    phoneLine: this.agtWhatsCoversationInfo.line.number,
                    params_header: this.getFormDataHeader(),
                    params: this.getFormData(),
                    params_buttons: this.getFormDataButtons(),
                    messages,
                    $t: this.$t
                };
                if (this.onlyWhatsappTemplates) {
                    result = await this.agtWhatsCoversationReactiveExpiredConversation(
                        reqData
                    );
                } else {
                    result = await this.agtWhatsCoversationSendWhatsappTemplateMessage(
                        reqData
                    );
                }
                this.closeModal();
                const { status, message } = result;
                if (status === HTTP_STATUS.SUCCESS) {
                    await notificationEvent(
                        NOTIFICATION.TITLES.SUCCESS,
                        message,
                        NOTIFICATION.ICONS.SUCCESS
                    );
                } else {
                    await notificationEvent(
                        NOTIFICATION.TITLES.ERROR,
                        message,template.configuration.text.replace,
                        NOTIFICATION.ICONS.ERROR
                    );
                }
            } catch (error) {
                console.error('ERROR Al crear al enviar template');
                console.error(error);
                await notificationEvent(
                    NOTIFICATION.TITLES.ERROR,
                    this.$t('globals.error_to_process_form'),
                    NOTIFICATION.ICONS.ERROR
                );
            }
        }
    },
    watch: {
        template: {
            handler () {
                if (this.template) {
                    this.initFormData();
                }
            },
            deep: true,
            immediate: true
        },
        agtWhatsCoversationInfo: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
