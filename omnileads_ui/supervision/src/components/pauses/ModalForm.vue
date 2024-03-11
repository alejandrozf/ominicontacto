<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '60vw' }"
    :closable="false"
    :modal="false"
  >
    <template #header>
      <h2>{{ formToCreate ? $t("forms.pause.new_pause") : $t("forms.pause.edit_pause") }}</h2>
    </template>
    <div class="card">
      <div class="grid formgrid mt-4">
        <div class="field col-6">
          <label
            id="pause_name"
            :class="{
              'p-error': v$.pauseForm.nombre.$invalid && submitted,
            }"
            >{{ $t("models.pause.name") }}*</label
          >
          <div class="p-inputgroup mt-2">
            <span class="p-inputgroup-addon">
              <i class="pi pi-list"></i>
            </span>
            <InputText
              id="pause_name"
              :class="{
                'p-invalid': v$.pauseForm.nombre.$invalid && submitted,
              }"
              @input='inputNameEvent'
              :placeholder="$t('forms.pause.enter_name')"
              v-model="v$.pauseForm.nombre.$model"
            />
          </div>
          <small
            v-if="
              (v$.pauseForm.nombre.$invalid && submitted) ||
              v$.pauseForm.nombre.$pending.$response
            "
            class="p-error"
            >{{
              v$.pauseForm.nombre.required.$message.replace(
                "Value",
                $t("models.pause.name")
              )
            }}</small
          >
          <small
            v-if="repeatedName"
            class="p-error"
            >Ya existe una pausa con ese nombre</small
          >
        </div>
        <div class="field col-6">
          <label
            id="pause_type"
            :class="{
              'p-error': v$.pauseForm.tipo.$invalid && submitted,
            }"
            >{{ $t("models.pause.type") }}*</label
          >
          <Dropdown
            v-model="pauseForm.tipo"
            class="w-full mt-2"
            :class="{
              'p-invalid': v$.pauseForm.tipo.$invalid && submitted,
            }"
            :options="pauseTypes"
            placeholder="-----"
            optionLabel="option"
            optionValue="value"
            :emptyFilterMessage="$t('globals.without_data')"
            :filter="true"
            v-bind:filterPlaceholder="
              $t('globals.find_by', { field: $tc('globals.name') }, 1)
            "
          />
          <small
            v-if="
              (v$.pauseForm.tipo.$invalid && submitted) ||
              v$.pauseForm.tipo.$pending.$response
            "
            class="p-error"
            >{{
              v$.pauseForm.tipo.required.$message.replace(
                "Value",
                $t("models.pause.type")
              )
            }}</small
          >
        </div>
      </div>
    </div>
    <template #footer>
      <div class="flex justify-content-end flex-wrap">
        <Button
          class="p-button-danger p-button-outlined mr-2"
          :label="$t('globals.cancel')"
          @click="closeModal"
        />
        <Button :label="$t('globals.save')" @click="save(!v$.$invalid)" />
      </div>
    </template>
  </Dialog>
</template>

<script>
import { useVuelidate } from '@vuelidate/core';
import { required } from '@vuelidate/validators';
import { mapActions, mapState } from 'vuex';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            pauseForm: {
                nombre: { required },
                tipo: { required }
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
        pauses: {
            type: Array,
            default: () => []
        }
    },
    data () {
        return {
            submitted: false,
            repeatedName: false,
            pauseTypes: [
                { option: this.$t('forms.pause.types.opt1'), value: 'P' },
                { option: this.$t('forms.pause.types.opt2'), value: 'R' }
            ]
        };
    },
    computed: {
        ...mapState(['pauseForm'])
    },
    async created () {
        await this.initializeData();
    },
    methods: {
        ...mapActions(['createPause', 'updatePause', 'initPauseForm', 'initPauses']),
        initializeData () {
            this.submitted = false;
            this.repeatedName = false;
        },
        closeModal () {
            this.$emit('handleModalEvent', {
                showModal: false, formToCreate: false, pause: null
            });
            this.initializeData();
        },
        inputNameEvent () {
            this.repeatedName = this.pauses.find((p) => p.nombre === this.pauseForm.nombre);
        },
        async save (isFormValid) {
            this.submitted = true;
            if (!isFormValid || this.repeatedName) {
                return null;
            }
            var response = null;
            if (this.formToCreate) {
                response = await this.createPause(this.pauseForm);
            } else {
                response = await this.updatePause({
                    id: this.pauseForm.id,
                    data: this.pauseForm
                });
            }
            this.closeModal();
            const { status, message } = response;
            if (status === 'SUCCESS') {
                await this.initPauses();
                this.$router.push({ name: 'pauses' });
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
    }
};
</script>
