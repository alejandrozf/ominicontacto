<template>
<Fieldset :toggleable="true" :collapsed="false">
  <div class="field col-12">
  <div class="card mt-2">
    <div class="grid formgrid">
      <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
        <label
          :class="{
            'p-error':
              isEmptyField(interactiveForm.text) && submitted,
          }"
          >{{
            $t("models.whatsapp.line.interactive_form.text")
          }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-comment"></i>
          </span>
          <InputText
            :class="{
              'p-invalid':
                isEmptyField(interactiveForm.text) && submitted,
            }"
            v-model="interactiveForm.text"
          />
        </div>
        <small
          v-if="isEmptyField(interactiveForm.text) && submitted"
          class="p-error"
        >
          {{
            $t(
              "forms.whatsapp.line.validations.field_is_required",
              {
                field: $t(
                  "models.whatsapp.line.interactive_form.text"
                ),
              }
            )
          }}
        </small>
      </div>
      <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
        <label
          :class="{
            'p-error':
              isEmptyField(interactiveForm.timeout) && submitted,
          }"
          >{{
            $t("models.whatsapp.line.interactive_form.timeout")
          }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-clock"></i>
          </span>
          <InputNumber
            :class="{
              'p-invalid':
                isEmptyField(interactiveForm.timeout) && submitted,
            }"
            :showButtons="true"
            :min="0"
            :max="100"
            v-model="interactiveForm.timeout"
          />
        </div>
        <small>
          {{ $t("globals.in_seconds") }}
        </small>
        <div
          v-if="isEmptyField(interactiveForm.timeout) && submitted"
        >
          <br />
          <small class="p-error">
            {{
              $t(
                "forms.whatsapp.line.validations.field_is_required",
                {
                  field: $t(
                    "models.whatsapp.line.interactive_form.timeout"
                  ),
                }
              )
            }}
          </small>
        </div>
      </div>
    </div>
    <div class="grid formgrid">
      <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
        <label
          :class="{
            'p-error':
              isEmptyField(interactiveForm.wrong_answer) &&
              submitted,
          }"
          >{{
            $t(
              "models.whatsapp.line.interactive_form.wrong_answer"
            )
          }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-times-circle"></i>
          </span>
          <InputText
            :class="{
              'p-invalid':
                isEmptyField(interactiveForm.wrong_answer) &&
                submitted,
            }"
            v-model="interactiveForm.wrong_answer"
          />
        </div>
        <small
          v-if="
            isEmptyField(interactiveForm.wrong_answer) && submitted
          "
          class="p-error"
        >
          {{
            $t(
              "forms.whatsapp.line.validations.field_is_required",
              {
                field: $t(
                  "models.whatsapp.line.interactive_form.wrong_answer"
                ),
              }
            )
          }}
        </small>
      </div>
      <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
        <label
          :class="{
            'p-error':
              isEmptyField(interactiveForm.success) &&
              submitted,
          }"
          >{{
            $t(
              "models.whatsapp.line.interactive_form.success_answer"
            )
          }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-check-circle"></i>
          </span>
          <InputText
            :class="{
              'p-invalid':
                isEmptyField(interactiveForm.success) &&
                submitted,
            }"
            v-model="interactiveForm.success"
          />
        </div>
        <small
          v-if="
            isEmptyField(interactiveForm.success) && submitted
          "
          class="p-error"
        >
          {{
            $t(
              "forms.whatsapp.line.validations.field_is_required",
              {
                field: $t(
                  "models.whatsapp.line.interactive_form.success_answer"
                ),
              }
            )
          }}
        </small>
      </div>
    </div>
  </div>
  <div class="card  mt-2">
    <DataTable
      :value="interactiveForm.options"
      class="p-datatable-sm"
      showGridlines
      :scrollable="true"
      scrollHeight="600px"
      responsiveLayout="scroll"
      dataKey="id"
      :rows="10"
      :rowsPerPageOptions="[10, 20, 50]"
      :paginator="true"
      paginatorTemplate="CurrentPageReport FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown"
      :currentPageReportTemplate="
        $t('globals.showing_datatable_info', {
          first: '{first}',
          last: '{last}',
          totalRecords: '{totalRecords}',
        })
      "
      >
      <template #header>
        <div class="flex justify-content-between flex-wrap">
          <div class="flex align-items-center justify-content-center"></div>
          <div class="flex align-items-center justify-content-center">
            <Button
              type="button"
              icon="pi pi-plus"
              class="p-button-info ml-2"
              @click="newOption()"
            />
          </div>
        </div>
      </template>
      <template #empty> {{ $t("globals.without_data") }} </template>
      <template #loading> {{ $t("globals.load_info") }} </template>
      <Column
        field="value"
        :header="$t('models.whatsapp.line.options.value')"
        :sortable="true"
      ></Column>
      <Column
        field="description"
        :header="$t('models.whatsapp.line.options.description')"
      ></Column>
      <Column
        field="type_option"
        :header="$t('models.whatsapp.line.options.destination_type')"
      >
        <template #body="slotProps">
          {{ getDestinationType(slotProps.data.type_option) }}
        </template>
      </Column>
      <Column
        field="destination"
        :header="$t('models.whatsapp.line.options.destination')"
        :sortable="true"
      >
      <template #body="slotProps">
        {{ getDestination(slotProps.data.destination) }}
      </template>
    </Column>
    <Column :header="$tc('globals.option', 2)" style="max-width: 20rem">
      <template #body="slotProps">
        <Button
          icon="pi pi-pencil"
          class="p-button-warning ml-2"
          @click="edit(slotProps.data)"
          v-tooltip.top="$t('globals.edit')"
        />
        <Button
          icon="pi pi-trash"
          class="p-button-danger ml-2"
          @click="remove(slotProps.data.id)"
          v-tooltip.top="$t('globals.delete')"
        />
      </template>
    </Column>
    </DataTable>
</div>
<ModalToHandleOption
  :showModal="showModal"
  :formToCreate="formToCreate"
  :menuId="interactiveForm.id_tmp"
  @handleModalEvent="handleModalEvent"
/>
</div>
</Fieldset>
</template>

<script>
import { integer, required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { mapActions, mapState } from 'vuex';
import ModalToHandleOption from '@/components/supervisor/whatsapp/lines/options_form/ModalToHandleOption';
import { DESTINATION_OPTION_TYPES } from '@/globals/supervisor/whatsapp/line';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            form: {
              text: { required },
              wrongAnswer: { required },
              successAnswer: { required },
              timeout: { required },
              options: { required }
            }
        };
    },
    inject: ['$helpers'],
    props: {
        data: {
          type: Object,
          default: {}
        }
    },
    components: {
      ModalToHandleOption,
      DESTINATION_OPTION_TYPES
    },
    data () {
        return {
          invalidInteractiveForm: false,
          interactiveForm: Object.assign(this.data),
          destinationTypes: [
                { name: '-------', value: null },
                {
                    name: this.$t('forms.whatsapp.line.destination_types.campaign'),
                    value: DESTINATION_OPTION_TYPES.CAMPAIGN
                },
                {
                    name: this.$t('forms.whatsapp.line.destination_types.menu'),
                    value: DESTINATION_OPTION_TYPES.INTERACTIVE
                }
            ],
          showModal: false
        };
    },
    computed: {
        ...mapState([
            'supWhatsappLineOptionForm',
            'supWhatsappLineCampaigns',
            'supWhatsappLineOptions'
        ])
    },
    methods: {
        ...mapActions([
            'createWhatsappLineOption',
            'updateWhatsappLineOption',
            'initWhatsappLineOptionForm',
            'deleteWhatsappLineOption',
        ]),
        isEmptyField (field = null) {
            return field === null || field === undefined || field === '';
        },
        getDestinationType (type) {
            const destinationType = this.destinationTypes.find((dt) => dt.value === type);
            if (destinationType) {
                return destinationType.name;
            } else {
                return '----------';
            }
        },
        getDestination (id) {
            const campaign = this.supWhatsappLineCampaigns.find((c) => c.id === id);
            if (campaign) {
                return `${campaign.name}`;
            } else {
                return '----------';
            }
        },
        handleModalEvent ({ showModal = false, formToCreate = false }) {
            this.showModal = showModal;
            this.formToCreate = formToCreate;
        },

        newOption () {
            this.initWhatsappLineOptionForm({});
            this.showModal = true;
            this.formToCreate = true;
        },
        edit (option) {
            this.showModal = true;
            this.formToCreate = false;
            this.initWhatsappLineOptionForm(option);
        },
        remove (id) {
            console.log(1, this.interactiveForm.id_tmp)
            this.deleteWhatsappLineOption({
              id: id, menuId: this.interactiveForm.id_tmp
            });
            this.$swal(
                this.$helpers.getToasConfig(
                    this.$t('globals.success_notification'),
                    this.$t('forms.whatsapp.line.options.success_delete'),
                    this.$t('globals.icon_success')
                )
            );
        },
    },
    watch: {
      supWhatsappLineOptions: {
            handler () {
              this.supWhatsappLineOptions.forEach(({menuId, ...option})=>{
                if (option.index !== undefined && menuId === this.interactiveForm.id_tmp) {
                  if (this.interactiveForm.options){
                    const idx = this.interactiveForm.options.findIndex(({index}) => index === option.index)
                    if (idx === -1) {
                      this.interactiveForm.options.push(option)
                    }
                  }
                  else
                    this.interactiveForm.options.push(option)
                }
              })
              // // this.interactiveForm.options = this.supWhatsappLineOptions.filter(
              // //   (option)=>option.menuId === this.interactiveForm.id
              // // )
              // // const {menuId, ...supWhatsappLineOptions} = this.supWhatsappLineOptions[0]
              // // if (menuId === this.interactiveForm.id) {
              // //   console.log("WATCH SI-PICK", this.interactiveForm.id, supWhatsappLineOptions);
              // //   this.interactiveForm.options.push(supWhatsappLineOptions)
              // // } else {
              // //   console.log("WATCH NO-PICK", this.interactiveForm.id, supWhatsappLineOptions);
              // // }
              // console.log(this.supWhatsappLineOptions)
              // // var option = this.supWhatsappLineOptions[0]
              // // if (option)
              // //   this.interactiveForm.options.push(option)
            },
            deep: true,
            immediate: true
      }
      // interactiveForm: {
      //   handler () {
      //     supWhatsappLine.destination.data.push({
      //         text: this.interactiveForm.text,
      //         wrong_answer: this.interactiveForm.wrongAnswer,
      //         success: this.interactiveForm.successAnswer,
      //         timeout: this.interactiveForm.timeout
      //         // options: this.supWhatsappLineOptions.map((o) => {
      //         //     return {
      //         //         value: o.value,
      //         //         description: o.description,
      //         //         destination: o.destination,
      //         //         type_option: o.destinationType
      //         //     };
      //         // })
      //     })
      //   },
      //   deep: true,
      //   immediate: true
      // }
    }
};
</script>
