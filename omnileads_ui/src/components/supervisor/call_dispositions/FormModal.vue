<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '30vw' }"
    :closable="false"
    :modal="false"
  >
    <template #header>
      <h2 v-if="formToCreate">{{ $t("views.call_dispositions.new_title") }}</h2>
      <h2 v-if="formToAddSubdisposition">{{ $t("views.call_dispositions.add_subcategory") }}</h2>
      <h2 v-else>{{ $t("views.call_dispositions.edit_title") }}</h2>
    </template>
    <div class="card">
      <div v-if="formToAddSubdisposition==false" class="fluid grid formgrid">
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
      <div class="fluid grid formgrid">
        <div class="field col-12">
            <label>{{ $t("models.call_disposition.subcalificaciones") }}</label>
          <div class="p-inputgroup mt-2">
            <span class="p-inputgroup-addon">
              <i class="pi pi-sitemap"></i>
            </span>
            <Listbox v-model="subcalificacion_selected" :options="callDisposition.subcalificaciones" class="w-full md:w-56" />
          </div>
          <div class="p-inputgroup mt-2">
            <InputText
              id="call_disposition_subcalificaciones"
              :class="{
                'p-invalid':
                  v$.callDispositionForm.subcalificaciones.$invalid && submitted,
              }"
              :placeholder="$t('forms.call_disposition.enter_subdisposition')"
              v-model="subcalificacion_new"
            />
            <Button
              class="p-button-success ml-2"
              icon="pi pi-plus"
              @click="addSubcalificacion()"
            />
            <Button
            class="p-danger ml-2"
            icon="pi pi-times"
            @click="deleteSubcalificacion()"
          />
          </div>
          <small
            v-if="
              (v$.callDispositionForm.subcalificaciones.$invalid && submitted) ||
              v$.callDispositionForm.subcalificaciones.$pending.$response
            "
            class="p-error"
            >{{
              v$.callDispositionForm.subcalificaciones.required.$message.replace(
                "Value",
                $t("models.call_disposition.subcalificaciones")
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
import { removeInPlace } from '@/utils';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            callDispositionForm: {
                nombre: { required },
                subcalificaciones: {}
            }
        };
    },
    inject: ['$helpers'],
    props: {
        formToCreate: {
            type: Boolean,
            default: true
        },
        formToAddSubdisposition: {
            type: Boolean,
            default: false
        },
        showModal: {
            type: Boolean,
            default: false
        },
        callDisposition: {
            type: Object,
            default () {
                return {
                    nombre: '',
                    subcalificaciones: []
                };
            }
        }
    },
    data () {
        return {
            callDispositionForm: {
                nombre: '',
                subcalificaciones: []
            },
            submitted: false,
            filters: null,
            subcalificacion_selected: null,
            subcalificacion_new: null
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
            this.callDispositionForm.subcalificaciones = this.callDisposition.subcalificaciones;
        },
        closeModal () {
            this.submitted = false;
            this.$emit('handleModalEvent', {
                showModal: false,
                toCreate: false,
                toAddSubcategory: false,
                callDisposition: { nombre: '', subcalificaciones: [] }
            });
        },
        addSubcalificacion() {
          this.callDispositionForm.subcalificaciones.push(this.subcalificacion_new)
          this.subcalificacion_new = ""
        },
        deleteSubcalificacion() {
          var arrayCopy;
          arrayCopy = this.callDisposition.subcalificaciones.slice();
          this.callDisposition.subcalificaciones = removeInPlace(arrayCopy, this.subcalificacion_selected);
          this.callDispositionForm.subcalificaciones = this.callDisposition.subcalificaciones
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
            } else if(this.formToAddSubdisposition){
                response = await this.updateCallDisposition({
                      id: this.callDisposition.id,
                      data: this.callDispositionForm
                  });
                  successMsg = this.$tc('globals.success_added', {
                      type: this.$tc('globals.call_disposition')
                  });
                  errorMsg = this.$tc('globals.error_to_updated_type', {
                      type: this.$tc('globals.success_added')
                  });
            }
            else {
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
