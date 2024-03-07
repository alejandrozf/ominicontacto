<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '60vw' }"
    :modal="false"
    :closable="false"
    :header="title"
  >
    <div class="grid formgrid mt-4">
      <div class="field col-12">
        <div class="field-checkbox">
          <label>{{ $t("forms.pause_setting.infinite_time") }} </label>
          <Checkbox
            v-model="infinitePause"
            :binary="true"
            @change="setInfinitPause"
          />
        </div>
        <small>{{ $t("views.pause_setting.min_time_allowed") }}</small>
      </div>
    </div>
    <div class="grid formgrid mt-6">
      <div class="field col-4">
        <label for="grupo_pausa_type">{{
          $t("globals.type_of", { type: $t("globals.pause") })
        }}</label>
        <Dropdown
          id="grupo_pausa_type"
          class="w-full mt-2"
          v-model="pausesTypeSelected"
          @change="changePauseType"
          :options="pausesType"
          optionLabel="label"
          optionValue="value"
          :placeholder="$t('globals.filter_by_type', { type: 'tipo' })"
        />
      </div>
      <div class="field col-4">
        <label for="grupo_pausa">{{ $t("globals.pause") }}</label>
        <Dropdown
          id="grupo_pausa"
          class="w-full mt-2"
          v-model="newPauseConfig.pauseId"
          :options="pauses"
          optionLabel="nombre"
          optionValue="id"
          :filter="true"
          :placeholder="
            $tc('globals.select_type', { type: $t('globals.pause') }, 2)
          "
        />
      </div>
      <div class="field col-4">
        <label for="pause_time_to_end">{{
          $t("models.pause_setting.time_to_end_pause")
        }}</label>
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-clock"></i>
          </span>
          <InputNumber
            id="pause_time_to_end"
            class="w-full"
            v-model="newPauseConfig.timeToEndPause"
            @input="inputWatcher"
            :min="0"
            :max="28800"
            :disabled="disableTime"
            :placeholder="$t('forms.pause_setting.enter_time')"
          />
        </div>
        <small id="pause_time_to_end">{{ $t("globals.in_seconds") }}</small>
        <br /><br />
        <small v-if="maxTimeAllowed" style="color: red">{{
          $t("views.pause_setting.max_time_allowed")
        }}</small>
        <small v-if="minTimeAllowed" style="color: red">{{
          $t("views.pause_setting.min_time_allowed")
        }}</small>
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
        :disabled="btnAddPauseStatus"
        :label="$t('globals.add')"
        @click="addConfigPause"
        autofocus
      />
    </template>
  </Dialog>
</template>

<script>
export default {
    props: {
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
            infinitePause: false,
            disableTime: false,
            newPauseConfig: {
                pauseId: 0,
                timeToEndPause: 0,
                name: '',
                type: ''
            },
            pausesTypeSelected: 1,
            pausesType: [
                { label: this.$t('forms.pause.types.opt1'), value: 1 },
                { label: this.$t('forms.pause.types.opt2'), value: 0 }
            ],
            title:
        this.$tc('globals.new', 2) + ' ' + this.$tc('globals.pause_config'),
            btnEditStatus: true,
            maxTimeAllowed: false,
            minTimeAllowed: false
        };
    },
    created () {
        this.cleanNewPauseConfig();
    },
    methods: {
        cleanNewPauseConfig () {
            this.btnEditStatus = true;
            this.maxTimeAllowed = false;
            this.minTimeAllowed = false;
            this.infinitePause = false;
            this.pausesTypeSelected = 1;
            this.disableTime = false;
            this.newPauseConfig = {
                pauseId: 0,
                timeToEndPause: 0,
                name: '',
                type: ''
            };
            const value = this.newPauseConfig.timeToEndPause;
            this.limitNotifications(value);
            this.infinitePause = value === 0 || value === null;
        },
        openModal () {
            this.cleanNewPauseConfig();
            this.$emit('handleModal', true);
        },
        closeModal () {
            this.cleanNewPauseConfig();
            this.$emit('handleModal', false);
        },
        addConfigPause () {
            if (
                this.newPauseConfig.timeToEndPause == null ||
        !this.newPauseConfig.timeToEndPause
            ) {
                this.newPauseConfig.timeToEndPause = 0;
            }
            this.newPauseConfig.type = this.pausesTypeSelected === 1
                ? this.$t('forms.pause.types.opt1')
                : this.$t('forms.pause.types.opt2');
            this.newPauseConfig.name = this.pauses.find(
                (p) => p.id === this.newPauseConfig.pauseId
            ).nombre;
            this.$emit('addConfigPauseEvent', this.newPauseConfig);
            this.closeModal();
        },
        changePauseType () {
            this.$emit('filterPausesEvent', this.pausesTypeSelected);
            this.newPauseConfig.pauseId = 0;
        },
        inputWatcher ({ value }) {
            this.limitNotifications(value);
            this.infinitePause = value === 0 || value === null;
        },
        limitNotifications (value) {
            if (value >= 28800) {
                this.maxTimeAllowed = true;
                this.minTimeAllowed = false;
            } else if (value === 0 || value === null) {
                this.maxTimeAllowed = false;
                this.minTimeAllowed = true;
            } else {
                this.maxTimeAllowed = false;
                this.minTimeAllowed = false;
            }
        },
        setInfinitPause () {
            if (this.infinitePause) {
                this.newPauseConfig.timeToEndPause = 0;
                this.disableTime = true;
            } else {
                this.disableTime = false;
            }

            const value = this.newPauseConfig.timeToEndPause;
            this.limitNotifications(value);

            this.btnEditStatus = this.newPauseConfig.pauseId === 0;
        }
    },
    watch: {
        pauses: {
            handler () {},
            deep: true,
            immediate: true
        }
    },
    computed: {
        btnAddPauseStatus () {
            return this.newPauseConfig.pauseId === 0;
        }
    }
};
</script>
