<template>
  <div class="card">
    <div class="grid formgrid">
      <div class="field col-12">
        <label
          :class="{
            'p-error': v$.form.plantilla.$invalid && submitted,
          }"
          >{{ $tc("globals.whatsapp.message_template") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-sitemap"></i>
          </span>
          <Dropdown
            v-model="v$.form.plantilla.$model"
            class="w-full"
            :class="{
              'p-invalid': v$.form.plantilla.$invalid && submitted,
            }"
            :options="templates"
            placeholder="-----"
            optionLabel="nombre"
            optionValue="id"
            :emptyFilterMessage="$t('globals.without_data')"
            :filter="true"
            :showClear="true"
            v-bind:filterPlaceholder="
              $t('globals.find_by', { field: $tc('globals.name') }, 1)
            "
          />
        </div>
        <small
          v-if="
            (v$.form.plantilla.$invalid && submitted) ||
            v$.form.plantilla.$pending.$response
          "
          class="p-error"
        >
          {{
            v$.form.plantilla.required.$message.replace(
              "Value",
              $tc("globals.whatsapp.message_template")
            )
          }}
        </small>
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
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { mapActions, mapState } from 'vuex';
import { TEMPLATE_TYPES } from '@/globals/supervisor/whatsapp/message_template';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            form: {
                plantilla: { required }
            }
        };
    },
    inject: ['$helpers'],
    data () {
        return {
            form: {
                plantilla: null
            },
            submitted: false,
            templateTypes: [
                { name: '-----', value: null },
                {
                    name: this.$t('forms.whatsapp.message_template.types.text'),
                    value: TEMPLATE_TYPES.TEXT
                }
            ],
            templates: []
        };
    },
    created () {
        this.initializeData();
    },
    computed: {
        ...mapState(['supWhatsappMessageTemplates', 'supMessageTemplatesOfGroup'])
    },
    methods: {
        ...mapActions(['addMessageTemplateToGroup']),
        closeModal () {
            this.$emit('closeModalEvent');
            this.initializeData();
        },
        initializeData () {
            this.submitted = false;
        },
        save (isFormValid) {
            this.submitted = true;
            if (!isFormValid) {
                return null;
            }
            this.addMessageTemplateToGroup(this.form.plantilla);
            this.closeModal();
            this.$swal(
                this.$helpers.getToasConfig(
                    this.$t('globals.success_notification'),
                    this.$tc('globals.success_added_type', {
                        type: this.$tc('globals.whatsapp.message_template')
                    }),
                    this.$t('globals.icon_success'),
                    this.$t('globals.how_to_save_changes')
                )
            );
        },
        setTemplates () {
            const $this = this;
            if (
                this.supMessageTemplatesOfGroup &&
        this.supMessageTemplatesOfGroup.length > 0
            ) {
                this.templates = this.supWhatsappMessageTemplates.filter(
                    (t) => !this.supMessageTemplatesOfGroup.includes(t.id)
                ).map(function (t) {
                    const tipo = $this.templateTypes.find(type => type.value === t.type).name;
                    return {
                        id: t.id,
                        nombre: `Tipo (${tipo}): ${t.name}`
                    };
                });
            } else {
                this.templates = this.supWhatsappMessageTemplates.map(function (t) {
                    const tipo = $this.templateTypes.find(type => type.value === t.type).name;
                    return {
                        id: t.id,
                        nombre: `Tipo (${tipo}): ${t.name}`
                    };
                });
            }
        }
    },
    watch: {
        supWhatsappMessageTemplates: {
            handler () {},
            deep: true,
            immediate: true
        },
        supMessageTemplatesOfGroup: {
            handler () {
                this.setTemplates();
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
