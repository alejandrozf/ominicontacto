<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '30vw' }"
    :modal="false"
    :closable="false"
    :header="$tc('globals.pause_config_info', { name: pauseConfigToEdit.name })"
  >
    <div class="p-fluid p-grid p-formgrid p-mt-4">
      <div class="field p-col-12">
        <div class="field-checkbox">
          <label>{{ $t("forms.pause_setting.infinite_time") }}  </label>
          <Checkbox
            v-model="infinitePause"
            :binary="true"
            @change="setInfinitPause"
          />
        </div>
        <small>{{ $t("views.pause_setting.min_time_allowed") }}</small>
      </div>
    </div>

    <div class="p-fluid grid p-mt-4">
      <div class="field col-12 md:col-4">
        <label for="pause_time_to_end">{{
          $t("models.pause_setting.time_to_end_pause")
        }}</label>
        <div class="p-inputgroup p-mt-3">
          <span class="p-inputgroup-addon">
            <i class="pi pi-clock"></i>
          </span>
          <InputNumber
            id="pause_time_to_end"
            v-model="pauseConfigToEdit.timeToEndPause"
            :min="0"
            :max="28800"
            :disabled="disableTime"
            @input="inputWatcher"
            :placeholder="$t('forms.pause_setting.enter_time')"
          />
        </div>
        <small id="pause_time_to_end">{{ $t("globals.in_seconds") }}</small>
        <br />
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
        :label="$t('globals.save')"
        :disabled="btnEditStatus"
        icon="pi pi-save"
        @click="editPauseConfig"
        autofocus
      />
    </template>
  </Dialog>
</template>

<script>
import { mapActions } from 'vuex';

export default {
    inject: ['$helpers'],
    props: {
        showModal: {
            type: Boolean,
            default: false
        },
        pauseConfig: {
            type: Object,
            default: () => {}
        }
    },
    data () {
        return {
            infinitePause: false,
            disableTime: false,
            pauseConfigToEdit: {
                timeToEndPause: 0,
                name: '',
                id: 0
            },
            btnEditStatus: true,
            maxTimeAllowed: false,
            minTimeAllowed: false
        };
    },
    created () {
        this.initializeModalData();
    },
    methods: {
        ...mapActions(['updatePauseConfig']),
        openModal () {
            this.initializeModalData();
            this.$emit('handleModal', true);
        },
        closeModal () {
            this.initializeModalData();
            this.$emit('handleModal', false);
        },
        async editPauseConfig () {
            if (
                this.pauseConfigToEdit.timeToEndPause == null ||
        !this.pauseConfigToEdit.timeToEndPause
            ) {
                this.pauseConfigToEdit.timeToEndPause = 0;
            }
            const response = await this.updatePauseConfig(this.pauseConfigToEdit);
            this.closeModal();
            if (response) {
                this.$emit('initDataEvent');
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.success_notification'),
                        this.$tc('globals.success_deleted_type', {
                            type: this.$tc('globals.pause_config')
                        }),
                        this.$t('globals.icon_success')
                    )
                );
            } else {
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.error_notification'),
                        this.$tc('globals.error_to_deleted_type', {
                            type: this.$tc('globals.pause_config')
                        }),
                        this.$t('globals.icon_error')
                    )
                );
            }
        },
        initializeModalData () {
            this.disableTime = false;
            this.btnEditStatus = true;
            this.pauseConfigToEdit.timeToEndPause = parseInt(
                this.pauseConfig.time_to_end_pause
            );
            this.pauseConfigToEdit.name = this.pauseConfig.pause_name;
            this.pauseConfigToEdit.id = parseInt(this.pauseConfig.id);
            const value = this.pauseConfigToEdit.timeToEndPause;
            this.limitNotifications(value);
            this.infinitePause = (value === 0 || value === null);
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
        inputWatcher ({ value }) {
            this.btnEditStatus = value === this.pauseConfigToEdit.timeToEndPause;
            this.infinitePause = (value === 0 || value === null);
            this.limitNotifications(value);
        },
        setInfinitPause () {
            if (this.infinitePause) {
                this.pauseConfigToEdit.timeToEndPause = 0;
                this.disableTime = true;
            } else {
                this.disableTime = false;
                this.pauseConfigToEdit.timeToEndPause = parseInt(
                    this.pauseConfig.time_to_end_pause
                );
            }

            const value = this.pauseConfigToEdit.timeToEndPause;
            this.limitNotifications(value);

            this.btnEditStatus = (this.pauseConfig.time_to_end_pause === this.pauseConfigToEdit.timeToEndPause);
        }
    },
    watch: {
        pauseConfig: {
            handler () {
                this.initializeModalData();
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
