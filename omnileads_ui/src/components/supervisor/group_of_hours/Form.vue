<template>
  <div class="card">
    <div class="grid formgrid mt-4">
      <div class="field col-4">
        <label
          id="group_of_hour_name"
          :class="{
            'p-error': v$.groupOfHour.nombre.$invalid && submitted || repeatedGroupOfHourName
          }"
          >{{ $t("models.group_of_hour.name") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <InputText
            id="group_of_hour_name"
            :class="{
              'p-invalid': v$.groupOfHour.nombre.$invalid && submitted || repeatedGroupOfHourName
            }"
            @input="inputGroupOfHourNameEvent"
            :placeholder="$t('forms.group_of_hour.enter_name')"
            v-model="v$.groupOfHour.nombre.$model"
          />
        </div>
        <small
          v-if="
            (v$.groupOfHour.nombre.$invalid && submitted) ||
            v$.groupOfHour.nombre.$pending.$response
          "
          class="p-error"
          >{{
            v$.groupOfHour.nombre.required.$message.replace(
              "Value",
              $t("models.group_of_hour.name")
            )
          }}</small
        >
        <small
          v-if="repeatedGroupOfHourName"
          class="p-error"
          >{{
            $t('forms.group_of_hour.validations.repeated_group_name')
          }}</small
        >
      </div>
    </div>
    <div class="grid formgrid mt-4">
      <div class="field col-12">
        <h2>{{ $tc('globals.time_validation', 2) }}</h2>
        <InlineMessage v-if="emptyTimeValidations" severity="warn" class="mb-3">{{
          $t("forms.group_of_hour.validations.not_empty_time_validations")
        }}</InlineMessage>
        <TimeValidationsTable
          :timeValidations="groupOfHour.validaciones_de_tiempo"
          @handleTimeValidationModalEvent="handleTimeValidationModal"
        />
      </div>
    </div>
    <div class="flex justify-content-end flex-wrap">
      <div class="flex align-items-center justify-content-center">
        <Button
          :label="$t('globals.save')"
          icon="pi pi-save"
          class="mt-4"
          @click="save(!v$.$invalid)"
        />
      </div>
    </div>
    <ModalToHandleTimeValidation
      :timeValidation='timeValidation'
      :showModal="showTimeValidationModal"
      :formToCreate='formToCreateTimeValidation'
      @handleTimeValidationModalEvent="handleTimeValidationModal"
    />
  </div>
</template>

<script>
import { useVuelidate } from '@vuelidate/core';
import { required } from '@vuelidate/validators';
import { mapActions, mapState } from 'vuex';
import TimeValidationsTable from '@/components/supervisor/group_of_hours/TimeValidationsTable';
import ModalToHandleTimeValidation from '@/components/supervisor/group_of_hours/ModalToHandleTimeValidation';
import { HTTP_STATUS } from '@/globals';

export default {
    setup: () => ({ v$: useVuelidate({ $scope: false }) }),
    validations () {
        return {
            groupOfHour: {
                nombre: { required }
            }
        };
    },
    components: {
        TimeValidationsTable,
        ModalToHandleTimeValidation
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
            submitted: false,
            showTimeValidationModal: false,
            emptyTimeValidations: false,
            repeatedGroupOfHourName: false,
            formToCreateTimeValidation: true,
            timeValidation: null
        };
    },
    computed: {
        ...mapState(['groupOfHours', 'groupOfHour'])
    },
    async created () {
        await this.initializeData();
        await this.initGroupOfHours();
    },
    methods: {
        ...mapActions([
            'createGroupOfHour',
            'updateGroupOfHour',
            'initGroupOfHours',
            'initTimeValidation'
        ]),
        initializeData () {
            this.submitted = false;
            this.showTimeValidationModal = false;
            this.emptyTimeValidations = false;
            this.repeatedGroupOfHourName = false;
            this.formToCreateTimeValidation = true;
            this.timeValidation = null;
        },
        checkEmptyTimeValidations () {
            this.emptyTimeValidations =
        this.groupOfHour.validaciones_de_tiempo.length === 0;
        },
        inputGroupOfHourNameEvent () {
            this.repeatedGroupOfHourName = this.groupOfHours.find(
                (data) => data.nombre === this.groupOfHour.nombre
            );
        },
        handleTimeValidationModal (showModal, formToCreate = true, timeValidation = null) {
            this.showTimeValidationModal = showModal;
            this.formToCreateTimeValidation = formToCreate;
            this.timeValidation = timeValidation;
            this.initTimeValidation(timeValidation);
        },
        async save (isFormValid) {
            this.submitted = true;
            this.checkEmptyTimeValidations();
            if (!isFormValid || this.emptyTimeValidations || this.repeatedGroupOfHourName) {
                return null;
            }
            var response = null;
            if (this.formToCreate) {
                response = await this.createGroupOfHour(this.groupOfHour);
            } else {
                response = await this.updateGroupOfHour({
                    id: this.groupOfHour.id,
                    data: this.groupOfHour
                });
            }
            const { status, message } = response;
            if (status === HTTP_STATUS.SUCCESS) {
                await this.initGroupOfHours();
                this.$router.push({ name: 'supervisor_group_of_hours' });
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
        formToCreate: {
            handler () {},
            deep: true,
            immediate: true
        },
        groupOfHour: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
