<template>
  <div class="card">
    <div class="grid formgrid mt-4">
      <div class="field col-6">
        <label
          :class="{
            'p-error': v$.form.nombre.$invalid && submitted,
          }"
          >{{ $t("models.whatsapp.group_of_message_template.nombre") }}*</label
        >
        <div class="p-inputgroup mt-1">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <InputText
            :class="{
              'p-invalid': v$.form.nombre.$invalid && submitted,
            }"
            v-model="v$.form.nombre.$model"
          />
        </div>
        <small
          v-if="
            (v$.form.nombre.$invalid && submitted) ||
            v$.form.nombre.$pending.$response
          "
          class="p-error"
          >{{
            v$.form.nombre.required.$message.replace(
              "Value",
              $t("models.whatsapp.group_of_message_template.nombre")
            )
          }}</small
        >
      </div>
    </div>
    <div class="grid formgrid mt-2">
      <div class="field col-12">
        <h2>{{ $t("models.whatsapp.group_of_message_template.plantillas") }}</h2>
        <InlineMessage v-if="emptyTemplates" severity="warn" class="mb-3">{{
          $t(
            "forms.whatsapp.group_of_message_template.validations.not_empty_templates"
          )
        }}</InlineMessage>
        <PlantillasTable @handleModalEvent="handleModal" />
      </div>
    </div>
    <div class="flex justify-content-end flex-wrap mt-4">
      <div class="flex align-items-center">
        <Button
          :label="$t('globals.save')"
          icon="pi pi-save"
          @click="save(!v$.$invalid)"
        />
      </div>
    </div>
    <PlantillaModal
      :showModal="showModal"
      :formToCreate="modalFormToCreate"
      @handleModalEvent="handleModal"
    />
  </div>
</template>

<script>
import { FilterMatchMode } from 'primevue/api';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { mapActions, mapState } from 'vuex';
import { HTTP_STATUS } from '@/globals';
import PlantillasTable from '@/components/supervisor/whatsapp/group_of_message_templates/forms/Table';
import PlantillaModal from '@/components/supervisor/whatsapp/group_of_message_templates/forms/ModalToHandleForm';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            form: {
                nombre: { required },
                plantillas: { required }
            }
        };
    },
    components: {
        PlantillasTable,
        PlantillaModal
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
            form: {
                id: null,
                nombre: null,
                plantillas: null
            },
            submitted: false,
            filters: null,
            showModal: false,
            modalFormToCreate: false,
            emptyTemplates: false
        };
    },
    created () {
        this.initializeData();
    },
    computed: {
        ...mapState([
            'supWhatsappGroupOfMessageTemplate',
            'supMessageTemplatesOfGroup'
        ])
    },
    methods: {
        ...mapActions([
            'createWhatsappGroupOfMessageTemplate',
            'updateWhatsappGroupOfMessageTemplate',
            'initWhatsappGroupOfMessageTemplates',
            'initFacebookPageTemplates'
        ]),
        async handleModal ({ showModal = false, formToCreate = false }) {
            this.showModal = showModal;
            if (showModal) {
                await this.initFacebookPageTemplates();
            }
            this.modalFormToCreate = formToCreate;
        },
        initializeData () {
            this.initFormData();
            this.submitted = false;
        },
        initFormData () {
            this.form.id = this.supWhatsappGroupOfMessageTemplate.id;
            this.form.nombre = this.supWhatsappGroupOfMessageTemplate.nombre;
            this.form.plantillas = this.supWhatsappGroupOfMessageTemplate.plantillas;
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
            this.submitted = true;
            this.form.plantillas = this.supMessageTemplatesOfGroup;
            this.emptyTemplates = this.form.plantillas.length === 0;
            if (!isFormValid || this.emptyTemplates) {
                return null;
            }
            var response = null;
            const form = {
                name: this.form.nombre,
                templates: this.form.plantillas
            };
            if (this.formToCreate) {
                response = await this.createWhatsappGroupOfMessageTemplate(form);
            } else {
                response = await this.updateWhatsappGroupOfMessageTemplate({
                    id: this.form.id,
                    data: form
                });
            }
            const { status, message } = response;
            if (status === HTTP_STATUS.SUCCESS) {
                await this.initWhatsappGroupOfMessageTemplates();
                this.$router.push({
                    name: 'supervisor_whatsapp_group_of_message_templates'
                });
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
        supWhatsappGroupOfMessageTemplate: {
            handler () {
                if (this.supWhatsappGroupOfMessageTemplate) {
                    this.initFormData();
                }
            },
            deep: true,
            immediate: true
        },
        supMessageTemplatesOfGroup: {
            handler () {
                this.emptyTemplates = this.supMessageTemplatesOfGroup.length === 0;
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
