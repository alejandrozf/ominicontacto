<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '30vw' }"
    :modal="false"
    :closable="false"
    :header="$tc('globals.pause_set_info', { name: setToEdit.name })"
  >
    <div class="p-fluid grid formgrid p-mt-4">
      <div class="field col-12 md:col-4">
        <label
          for="grupo_nombre"
          :class="{ 'p-error': v$.set_name.$invalid && submitted }"
          >{{ $t("forms.pause_set.new.name") }}*</label
        >
        <div class="p-inputgroup p-mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <InputText
            id="grupo_nombre"
            @input="inputWatcher"
            :placeholder="$t('forms.pause_set.new.enter_name')"
            :class="{ 'p-invalid': v$.set_name.$invalid && submitted }"
            v-model="v$.set_name.$model"
          />
        </div>
        <small
          v-if="
            (v$.set_name.$invalid && submitted) ||
            v$.set_name.$pending.$response
          "
          class="p-error"
          >{{
            v$.set_name.required.$message.replace(
              "Value",
              $t("forms.pause_set.new.name")
            )
          }}</small
        >
      </div>
    </div>

    <template #footer>
      <Button
        :label="$t('globals.close')"
        icon="pi pi-times"
        @click="closeModal"
        class="p-button-text p-button-danger"
      />
      <Button
        :label="$t('globals.save')"
        icon="pi pi-save"
        :disabled="btnEditStatus"
        @click="editGroup(!v$.$invalid)"
        autofocus
      />
    </template>
  </Dialog>
</template>

<script>
import { mapActions } from 'vuex';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            set_name: {
                required
            }
        };
    },
    inject: ['$helpers'],
    props: {
        showModal: {
            type: Boolean,
            default: false
        },
        group: {
            type: Object,
            default: () => {}
        }
    },
    data () {
        return {
            btnEditStatus: true,
            set_name: '',
            submitted: false,
            setToEdit: {
                name: 0,
                id: 0
            }
        };
    },
    methods: {
        ...mapActions(['updatePauseSetName']),
        openModal () {
            this.initializeModalData();
            this.$emit('handleModal', true);
        },
        closeModal () {
            this.initializeModalData();
            this.$emit('handleModal', false);
        },
        async editGroup (isFormValid) {
            this.submitted = true;
            if (!isFormValid) {
                return null;
            }
            this.setToEdit.name = this.set_name;
            const response = await this.updatePauseSetName(this.setToEdit);
            await this.closeModal();
            if (response) {
                this.$emit('initDataEvent');
                await this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.success_notification'),
                        this.$tc('globals.success_updated_type', {
                            type: this.$tc('globals.pause_config')
                        }),
                        this.$t('globals.icon_success')
                    )
                );
            } else {
                await this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.error_notification'),
                        this.$tc('globals.error_to_updated_type', {
                            type: this.$tc('globals.pause_config')
                        }),
                        this.$t('globals.icon_error')
                    )
                );
            }
        },
        initializeModalData () {
            this.set_name = this.group.nombre;
            this.setToEdit.name = this.group.nombre;
            this.setToEdit.id = this.group.id;
            this.submitted = false;
            this.btnEditStatus = true;
        },
        inputWatcher () {
            this.btnEditStatus = this.setToEdit.name === this.set_name;
        }
    },
    watch: {
        group: {
            handler () {
                this.initializeModalData();
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
