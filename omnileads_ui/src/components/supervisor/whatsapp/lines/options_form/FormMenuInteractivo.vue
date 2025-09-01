<template>
<div>
<Fieldset :toggleable="true" :collapsed="false">
  <div class="field col-12">
  <div class="card mt-2">
      <div v-if="data.is_main" class="flex flex-wrap mt-2">
        <label> {{ $t("models.whatsapp.line.interactive_form.is_main") }} </label>
        <Checkbox v-model="interactiveForm.is_main" :disabled="true" binary/>
      </div>
      <div v-else class="flex flex-wrap mt-2">
        <Button label="Delete" icon="pi pi-trash" class="p-button-danger ml-2" @click="delete_menu(data.id_tmp)" />
      </div>
  </div>
  <div class="card mt-2">
    <div class="grid formgrid">
      <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
        <label
          :class="{
            'p-error': isNoValidLen(interactiveForm.menu_header, 60) && submitted,
          }"
          >{{
            $t("models.whatsapp.line.interactive_form.menu_header")
          }}</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-comment"></i>
          </span>
          <InputText
            :class="{
              'p-invalid':
                isNoValidLen(interactiveForm.menu_header, 60) && submitted,
            }"
            v-model="interactiveForm.menu_header"
          />
        </div>
        <small> {{
          $t(
            "forms.whatsapp.line.validations.max_len_help",
            {
              max_len: 60
            }
          )
        }}</small><br />
        <small v-if="isNoValidLen(interactiveForm.menu_header, 60) && submitted" class="p-error">
          {{
            $t(
              "forms.whatsapp.line.validations.max_len",
              {
                max_len: 60
              }
            )
          }}
        </small>
      </div>
      <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
        <label
          :class="{
            'p-error':
              (isEmptyField(interactiveForm.menu_body) || isNoValidLen(interactiveForm.menu_body, 1024))&& submitted,
          }"
          >{{
            $t("models.whatsapp.line.interactive_form.menu_body")
          }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-comment"></i>
          </span>
          <InputText
            :class="{
              'p-invalid':
              (isEmptyField(interactiveForm.menu_body) || isNoValidLen(interactiveForm.menu_body, 1024)) && submitted,
            }"
            v-model="interactiveForm.menu_body"
          />
        </div>
        <small> {{
          $t(
            "forms.whatsapp.line.validations.max_len_help",
            {
              max_len: 1024
            }
          )
        }}</small>
        <div
          v-if="isEmptyField(interactiveForm.menu_body) && submitted"
        >
          <small class="p-error">
            {{
              $t(
                "forms.whatsapp.line.validations.field_is_required",
                {
                  field: $t(
                    "models.whatsapp.line.interactive_form.menu_body"
                  ),
                }
              )
            }}
          </small>
        </div>
        <div
          v-if="isNoValidLen(interactiveForm.menu_body, 1024) && submitted"
        >
        <small class="p-error">
          {{
            $t(
              "forms.whatsapp.line.validations.max_len",
              {
                max_len:1024
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
              isNoValidLen(interactiveForm.menu_footer, 60) && submitted,
          }"
        >{{
            $t("models.whatsapp.line.interactive_form.menu_footer")
          }}</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-comment"></i>
          </span>
          <InputText
          :class="{
            'p-invalid':
             isNoValidLen(interactiveForm.menu_footer, 60) && submitted,
          }"
            v-model="interactiveForm.menu_footer"
          />
        </div>
        <small> {{
          $t(
            "forms.whatsapp.line.validations.max_len_help",
            {
              max_len: 60
            }
          )
        }}</small>
        <div
          v-if="isNoValidLen(interactiveForm.menu_footer, 60) && submitted"
        >
          <small class="p-error">
            {{
              $t(
                "forms.whatsapp.line.validations.max_len",
                {
                  max_len:60
                }
              )
            }}
          </small>
        </div>
      </div>
      <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
        <label
          :class="{
            'p-error':
            (isEmptyField(interactiveForm.menu_button) || isNoValidLen(interactiveForm.menu_button, 20)) && submitted,
          }"
          >{{
            $t("models.whatsapp.line.interactive_form.menu_button")
          }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-comment"></i>
          </span>
          <InputText
            :class="{
              'p-invalid':
                (isEmptyField(interactiveForm.menu_button) || isNoValidLen(interactiveForm.menu_button, 20)) && submitted,
            }"
            v-model="interactiveForm.menu_button"
          />
        </div>
        <small> {{
          $t(
            "forms.whatsapp.line.validations.max_len_help",
            {
              max_len: 20
            }
          )
        }}</small>
        <div
          v-if="isEmptyField(interactiveForm.menu_button) && submitted"
        >
          <br />
          <small class="p-error">
            {{
              $t(
                "forms.whatsapp.line.validations.field_is_required",
                {
                  field: $t(
                    "models.whatsapp.line.interactive_form.menu_button"
                  ),
                }
              )
            }}
          </small>
        </div>
        <div
        v-if="isNoValidLen(interactiveForm.menu_button, 20) && submitted"
        >
        <br />
        <small class="p-error">
          {{
            $t(
              "forms.whatsapp.line.validations.max_len",
              {
                max_len: 20
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
        <small> {{
          $t(
            "forms.whatsapp.line.validations.max_len_help",
            {
              max_len: 100
            }
          )
          }}
        </small>
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
        <small> {{
          $t(
            "forms.whatsapp.line.validations.max_len_help",
            {
              max_len: 100
            }
          )
          }}
        </small>
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
        {{ getDestination(slotProps.data) }}
      </template>
    </Column>
    <Column :header="$t('globals.option')" style="max-width: 20rem">
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
          @click="remove(slotProps.data)"
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
</div>
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
              menuHeader: { required },
              menuBody: { required },
              menuFooter: { },
              menuButton: {required },
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
        },
        submitted: {
          type: Boolean,
          default: false
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
            'supWhatsappLine',
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
        isNoValidLen (field = null, max_length=0) {
            if (typeof field === 'string' || field instanceof String)
                return field.length > max_length
            return true
        },
        getDestinationType (type) {
            const destinationType = this.destinationTypes.find((dt) => dt.value === type);
            if (destinationType) {
                return destinationType.name;
            } else {
                return '----------';
            }
        },
        getDestination (data) {
            if (data.type_option === DESTINATION_OPTION_TYPES.CAMPAIGN){
              const campaign = this.supWhatsappLineCampaigns.find((c) => c.id === data.destination);
              if (campaign) {
                  return `${campaign.name}`;
              } else {
                  return '----------';
              }
            } else {
              const menu = this.supWhatsappLine.destination.data.find((c) => c.id_tmp === data.destination);
              if (menu.menu_header){
                return `${menu.menu_header}`;
              } else {
                  return '----------';
              }
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
        remove (option) {
            const id = option.id ? option.id : option.index
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
        delete_menu (menuId) {
          if (menuId !=0){
            this.supWhatsappLine.destination.data = this.supWhatsappLine.destination.data.filter(item => item.id_tmp !== menuId);
          }
        }
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
            },
            deep: true,
            immediate: true
      }
    }
};
</script>
