<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '40vw' }"
    :closable="false"
    :modal="false"
  >
    <template #header>
      <h2>
        {{
          formToCreate
            ? $t("views.time_validation.new_title")
            : $t("views.time_validation.edit_title")
        }}
      </h2>
    </template>
    <div class="card">
      <div class="grid formgrid">
        <div class="field col-6">
          <label
            id="tiempo_inicial"
            :class="{
              'p-error':
                v$.timeValidationForm.tiempo_inicial.$invalid && submitted,
            }"
            >{{ $t("models.time_validation.tiempo_inicial") }}*</label
          >
          <div class="p-inputgroup mt-2">
            <Calendar
              v-model="v$.timeValidationForm.tiempo_inicial.$model"
              :showTime="true"
              :timeOnly="true"
              hourFormat="24"
              :class="{
                'p-invalid':
                  v$.timeValidationForm.tiempo_inicial.$invalid && submitted,
              }"
            />
          </div>
          <small
            v-if="
              (v$.timeValidationForm.tiempo_inicial.$invalid && submitted) ||
              v$.timeValidationForm.tiempo_inicial.$pending.$response
            "
            class="p-error"
            >{{
              v$.timeValidationForm.tiempo_inicial.required.$message.replace(
                "Value",
                $t("models.time_validation.tiempo_inicial")
              )
            }}</small
          >
        </div>
        <div class="field col-6">
          <label
            id="tiempo_final"
            :class="{
              'p-error':
                v$.timeValidationForm.tiempo_final.$invalid && submitted,
            }"
            >{{ $t("models.time_validation.tiempo_final") }}*</label
          >
          <div class="p-inputgroup mt-2">
            <Calendar
              v-model="v$.timeValidationForm.tiempo_final.$model"
              :showTime="true"
              :timeOnly="true"
              hourFormat="24"
              :class="{
                'p-invalid':
                  v$.timeValidationForm.tiempo_final.$invalid && submitted,
              }"
            />
          </div>
          <small
            v-if="
              (v$.timeValidationForm.tiempo_final.$invalid && submitted) ||
              v$.timeValidationForm.tiempo_final.$pending.$response
            "
            class="p-error"
            >{{
              v$.timeValidationForm.tiempo_final.required.$message.replace(
                "Value",
                $t("models.time_validation.tiempo_final")
              )
            }}</small
          >
        </div>
      </div>
      <div class="grid formgrid mt-4">
        <div class="field col-6">
          <label>{{ $t("models.time_validation.dia_semana_inicial") }}</label>
          <Dropdown
            v-model="timeValidationForm.dia_semana_inicial"
            class="w-full"
            :options="weekdays"
            optionLabel="option"
            optionValue="value"
            placeholder="-------"
            :emptyFilterMessage="$t('globals.without_data')"
            :filter="true"
            v-bind:filterPlaceholder="
              $t('globals.find_by', { field: $tc('globals.name') }, 1)
            "
          />
        </div>
        <div class="field col-6">
          <label>{{ $t("models.time_validation.dia_semana_final") }}</label>
          <Dropdown
            v-model="timeValidationForm.dia_semana_final"
            class="w-full"
            :options="weekdays"
            optionLabel="option"
            optionValue="value"
            placeholder="-------"
            :emptyFilterMessage="$t('globals.without_data')"
            :filter="true"
            v-bind:filterPlaceholder="
              $t('globals.find_by', { field: $tc('globals.name') }, 1)
            "
          />
        </div>
      </div>
      <div class="grid formgrid mt-4">
        <div class="field col-6">
          <label>{{ $t("models.time_validation.dia_mes_inicio") }}</label>
          <Dropdown
            v-model="timeValidationForm.dia_mes_inicio"
            class="w-full"
            :options="startDays"
            optionLabel="option"
            optionValue="value"
            placeholder="-------"
            :emptyFilterMessage="$t('globals.without_data')"
            :filter="true"
            v-bind:filterPlaceholder="
              $t('globals.find_by', { field: $tc('globals.name') }, 1)
            "
          />
        </div>
        <div class="field col-6">
          <label>{{ $t("models.time_validation.dia_mes_final") }}</label>
          <Dropdown
            v-model="timeValidationForm.dia_mes_final"
            class="w-full"
            :options="endDays"
            optionLabel="option"
            optionValue="value"
            placeholder="-------"
            :emptyFilterMessage="$t('globals.without_data')"
            :filter="true"
            v-bind:filterPlaceholder="
              $t('globals.find_by', { field: $tc('globals.name') }, 1)
            "
          />
        </div>
      </div>
      <div class="grid formgrid mt-4">
        <div class="field col-6">
          <label>{{ $t("models.time_validation.mes_inicio") }}</label>
          <Dropdown
            v-model="timeValidationForm.mes_inicio"
            class="w-full"
            :options="months"
            optionLabel="option"
            optionValue="value"
            @change='startMonthEvent'
            placeholder="-------"
            :emptyFilterMessage="$t('globals.without_data')"
            :filter="true"
            v-bind:filterPlaceholder="
              $t('globals.find_by', { field: $tc('globals.name') }, 1)
            "
          />
        </div>
        <div class="field col-6">
          <label>{{ $t("models.time_validation.mes_final") }}</label>
          <Dropdown
            v-model="timeValidationForm.mes_final"
            class="w-full"
            :options="months"
            optionLabel="option"
            optionValue="value"
            placeholder="-------"
            @change='endMonthEvent'
            :emptyFilterMessage="$t('globals.without_data')"
            :filter="true"
            v-bind:filterPlaceholder="
              $t('globals.find_by', { field: $tc('globals.name') }, 1)
            "
          />
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
import { mapActions } from 'vuex';

export default {
    setup: () => ({ v$: useVuelidate({ $scope: false }) }),
    validations () {
        return {
            timeValidationForm: {
                tiempo_inicial: { required },
                tiempo_final: { required }
            }
        };
    },
    inject: ['$helpers'],
    props: {
        timeValidations: {
            type: Array,
            default: () => []
        },
        timeValidation: {
            type: Object,
            default: () => null
        },
        showModal: {
            type: Boolean,
            default: false
        },
        formToCreate: {
            type: Boolean,
            default: true
        }
    },
    data () {
        return {
            submitted: false,
            repeatedTimeValidation: false,
            weekdays: [
                { option: '---------', value: null },
                { option: this.$t('globals.monday'), value: 0 },
                { option: this.$t('globals.tuesday'), value: 1 },
                { option: this.$t('globals.wednesday'), value: 2 },
                { option: this.$t('globals.thursday'), value: 3 },
                { option: this.$t('globals.friday'), value: 4 },
                { option: this.$t('globals.saturday'), value: 5 },
                { option: this.$t('globals.sunday'), value: 6 }
            ],
            months: [
                { option: '---------', value: null },
                { option: this.$t('globals.january'), value: 1 },
                { option: this.$t('globals.february'), value: 2 },
                { option: this.$t('globals.march'), value: 3 },
                { option: this.$t('globals.april'), value: 4 },
                { option: this.$t('globals.may'), value: 5 },
                { option: this.$t('globals.june'), value: 6 },
                { option: this.$t('globals.july'), value: 7 },
                { option: this.$t('globals.august'), value: 8 },
                { option: this.$t('globals.september'), value: 9 },
                { option: this.$t('globals.october'), value: 10 },
                { option: this.$t('globals.november'), value: 11 },
                { option: this.$t('globals.december'), value: 12 }
            ],
            startDays: this.getDaysByMonth(),
            endDays: this.getDaysByMonth(),
            timeValidationForm: {
                id: null,
                tiempo_inicial: null,
                tiempo_final: null,
                dia_semana_inicial: null,
                dia_semana_final: null,
                dia_mes_inicio: null,
                dia_mes_final: null,
                mes_inicio: null,
                mes_final: null
            }
        };
    },
    async created () {
        await this.initializeData();
    },
    methods: {
        ...mapActions(['addTimeValidation', 'editTimeValidation']),
        initializeData () {
            this.submitted = false;
            this.repeatedTimeValidation = false;
            this.timeValidationForm = {
                id: null,
                tiempo_inicial: null,
                tiempo_final: null,
                dia_semana_inicial: null,
                dia_semana_final: null,
                dia_mes_inicio: null,
                dia_mes_final: null,
                mes_inicio: null,
                mes_final: null
            };
        },
        initTimeValidationForm () {
            if (this.timeValidation) {
                this.timeValidationForm.id = this.timeValidation.id;
                this.timeValidationForm.tiempo_inicial =
          this.timeValidation.tiempo_inicial;
                this.timeValidationForm.tiempo_final = this.timeValidation.tiempo_final;
                this.timeValidationForm.dia_semana_inicial =
          this.timeValidation.dia_semana_inicial;
                this.timeValidationForm.dia_semana_final =
          this.timeValidation.dia_semana_final;
                this.timeValidationForm.dia_mes_inicio =
          this.timeValidation.dia_mes_inicio;
                this.timeValidationForm.dia_mes_final =
          this.timeValidation.dia_mes_final;
                this.timeValidationForm.mes_inicio = this.timeValidation.mes_inicio;
                this.timeValidationForm.mes_final = this.timeValidation.mes_final;
            }
        },
        getDaysByMonth (month = null) {
            var fin = 31;
            if (month) {
                if (month === 2) {
                    fin = 28;
                } else if ([4, 6, 9, 11].includes(month)) {
                    fin = 30;
                }
            }
            var days = [{ option: '---------', value: null }];
            for (let i = 1; i <= fin; i++) {
                days.push({ option: `${i}`, value: i });
            }
            return days;
        },
        startMonthEvent () {
            this.startDays = this.getDaysByMonth(this.timeValidationForm.mes_inicio);
        },
        endMonthEvent () {
            this.endDays = this.getDaysByMonth(this.timeValidationForm.mes_final);
        },
        closeModal () {
            this.$emit('handleTimeValidationModalEvent', false, true, null);
            this.initializeData();
        },
        inputPatternEvent () {
            this.repeatedTimeValidation = this.timeValidations.find(function (tv) {
                if (this.timeValidationForm.tiempo_inicial === tv.tiempo_inicial &&
                    this.timeValidationForm.tiempo_final === tv.tiempo_final &&
                    this.timeValidationForm.dia_semana_inicial === tv.dia_semana_inicial &&
                    this.timeValidationForm.dia_semana_final === tv.dia_semana_final &&
                    this.timeValidationForm.dia_mes_inicio === tv.dia_mes_inicio &&
                    this.timeValidationForm.dia_mes_final === tv.dia_mes_final &&
                    this.timeValidationForm.mes_inicio === tv.mes_inicio &&
                    this.timeValidationForm.mes_final === tv.mes_final
                ) {
                    return true;
                } else {
                    return false;
                }
            });
        },
        async save (isFormValid) {
            this.submitted = true;
            if (!isFormValid || this.repeatedTimeValidation) {
                return null;
            }
            if (this.timeValidationForm.tiempo_inicial instanceof Date) {
                const startTime = new Date(this.timeValidationForm.tiempo_inicial);
                this.timeValidationForm.tiempo_inicial = `${startTime.getHours() > 9 ? startTime.getHours() : '0' + startTime.getHours()}:${startTime.getMinutes() > 9 ? startTime.getMinutes() : '0' + startTime.getMinutes()}:00`;
            }
            if (this.timeValidationForm.tiempo_final instanceof Date) {
                const endTime = new Date(this.timeValidationForm.tiempo_final);
                this.timeValidationForm.tiempo_final = `${endTime.getHours() > 9 ? endTime.getHours() : '0' + endTime.getHours()}:${endTime.getMinutes() > 9 ? endTime.getMinutes() : '0' + endTime.getMinutes()}:00`;
            }
            if (this.formToCreate) {
                this.addTimeValidation(this.timeValidationForm);
            } else {
                this.editTimeValidation({ oldTimeValidation: this.timeValidation, newTimeValidation: this.timeValidationForm });
            }
            this.closeModal();
        }
    },
    watch: {
        timeValidations: {
            handler () {},
            deep: true,
            immediate: true
        },
        timeValidation: {
            handler () {
                this.initTimeValidationForm();
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
