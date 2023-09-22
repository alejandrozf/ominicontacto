<template>
  <div class="card">
    <div class="grid formgrid mt-4">
      <div class="field col-6">
        <label
          :class="{
            'p-error': v$.form.nombre.$invalid && submitted,
          }"
          >{{ $t("models.whatsapp.group_of_whatsapp_template.nombre") }}*</label
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
              $t("models.whatsapp.group_of_whatsapp_template.nombre")
            )
          }}</small
        >
      </div>
    </div>
    <div class="grid formgrid mt-2">
      <div class="field col-12">
        <h2>Templates</h2>
        <InlineMessage v-if="emptyTemplates" severity="warn" class="mb-3">{{
          $t(
            "forms.whatsapp.group_of_whatsapp_template.validations.not_empty_templates"
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
import PlantillasTable from '@/components/supervisor/whatsapp/group_of_whatsapp_templates/forms/Table';
import PlantillaModal from '@/components/supervisor/whatsapp/group_of_whatsapp_templates/forms/ModalToHandleForm';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            form: {
                nombre: { required },
                templates: { required }
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
                templates: null
            },
            submitted: false,
            filters: null,
            showModal: false,
            emptyTemplates: false
        };
    },
    created () {
        this.initializeData();
    },
    computed: {
        ...mapState([
            'supWhatsappGroupOfWhatsappTemplate',
            'supWhatsappTemplatesOfGroup'
        ])
    },
    methods: {
        ...mapActions([
            'createWhatsappGroupOfWhatsappTemplate',
            'updateWhatsappGroupOfWhatsappTemplate',
            'initWhatsappGroupOfWhatsappTemplates',
            'initSupWhatsappTemplates'
        ]),
        async handleModal ({ showModal = false }) {
            this.showModal = showModal;
            if (showModal) {
                await this.initSupWhatsappTemplates();
            }
        },
        initializeData () {
            this.initFormData();
            this.submitted = false;
        },
        initFormData () {
            this.form.id = this.supWhatsappGroupOfWhatsappTemplate.id;
            this.form.nombre = this.supWhatsappGroupOfWhatsappTemplate.nombre;
            this.form.templates = this.supWhatsappGroupOfWhatsappTemplate.templates;
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
            this.form.templates = this.supWhatsappTemplatesOfGroup;
            this.emptyTemplates = this.form.templates.length === 0;
            if (!isFormValid || this.emptyTemplates) {
                return null;
            }
            const form = {
                name: this.form.nombre,
                templates: this.form.templates
            };
            var response = null;
            if (this.formToCreate) {
                response = await this.createWhatsappGroupOfWhatsappTemplate(form);
            } else {
                response = await this.updateWhatsappGroupOfWhatsappTemplate({
                    id: this.form.id,
                    data: form
                });
            }
            const { status, message } = response;
            if (status === HTTP_STATUS.SUCCESS) {
                await this.initWhatsappGroupOfWhatsappTemplates();
                this.$router.push({
                    name: 'supervisor_whatsapp_group_of_whatsapp_templates'
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
        supWhatsappGroupOfWhatsappTemplate: {
            handler () {
                if (this.supWhatsappGroupOfWhatsappTemplate) {
                    this.initFormData();
                }
            },
            deep: true,
            immediate: true
        },
        supWhatsappTemplatesOfGroup: {
            handler () {
                this.emptyTemplates = this.supWhatsappTemplatesOfGroup.length === 0;
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
