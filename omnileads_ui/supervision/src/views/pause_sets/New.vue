<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("globals.new") }} {{ $tc("globals.pause_set") }}</h1>
      </template>
      <template #end>
        <Button
          :label="$t('globals.back')"
          icon="pi pi-arrow-left"
          class="p-button-info mr-2"
          @click="backToPauseSetsList"
        />
      </template>
    </Toolbar>
    <div class="fluid grid formgrid mt-4">
      <div class="field col-12">
        <label
          for="grupo_nombre"
          :class="{ 'p-error': v$.group_name.$invalid && submitted }"
          >{{ $t("forms.pause_set.new.name") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <InputText
            id="grupo_nombre"
            class="w-full"
            :placeholder="$t('forms.pause_set.new.enter_name')"
            :class="{ 'p-invalid': v$.group_name.$invalid && submitted }"
            v-model="v$.group_name.$model"
          />
        </div>
        <small
          v-if="
            (v$.group_name.$invalid && submitted) ||
            v$.group_name.$pending.$response
          "
          class="p-error"
          >{{
            v$.group_name.required.$message.replace(
              "Value",
              $t("forms.pause_set.new.name")
            )
          }}</small
        >
      </div>
    </div>
    <br /><br />
    <hr class="mt-4" />
    <h3>{{ $t("views.pause_sets.configured_pauses") }}</h3>
    <DataTable
      :value="newGroup.pausas"
      class="p-datatable-sm mt-5 editable-cells-table"
      showGridlines
      :scrollable="true"
      scrollHeight="600px"
      responsiveLayout="scroll"
      dataKey="id"
      :rows="10"
      :rowsPerPageOptions="[10, 20, 50]"
      :paginator="true"
      editMode="cell"
      @cell-edit-complete="onEditTimeToEndPause"
      paginatorTemplate="CurrentPageReport FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown"
      :currentPageReportTemplate="
        $t('globals.showing_datatable_info', {
          first: '{first}',
          last: '{last}',
          totalRecords: '{totalRecords}',
        })
      "
      :filters="filters"
      filterDisplay="menu"
      :globalFilterFields="['pausa', 'representative.name']"
    >
      <template #header>
        <div class="flex justify-content-between flex-wrap">
          <div class="flex align-items-center justify-content-center">
            <Button
              type="button"
              icon="pi pi-filter-slash"
              :label="$t('globals.clean_filter')"
              class="p-button-outlined"
              @click="clearFilter2()"
            />
          </div>
          <div class="flex align-items-center justify-content-center">
            <Button
              icon="pi pi-pencil"
              class="p-button-warning mr-2 p-button-rounded p-button-outlined"
              v-tooltip.top="$t('views.pause_sets.how_to_edit_pause_setting')"
            />
            <Button
              icon="pi pi-plus"
              class="mr-2"
              @click="newPauseConfigModal"
              v-tooltip.top="title2"
            />
            <span class="p-input-icon-left">
              <i class="pi pi-search" />
              <InputText
                v-model="filters['global'].value"
                icon="pi pi-check"
                :placeholder="
                  $t('globals.find_by', { field: $tc('globals.name', 1) })
                "
              />
            </span>
          </div>
        </div>
      </template>
      <template #empty> {{ $t("globals.without_data") }} </template>
      <template #loading> {{ $t("globals.load_info") }} </template>
      <Column
        field="name"
        :sortable="true"
        :header="$t('models.pause_setting.pause')"
      ></Column>
      <Column
        field="type"
        :sortable="true"
        :header="$t('models.pause_setting.pause_type')"
      ></Column>
      <Column
        field="timeToEndPause"
        :sortable="true"
        :header="$t('models.pause_setting.time_to_end_pause')"
      >
        <template #editor="{ data, field }">
          <InputNumber v-model="data[field]" autofocus />
        </template>
        <template #body="slotProps">
          {{
            slotProps.data.timeToEndPause > 0
              ? formatTime(slotProps.data.timeToEndPause)
              : $t("views.pause_sets.infinite_pause")
          }}
        </template>
      </Column>
      <Column :header="$tc('globals.option', 2)" style="max-width: 25rem">
        <template #body="slotProps">
          <Button
            v-if="newGroup.pausas.length >= 2"
            icon="pi pi-trash"
            class="p-button-danger ml-2"
            @click="removePauseConfig(slotProps.data.pauseId)"
            v-tooltip.top="$t('globals.delete')"
          />
        </template>
      </Column>
    </DataTable>
    <div class="flex justify-content-end flex-wrap">
      <div class="flex align-items-center justify-content-center">
        <Button
          :label="$t('globals.save')"
          icon="pi pi-save"
          class="mt-4"
          @click="createGroup(!v$.$invalid)"
        />
      </div>
    </div>
    <NewConfigPause
      :showModal="showModal"
      :pauses="filteredPauses"
      @handleModal="handleModal"
      @filterPausesEvent="changePauseType"
      @addConfigPauseEvent="addConfigPause"
    ></NewConfigPause>
  </div>
</template>

<script>
import { FilterMatchMode } from 'primevue/api';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { mapActions, mapState } from 'vuex';
import NewConfigPause from '@/components/pause_sets/forms/NewConfigPause';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            group_name: {
                required
            }
        };
    },
    inject: ['$helpers'],
    data () {
        return {
            showModal: false,
            submitted: false,
            group_name: '',
            filters: null,
            newGroup: {
                nombre: '',
                pausas: []
            },
            filteredPauses: [],
            pausesTypeSelected: 1,
            title: this.$tc('globals.new') + ' ' + this.$tc('globals.pause_set'),
            title2: this.$tc('globals.new') + ' ' + this.$tc('globals.pause_config')
        };
    },
    async created () {
        await this.initFilters();
        await this.initActivePauses();
    },
    components: {
        NewConfigPause
    },
    methods: {
        ...mapActions(['createPauseSet', 'initActivePauses']),
        handleModal (show) {
            this.showModal = show;
        },
        newPauseConfigModal () {
            this.filterPauses();
            this.showModal = true;
        },
        backToPauseSetsList () {
            this.initializeData();
            this.$router.push({ name: 'pause_sets' });
        },
        initializeData () {
            this.group_name = '';
            this.submitted = false;
            this.newGroup = {
                nombre: '',
                pausas: []
            };
        },
        clearFilter () {
            this.initFilters();
        },
        initFilters () {
            this.filters = {
                global: { value: null, matchMode: FilterMatchMode.CONTAINS }
            };
        },
        addConfigPause (newPauseConfig) {
            this.newGroup.pausas.push(newPauseConfig);
            this.$swal(
                this.$helpers.getToasConfig(
                    this.$t('globals.success_notification'),
                    this.$tc('globals.success_added_type', {
                        type: this.$tc('globals.pause_config')
                    }),
                    this.$t('globals.icon_success')
                )
            );
        },
        filterPauses () {
            this.filteredPauses = this.activePauses.filter(
                (p) => p.es_productiva === (this.pausesTypeSelected === 1)
            );
            if (this.newGroup.pausas.length > 0) {
                const groupPausesId = this.newGroup.pausas.map((p) => p.pauseId);
                this.filteredPauses = this.filteredPauses.filter((p) => !groupPausesId.includes(p.id));
            }
        },
        changePauseType (type) {
            this.pausesTypeSelected = type;
            this.filterPauses();
        },
        removePauseConfig (id) {
            for (var i = 0; i < this.newGroup.pausas.length; i++) {
                if (this.newGroup.pausas[i].pauseId === id) {
                    this.newGroup.pausas.splice(i, 1);
                }
            }
            this.$swal(
                this.$helpers.getToasConfig(this.$t('globals.success_notification'))
            );
        },
        onEditTimeToEndPause (event) {
            const { data, newValue } = event;
            this.newGroup.pausas.find(function (p) {
                if (p.pauseId === data.pauseId) {
                    p.timeToEndPause = newValue;
                }
            });
        },
        async createGroup (isFormValid) {
            this.submitted = true;
            this.newGroup.nombre = this.group_name;
            if (!isFormValid) {
                return null;
            }
            if (this.newGroup.pausas.length === 0) {
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.warning_notification'),
                        this.$t('views.pause_sets.pause_sets_without_pauses'),
                        this.$t('globals.icon_error')
                    )
                );
                return;
            }
            const response = await this.createPauseSet(this.newGroup);
            this.backToPauseSetsList();
            if (response) {
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.success_notification'),
                        this.$tc('globals.success_added_type', {
                            type: this.$tc('globals.pause_config')
                        }),
                        this.$t('globals.icon_success')
                    )
                );
            } else {
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.error_notification'),
                        this.$tc('globals.error_to_created_type', {
                            type: this.$tc('globals.pause_config')
                        }),
                        this.$t('globals.icon_error')
                    )
                );
            }
        },
        formatTime (sec) {
            return this.$helpers.formatTime(sec);
        }
    },
    computed: {
        ...mapState(['activePauses'])
    }
};
</script>
