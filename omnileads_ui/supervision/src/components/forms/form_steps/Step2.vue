<template>
  <div class="card">
    <h3>{{ $t("views.form.step2.title") }}</h3>
    <FormFieldsTable
      :fields="newForm.campos.sort((a, b) => (a.orden > b.orden ? 1 : -1))"
      @upEvent="up"
      @downEvent="down"
      @handleModalEvent="handleModal"
      @removeFormFieldEvent="removeFormField"
    />
    <ModalFormField
      :showModal="showModal"
      @handleModalEvent="handleModal"
      @addFieldEvent="addFielToForm"
    />
    <div class="flex justify-content-between flex-wrap">
      <div class="flex align-items-center justify-content-center">
        <Button
          :label="$t('globals.back')"
          icon="pi pi-angle-left"
          icon-pos="right"
          class="mt-4 p-button-secondary"
          @click="prevPage"
        />
      </div>
      <div class="flex align-items-center justify-content-center">
        <Button
          :label="$t('globals.next')"
          icon="pi pi-angle-right"
          icon-pos="right"
          class="mt-4 p-button-secondary"
          @click="nextPage"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import FormFieldsTable from '@/components/forms/FormFieldsTable';
import ModalFormField from '@/components/forms/ModalFormField';

export default {
    inject: ['$helpers'],
    data () {
        return {
            showModal: false
        };
    },
    components: {
        FormFieldsTable,
        ModalFormField
    },
    computed: {
        ...mapState(['newForm'])
    },
    methods: {
        ...mapActions(['removeFormField']),
        nextPage () {
            if (this.newForm.campos.length === 0) {
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.warning_notification'),
                        this.$t('forms.form.validations.not_empty_form_field'),
                        this.$t('globals.icon_warning')
                    )
                );
                return null;
            }
            this.$emit('next-page', { pageIndex: 1 });
        },
        prevPage () {
            this.$emit('prev-page', { pageIndex: 1 });
        },
        handleModal (showModal) {
            this.showModal = showModal;
        },
        addFielToForm (formData) {
            this.newForm.campos.push(formData);
            this.showModal = false;
        },
        up (field) {
            const orden = field.orden;
            if (orden > 1) {
                var beforeField = this.newForm.campos.find(
                    (campo) => campo.orden === orden - 1
                );
                var currentField = this.newForm.campos.find(
                    (campo) => campo.orden === orden
                );
                beforeField.orden = orden;
                currentField.orden = orden - 1;
            }
        },
        down (field) {
            const orden = field.orden;
            if (this.newForm.campos.length > orden) {
                var currentField = this.newForm.campos.find(
                    (campo) => campo.orden === orden
                );
                var afterField = this.newForm.campos.find(
                    (campo) => campo.orden === orden + 1
                );
                afterField.orden = orden;
                currentField.orden = orden + 1;
            }
        }
    }
};
</script>
