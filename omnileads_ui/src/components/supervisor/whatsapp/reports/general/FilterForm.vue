<template>
  <div>
    <div class="flex justify-content-end flex-wrap">
      <div class="flex align-items-center justify-content-center">
        <Button
          type="button"
          icon="pi pi-filter-slash"
          :label="$t('globals.clean_filter')"
          class="p-button-outlined"
          @click="cleanFilters()"
        />
      </div>
    </div>
    <div class="grid">
      <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
        <label
          :class="{
            'p-error': v$.form.startDate.$invalid,
          }"
          >{{
            $t(
              "forms.whatsapp.reports.general.form_filters.start_date"
            )
          }}
          *</label
        >
        <div class="p-inputgroup mt-2">
          <Calendar
            dateFormat="yy-mm-dd"
            :placeholder="
              $t(
                'forms.whatsapp.reports.general.form_filters.placeholders.start_date'
              )
            "
            v-model="v$.form.startDate.$model"
            @date-select="search"
            @today-click="search"
            @clear-click="search"
            :maxDate="maxDate"
            :showIcon="true"
            :showButtonBar="true"
            :class="{
              'p-invalid': v$.form.startDate.$invalid,
            }"
          />
        </div>
        <small
          v-if="
            v$.form.startDate.$invalid || v$.form.startDate.$pending.$response
          "
          class="p-error"
          >{{
            v$.form.startDate.required.$message.replace(
              "Value",
              $t(
                "forms.whatsapp.reports.general.form_filters.start_date"
              )
            )
          }}</small
        >
      </div>
      <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
        <label
          :class="{
            'p-error': v$.form.endDate.$invalid,
          }"
          >{{
            $t(
              "forms.whatsapp.reports.general.form_filters.end_date"
            )
          }}
          *</label
        >
        <div class="p-inputgroup mt-2">
          <Calendar
            dateFormat="yy-mm-dd"
            :placeholder="
              $t(
                'forms.whatsapp.reports.general.form_filters.placeholders.end_date'
              )
            "
            v-model="v$.form.endDate.$model"
            @date-select="search"
            @today-click="search"
            @clear-click="search"
            :maxDate="maxDate"
            :showIcon="true"
            :showButtonBar="true"
            :class="{
              'p-invalid': v$.form.endDate.$invalid,
            }"
          />
        </div>
        <small
          v-if="v$.form.endDate.$invalid || v$.form.endDate.$pending.$response"
          class="p-error"
          >{{
            v$.form.endDate.required.$message.replace(
              "Value",
              $t(
                "forms.whatsapp.reports.general.form_filters.end_date"
              )
            )
          }}</small
        >
      </div>
    </div>
  </div>
</template>

<script>
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { mapActions, mapState } from 'vuex';
import { HTTP_STATUS } from '@/globals';

export default {
    inject: ['$helpers'],
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            form: {
                startDate: { required },
                endDate: { required }
            }
        };
    },
    props: {
        campaignId: {
            type: Number,
            required: true,
            default: null
        }
    },
    data () {
        return {
            form: {
                startDate: new Date(),
                endDate: new Date()
            },
            maxDate: new Date(new Date().getTime() + 24 * 60 * 60 * 1000)
        };
    },
    computed: {
        ...mapState([''])
    },
    async created () {
        await this.search();
    },
    methods: {
        ...mapActions(['initSupWhatsReportGeneral']),
        cleanFilters () {
            this.form.startDate = new Date();
            this.form.endDate = new Date();
            this.search();
        },
        getFormatDate (date = null) {
            if (!date) {
                return null;
            }
            return `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
        },
        async search () {
            if (
                this.v$.form &&
        (this.v$.form.endDate.$invalid || this.v$.form.startDate.$invalid)
            ) {
                return;
            }
            if (this.form.startDate > this.form.endDate) {
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.warning_notification'),
                        this.$t(
                            'forms.whatsapp.reports.general.validations.biggest_start_data'
                        ),
                        this.$t('globals.icon_warning')
                    )
                );
                return;
            }
            if (!this.campaignId) {
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.warning_notification'),
                        this.$t(
                            'forms.whatsapp.reports.general.validations.campaign_required'
                        ),
                        this.$t('globals.icon_warning')
                    )
                );
                return;
            }
            const response = await this.initSupWhatsReportGeneral({
                campaignId: this.campaignId,
                filters: {
                    startDate: this.getFormatDate(this.form.startDate),
                    endDate: this.getFormatDate(this.form.endDate)
                }
            });
            const { status, message } = response;
            if (status === HTTP_STATUS.SUCCESS) {
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
        campaignId: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
