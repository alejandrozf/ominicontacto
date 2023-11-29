<template>
  <div class="grid">
    <div class="field sm:col-12 md:col-6 lg:col-6 xl:col-6">
      <label
        :class="{
          'p-error': v$.form.startDate.$invalid,
        }"
        >{{
          $t(
            "forms.whatsapp.reports.campaign.conversation.form_filters.start_date"
          )
        }}
        *</label
      >
      <div class="p-inputgroup mt-2">
        <Calendar
          dateFormat="yy-mm-dd"
          :placeholder="
            $t(
              'forms.whatsapp.reports.campaign.conversation.form_filters.placeholders.start_date'
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
              "forms.whatsapp.reports.campaign.conversation.form_filters.start_date"
            )
          )
        }}</small
      >
    </div>
    <div class="field sm:col-12 md:col-6 lg:col-6 xl:col-6">
      <label
        :class="{
          'p-error': v$.form.endDate.$invalid,
        }"
        >{{
          $t(
            "forms.whatsapp.reports.campaign.conversation.form_filters.end_date"
          )
        }}
        *</label
      >
      <div class="p-inputgroup mt-2">
        <Calendar
          dateFormat="yy-mm-dd"
          :placeholder="
            $t(
              'forms.whatsapp.reports.campaign.conversation.form_filters.placeholders.end_date'
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
              "forms.whatsapp.reports.campaign.conversation.form_filters.end_date"
            )
          )
        }}</small
      >
    </div>
    <div class="field sm:col-12 md:col-6 lg:col-6 xl:col-6">
      <label>{{
        $t("forms.whatsapp.reports.campaign.conversation.form_filters.agent")
      }}</label>
      <div class="p-inputgroup mt-2">
        <span class="p-inputgroup-addon">
          <i class="pi pi-users"></i>
        </span>
        <MultiSelect
          @change="search"
          :filterPlaceholder="
            $t('globals.find_by', { field: $tc('globals.name') }, 1)
          "
          :emptyFilterMessage="$t('globals.without_data')"
          :filter="true"
          v-model="form.agents"
          display="chip"
          :options="agents"
          optionLabel="name"
          :placeholder="
            $t(
              'forms.whatsapp.reports.campaign.conversation.form_filters.placeholders.agent'
            )
          "
          class="w-full md:w-20rem"
        />
      </div>
    </div>
    <div class="field sm:col-12 md:col-6 lg:col-6 xl:col-6">
      <label>{{
        $t("forms.whatsapp.reports.campaign.conversation.form_filters.phone")
      }}</label>
      <div class="p-inputgroup mt-2">
        <span class="p-inputgroup-addon">
          <i class="pi pi-phone"></i>
        </span>
        <InputText
          v-model="form.phone"
          class="w-full"
          :placeholder="
            $t(
              'forms.whatsapp.reports.campaign.conversation.form_filters.placeholders.phone'
            )
          "
          @input="search"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { mapActions, mapState } from 'vuex';
// import { HTTP_STATUS } from '@/globals';

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
            required: true
        }
    },
    data () {
        return {
            form: {
                startDate: new Date(),
                endDate: new Date(),
                agents: null,
                phone: null
            },
            agents: [
                {
                    value: -1,
                    name: this.$t(
                        'forms.whatsapp.reports.campaign.conversation.form_filters.placeholders.without_agent'
                    )
                }
            ],
            maxDate: new Date(new Date().getTime() + 24 * 60 * 60 * 1000)
        };
    },
    computed: {
        ...mapState(['supWhatsReportCampaignAgents'])
    },
    async created () {
        await this.search();
    },
    methods: {
        ...mapActions(['initSupWhatsReportCampaignConversations']),
        cleanFilters () {
            this.form.startDate = new Date();
            this.form.endDate = new Date();
            this.form.agents = null;
            this.form.phone = null;
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
                            'forms.whatsapp.reports.campaign.conversation.validations.biggest_start_data'
                        ),
                        this.$t('globals.icon_warning')
                    )
                );
                return;
            }
            await this.initSupWhatsReportCampaignConversations({
                campaignId: this.campaignId,
                filters: {
                    startDate: this.getFormatDate(this.form.startDate),
                    endDate: this.getFormatDate(this.form.endDate),
                    agents: this.form.agents
                        ? this.form.agents.map((a) => a.value)
                        : null,
                    phone: this.form.phone
                }
            });
        }
    },
    watch: {
        campaignId: {
            handler () {},
            deep: true,
            immediate: true
        },
        supWhatsReportCampaignAgents: {
            handler () {
                this.agents = [...this.agents, ...this.supWhatsReportCampaignAgents];
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
