<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '30vw' }"
    :closable="false"
    :modal="false"
  >
    <template #header>
      <h2 v-if="formToCreate">{{ $t("views.call_dispositions.new_title") }}</h2>
      <h2 v-else>{{ $t("views.call_dispositions.edit_title") }}</h2>
    </template>
    <div class="card">
      <div class="fluid grid formgrid">
        <div class="field col-12">
          <label
            id="call_disposition_name"
            :class="{
              'p-error': v$.callDispositionForm.nombre.$invalid && submitted,
            }"
            >{{ $t("models.call_disposition.name") }}*</label
          >
          <div class="p-inputgroup mt-2">
            <span class="p-inputgroup-addon">
              <i class="pi pi-list"></i>
            </span>
            <InputText
              id="call_disposition_name"
              :class="{
                'p-invalid':
                  v$.callDispositionForm.nombre.$invalid && submitted,
              }"
              :placeholder="$t('forms.call_disposition.enter_name')"
              v-model="v$.callDispositionForm.nombre.$model"
            />
          </div>
          <small
            v-if="
              (v$.callDispositionForm.nombre.$invalid && submitted) ||
              v$.callDispositionForm.nombre.$pending.$response
            "
            class="p-error"
            >{{
              v$.callDispositionForm.nombre.required.$message.replace(
                "Value",
                $t("models.call_disposition.name")
              )
            }}</small
          >
        </div>
      </div>
      <div class="flex justify-content-end flex-wrap">
        <div class="flex align-items-center justify-content-center">
          <Button
            class="p-button-danger p-button-outlined mr-2"
            :label="$t('globals.cancel')"
            @click="closeModal"
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
  </Dialog>
</template>

<script>
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { mapActions } from 'vuex';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            callDispositionForm: {
                nombre: { required }
            }
        };
    },
    inject: ['$helpers'],
    props: {
        formToCreate: {
            type: Boolean,
            default: true
        },
        showModal: {
            type: Boolean,
            default: false
        },
        callDisposition: {
            type: Object,
            default () {
                return {
                    nombre: ''
                };
            }
        }
    },
    data () {
        return {
            callDispositionForm: {
                nombre: ''
            },
            submitted: false,
            filters: null
        };
    },
    created () {
        this.initializeData();
    },
    methods: {
        ...mapActions(['createCallDisposition', 'updateCallDisposition']),
        initializeData () {
            this.initFormData();
            this.submitted = false;
        },
        initFormData () {
            this.callDispositionForm.nombre = this.callDisposition.nombre;
        },
        closeModal () {
            this.submitted = false;
            this.$emit('handleModalEvent', {
                showModal: false,
                toCreate: false,
                callDisposition: { nombre: '' }
            });
        },
        async save (isFormValid) {
            this.submitted = true;
            if (!isFormValid) {
                return null;
            }
            var response = null;
            var successMsg = null;
            var errorMsg = null;
            if (this.formToCreate) {
                response = await this.createCallDisposition(this.callDispositionForm);
                successMsg = this.$tc('globals.success_added_type', {
                    type: this.$tc('globals.call_disposition')
                });
                errorMsg = this.$tc('globals.error_to_created_type', {
                    type: this.$tc('globals.call_disposition')
                });
            } else {
                response = await this.updateCallDisposition({
                    id: this.callDisposition.id,
                    data: this.callDispositionForm
                });
                successMsg = this.$tc('globals.success_updated_type', {
                    type: this.$tc('globals.call_disposition')
                });
                errorMsg = this.$tc('globals.error_to_updated_type', {
                    type: this.$tc('globals.call_disposition')
                });
            }
            this.closeModal();
            if (response) {
                this.$router.push({ name: 'supervisor_call_dispositions' });
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.success_notification'),
                        successMsg,
                        this.$t('globals.icon_success')
                    )
                );
            } else {
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.error_notification'),
                        errorMsg,
                        this.$t('globals.icon_error')
                    )
                );
            }
        }
    },
    watch: {
        callDisposition: {
            handler () {
                this.initFormData();
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
