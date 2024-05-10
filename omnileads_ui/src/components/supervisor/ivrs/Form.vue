<template>
  <div class="card">
    <div class="grid formgrid mt-4">
      <div class="field col-6">
        <label
          id="ivr_name"
          :class="{
            'p-error':
              (v$.ivrForm.name.$invalid && submitted) || repeatedIVRName,
          }"
          >{{ $t("models.ivr.name") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-bars"></i>
          </span>
          <InputText
            id="ivr_name"
            :class="{
              'p-invalid':
                (v$.ivrForm.name.$invalid && submitted) || repeatedIVRName,
            }"
            @input="inputIVRNameEvent"
            :placeholder="$t('forms.ivr.enter_name')"
            v-model="v$.ivrForm.name.$model"
          />
        </div>
        <small
          v-if="
            (v$.ivrForm.name.$invalid && submitted) ||
            v$.ivrForm.name.$pending.$response
          "
          class="p-error"
          >{{
            v$.ivrForm.name.required.$message.replace(
              "Value",
              $t("models.ivr.name")
            )
          }}</small
        >
        <small v-if="repeatedIVRName" class="p-error">{{
          $t("forms.ivr.validations.repeated_ivr_name")
        }}</small>
      </div>
      <div class="field col-6">
        <label
          id="ivr_description"
          :class="{
            'p-error': v$.ivrForm.description.$invalid && submitted,
          }"
          >{{ $t("models.ivr.description") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <Textarea
            id="ivr_description"
            :class="{
              'p-invalid': v$.ivrForm.description.$invalid && submitted,
            }"
            rows="5"
            cols="30"
            :placeholder="$t('forms.ivr.enter_description')"
            v-model="v$.ivrForm.description.$model"
          />
        </div>
        <small
          v-if="
            (v$.ivrForm.description.$invalid && submitted) ||
            v$.ivrForm.description.$pending.$response
          "
          class="p-error"
          >{{
            v$.ivrForm.description.required.$message.replace(
              "Value",
              $t("models.ivr.description")
            )
          }}</small
        >
      </div>
      <div class="field col-6">
        <label
          id="ivr_main_audio"
          :class="{
            'p-error': v$.ivrForm.main_audio.$invalid && submitted,
          }"
          >{{ $t("models.ivr.main_audio") }}*</label
        >
        <div class="flex justify-content-between flex-wrap">
          <div class="flex align-items-center justify-content-center">
            <span class="p-inputgroup-addon mr-2">
              <i class="pi pi-volume-up"></i>
            </span>
            {{
              getAudioInfo(ivrForm.type_main_audio, ivrForm.main_audio, ivrForm.main_audio_ext)
            }}
          </div>
          <div class="flex align-items-center justify-content-center">
            <Button
              v-if="ivrForm.main_audio || ivrForm.main_audio_ext"
              icon="pi pi-pencil"
              class="p-button-rounded p-button-warning"
              @click="
                handleAudioModal({
                  showModal: true,
                  formToCreate: true,
                  internalAudio: ivrForm.main_audio,
                  externalAudio: ivrForm.main_audio_ext,
                  audioType: ivrForm.type_main_audio,
                  option: 1,
                })
              "
              v-tooltip.top="$t('globals.edit')"
            />
            <Button
              v-else
              icon="pi pi-plus"
              class="p-button-rounded p-button-info"
              @click="
                handleAudioModal({
                  showModal: true,
                  formToCreate: true,
                  internalAudio: ivrForm.main_audio,
                  externalAudio: ivrForm.main_audio_ext,
                  audioType: ivrForm.type_main_audio,
                  option: 1,
                })
              "
              v-tooltip.top="$tc('globals.new', 1)"
            />
          </div>
        </div>
        <small
          v-if="
            (v$.ivrForm.main_audio.$invalid && submitted) ||
            v$.ivrForm.main_audio.$pending.$response
          "
          class="p-error"
          >{{
            v$.ivrForm.main_audio.required.$message.replace(
              "Value",
              $t("models.ivr.main_audio")
            )
          }}</small
        >
      </div>
    </div>
    <div class="grid formgrid mt-4">
      <div class="field col-6">
        <Fieldset :legend="$t('views.ivr.configuration_time_out')">
          <div>
            <div class="grid formgrid">
              <div class="field col-6">
                <label
                  id="ivr_time_out"
                  :class="{
                    'p-error': v$.ivrForm.time_out.$invalid && submitted,
                  }"
                  >{{
                    $t("models.ivr.time_out_configuration.time_out")
                  }}*</label
                >
                <div class="p-inputgroup mt-2">
                  <span class="p-inputgroup-addon">
                    <i class="pi pi-clock"></i>
                  </span>
                  <InputNumber
                    id="ivr_time_out"
                    :class="{
                      'p-invalid': v$.ivrForm.time_out.$invalid && submitted,
                    }"
                    v-model="v$.ivrForm.time_out.$model"
                    mode="decimal"
                    showButtons
                    :min="0"
                    :max="1000"
                  />
                </div>
                <small
                  v-if="
                    (v$.ivrForm.time_out.$invalid && submitted) ||
                    v$.ivrForm.time_out.$pending.$response
                  "
                  class="p-error"
                  >{{
                    v$.ivrForm.time_out.required.$message.replace(
                      "Value",
                      $t("models.ivr.time_out_configuration.time_out")
                    )
                  }}</small
                >
              </div>
              <div class="field col-6">
                <label
                  id="ivr_time_out_retries"
                  :class="{
                    'p-error':
                      v$.ivrForm.time_out_retries.$invalid && submitted,
                  }"
                  >{{ $t("models.ivr.time_out_configuration.retries") }}*</label
                >
                <div class="p-inputgroup mt-2">
                  <span class="p-inputgroup-addon">
                    <i class="pi pi-replay"></i>
                  </span>
                  <InputNumber
                    id="ivr_time_out_retries"
                    :class="{
                      'p-invalid':
                        v$.ivrForm.time_out_retries.$invalid && submitted,
                    }"
                    v-model="v$.ivrForm.time_out_retries.$model"
                    mode="decimal"
                    showButtons
                    :min="0"
                    :max="1000"
                  />
                </div>
                <small
                  v-if="
                    (v$.ivrForm.time_out_retries.$invalid && submitted) ||
                    v$.ivrForm.time_out_retries.$pending.$response
                  "
                  class="p-error"
                  >{{
                    v$.ivrForm.time_out_retries.required.$message.replace(
                      "Value",
                      $t("models.ivr.time_out_configuration.retries")
                    )
                  }}</small
                >
              </div>
            </div>
            <hr>
            <div class="grid formgrid mt-4">
              <div class="field col-12">
                <label
                  id="ivr_time_out_audio"
                  :class="{
                    'p-error': v$.ivrForm.time_out_audio.$invalid && submitted,
                  }"
                  >{{ $t("models.ivr.time_out_configuration.audio") }}*</label
                >
                <div class="flex justify-content-between flex-wrap">
                  <div class="flex align-items-center justify-content-center">
                    <span class="p-inputgroup-addon mr-2">
                      <i class="pi pi-volume-up"></i>
                    </span>
                    {{
                      getAudioInfo(ivrForm.type_time_out_audio, ivrForm.time_out_audio, ivrForm.time_out_audio_ext)
                    }}
                  </div>
                  <div class="flex align-items-center justify-content-center">
                    <Button
                      v-if="ivrForm.time_out_audio || ivrForm.time_out_audio_ext"
                      icon="pi pi-pencil"
                      class="p-button-rounded p-button-warning"
                      @click="
                        handleAudioModal({
                          showModal: true,
                          formToCreate: true,
                          internalAudio: ivrForm.time_out_audio,
                          externalAudio: ivrForm.time_out_audio_ext,
                          audioType: ivrForm.type_time_out_audio,
                          option: 2,
                        })
                      "
                      v-tooltip.top="$t('globals.edit')"
                    />
                    <Button
                      v-else
                      icon="pi pi-plus"
                      class="p-button-rounded p-button-info"
                      @click="
                        handleAudioModal({
                          showModal: true,
                          formToCreate: true,
                          internalAudio: ivrForm.time_out_audio,
                          externalAudio: ivrForm.time_out_audio_ext,
                          audioType: ivrForm.type_time_out_audio,
                          option: 2,
                        })
                      "
                      v-tooltip.top="$tc('globals.new', 1)"
                    />
                  </div>
                </div>
                <small
                  v-if="
                    (v$.ivrForm.time_out_audio.$invalid && submitted) ||
                    v$.ivrForm.time_out_audio.$pending.$response
                  "
                  class="p-error"
                  >{{
                    v$.ivrForm.time_out_audio.required.$message.replace(
                      "Value",
                      $t("models.ivr.time_out_configuration.audio")
                    )
                  }}</small
                >
              </div>
            </div>
            <hr>
            <div class="grid formgrid mt-4">
              <div class="field col-12">
                <label
                  id="ivr_time_out_destination"
                  :class="{
                    'p-error':
                      v$.ivrForm.time_out_destination.$invalid && submitted,
                  }"
                  >{{
                    $t("models.ivr.time_out_configuration.destination")
                  }}*</label
                >
                <div class="flex justify-content-between flex-wrap">
                  <div class="flex align-items-center justify-content-center">
                    {{
                      getDestinationInfo(ivrForm.time_out_destination_type, ivrForm.time_out_destination)
                    }}
                  </div>
                  <div class="flex align-items-center justify-content-center">
                    <Button
                      v-if="ivrForm.time_out_destination"
                      icon="pi pi-pencil"
                      class="p-button-rounded p-button-warning"
                      @click="
                        handleDestinationModal({
                          showModal: true,
                          formToCreate: false,
                          destination: ivrForm.time_out_destination,
                          destinationType: ivrForm.time_out_destination_type,
                          option: 1,
                        })
                      "
                      v-tooltip.top="$t('globals.edit')"
                    />
                    <Button
                      v-else
                      icon="pi pi-plus"
                      class="p-button-rounded p-button-info"
                      @click="
                        handleDestinationModal({
                          showModal: true,
                          formToCreate: false,
                          destination: ivrForm.time_out_destination,
                          destinationType: ivrForm.time_out_destination_type,
                          option: 1,
                        })
                      "
                      v-tooltip.top="$tc('globals.new', 1)"
                    />
                  </div>
                </div>
                <small
                  v-if="
                    (v$.ivrForm.time_out_destination.$invalid && submitted) ||
                    v$.ivrForm.time_out_destination.$pending.$response
                  "
                  class="p-error"
                  >{{
                    v$.ivrForm.time_out_destination.required.$message.replace(
                      "Value",
                      $t("models.ivr.time_out_configuration.destination")
                    )
                  }}</small
                >
              </div>
            </div>
          </div>
        </Fieldset>
      </div>
      <div class="field col-6">
        <Fieldset :legend="$t('views.ivr.configuration_invalid_destination')">
          <div>
            <div class="grid formgrid">
              <div class="field col-6">
                <label
                  id="ivr_invalid_retries"
                  :class="{
                    'p-error': v$.ivrForm.invalid_retries.$invalid && submitted,
                  }"
                  >{{
                    $t("models.ivr.invalid_destination_configuration.retries")
                  }}*</label
                >
                <div class="p-inputgroup mt-2">
                  <span class="p-inputgroup-addon">
                    <i class="pi pi-replay"></i>
                  </span>
                  <InputNumber
                    id="ivr_invalid_retries"
                    :class="{
                      'p-invalid':
                        v$.ivrForm.invalid_retries.$invalid && submitted,
                    }"
                    v-model="v$.ivrForm.invalid_retries.$model"
                    mode="decimal"
                    showButtons
                    :min="0"
                    :max="1000"
                  />
                </div>
                <small
                  v-if="
                    (v$.ivrForm.invalid_retries.$invalid && submitted) ||
                    v$.ivrForm.invalid_retries.$pending.$response
                  "
                  class="p-error"
                  >{{
                    v$.ivrForm.invalid_retries.required.$message.replace(
                      "Value",
                      $t("models.ivr.invalid_destination_configuration.retries")
                    )
                  }}</small
                >
              </div>
            </div>
            <hr>
            <div class="grid formgrid mt-4">
              <div class="field col-12">
                <label
                  id="ivr_invalid_audio"
                  :class="{
                    'p-error': v$.ivrForm.invalid_audio.$invalid && submitted,
                  }"
                  >{{
                    $t("models.ivr.invalid_destination_configuration.audio")
                  }}*</label
                >
                <div class="flex justify-content-between flex-wrap">
                  <div class="flex align-items-center justify-content-center">
                    <span class="p-inputgroup-addon mr-2">
                      <i class="pi pi-volume-up"></i>
                    </span>
                    {{
                      getAudioInfo(ivrForm.type_invalid_audio, ivrForm.invalid_audio, ivrForm.invalid_audio_ext)
                    }}
                  </div>
                  <div class="flex align-items-center justify-content-center">
                    <Button
                      v-if="ivrForm.invalid_audio || ivrForm.invalid_audio_ext"
                      icon="pi pi-pencil"
                      class="p-button-rounded p-button-warning"
                      @click="
                        handleAudioModal({
                          showModal: true,
                          formToCreate: true,
                          internalAudio: ivrForm.invalid_audio,
                          externalAudio: ivrForm.invalid_audio_ext,
                          audioType: ivrForm.type_invalid_audio,
                          option: 3,
                        })
                      "
                      v-tooltip.top="$t('globals.edit')"
                    />
                    <Button
                      v-else
                      icon="pi pi-plus"
                      class="p-button-rounded p-button-info"
                      @click="
                        handleAudioModal({
                          showModal: true,
                          formToCreate: true,
                          internalAudio: ivrForm.invalid_audio,
                          externalAudio: ivrForm.invalid_audio_ext,
                          audioType: ivrForm.type_invalid_audio,
                          option: 3,
                        })
                      "
                      v-tooltip.top="$tc('globals.new', 1)"
                    />
                  </div>
                </div>
                <small
                  v-if="
                    (v$.ivrForm.invalid_audio.$invalid && submitted) ||
                    v$.ivrForm.invalid_audio.$pending.$response
                  "
                  class="p-error"
                  >{{
                    v$.ivrForm.invalid_audio.required.$message.replace(
                      "Value",
                      $t("models.ivr.invalid_destination_configuration.audio")
                    )
                  }}</small
                >
              </div>
            </div>
            <hr>
            <div class="grid formgrid mt-4">
              <div class="field col-12">
                <label
                  id="ivr_invalid_destination"
                  :class="{
                    'p-error':
                      v$.ivrForm.invalid_destination.$invalid && submitted,
                  }"
                  >{{
                    $t(
                      "models.ivr.invalid_destination_configuration.destination"
                    )
                  }}*</label
                >
                <div class="flex justify-content-between flex-wrap">
                  <div class="flex align-items-center justify-content-center">
                    {{
                      getDestinationInfo(ivrForm.invalid_destination_type, ivrForm.invalid_destination)
                    }}
                  </div>
                  <div class="flex align-items-center justify-content-center">
                    <Button
                      v-if="ivrForm.invalid_destination"
                      icon="pi pi-pencil"
                      class="p-button-rounded p-button-warning"
                      @click="
                        handleDestinationModal({
                          showModal: true,
                          formToCreate: false,
                          destination: ivrForm.invalid_destination,
                          destinationType: ivrForm.invalid_destination_type,
                          option: 2,
                        })
                      "
                      v-tooltip.top="$t('globals.edit')"
                    />
                    <Button
                      v-else
                      icon="pi pi-plus"
                      class="p-button-rounded p-button-info"
                      @click="
                        handleDestinationModal({
                          showModal: true,
                          formToCreate: false,
                          destination: ivrForm.invalid_destination,
                          destinationType: ivrForm.invalid_destination_type,
                          option: 2,
                        })
                      "
                      v-tooltip.top="$tc('globals.new', 1)"
                    />
                  </div>
                </div>
                <small
                  v-if="
                    (v$.ivrForm.invalid_destination.$invalid && submitted) ||
                    v$.ivrForm.invalid_destination.$pending.$response
                  "
                  class="p-error"
                  >{{
                    v$.ivrForm.invalid_destination.required.$message.replace(
                      "Value",
                      $t(
                        "models.ivr.invalid_destination_configuration.destination"
                      )
                    )
                  }}</small
                >
              </div>
            </div>
          </div>
        </Fieldset>
      </div>
    </div>
    <div class="mt-4">
      <h3>{{ $t("models.ivr.destination_options") }}</h3>
      <DestinationOptionsTable
        :destinationOptions="ivrForm.destination_options"
        @handleDestinationOptionModalEvent="handleDestinationOptionModal"
      />
    </div>
    <!-- Main audio -->
    <AudioFile
      :modalTitle="$t('views.ivr.audios.main.title')"
      :internalAudioTitle="$t('views.ivr.audios.main.internal')"
      :externalAudioTitle="$t('views.ivr.audios.main.external')"
      :audioInfo="mainAudioInfo"
      :optionAudio="optionAudio"
      :showModal="showMainAudioModal"
      :formToCreate="formToCreateMainAudio"
      @handleAudioModalEvent="handleAudioModal"
    />
    <!-- Time out audio -->
    <AudioFile
      :modalTitle="$t('views.ivr.audios.time_out.title')"
      :internalAudioTitle="$t('views.ivr.audios.time_out.internal')"
      :externalAudioTitle="$t('views.ivr.audios.time_out.external')"
      :audioInfo="timeOutAudioInfo"
      :optionAudio="optionAudio"
      :showModal="showTimeOutAudioModal"
      :formToCreate="formToCreateTimeOutAudio"
      @handleAudioModalEvent="handleAudioModal"
    />
    <!-- Invalid audio -->
    <AudioFile
      :modalTitle="$t('views.ivr.audios.invalid.title')"
      :internalAudioTitle="$t('views.ivr.audios.invalid.internal')"
      :externalAudioTitle="$t('views.ivr.audios.invalid.external')"
      :audioInfo="invalidAudioInfo"
      :optionAudio="optionAudio"
      :showModal="showInvalidAudioModal"
      :formToCreate="formToCreateInvalidAudio"
      @handleAudioModalEvent="handleAudioModal"
    />
    <!-- Time out destination -->
    <Destination
      :modalTitle="$t('views.ivr.destinations.time_out')"
      :form="{
        destination_type: timeOutDestinationType,
        destination: timeOutDestination,
      }"
      :optionDestination="optionDestination"
      :showModal="showTimeOutDestinationModal"
      :formToCreate="formToCreateTimeOutDestination"
      @handleDestinationModalEvent="handleDestinationModal"
    />
    <!-- Invalid destination -->
    <Destination
      :modalTitle="$t('views.ivr.destinations.invalid')"
      :form="{
        destination_type: invalidDestinationType,
        destination: invalidDestination,
      }"
      :optionDestination="optionDestination"
      :showModal="showInvalidDestinationModal"
      :formToCreate="formToCreateInvalidDestination"
      @handleDestinationModalEvent="handleDestinationModal"
    />
    <DestinationOptionModal
      :destinationOptions="ivrForm.destination_options"
      :destinationOption="destinationOption"
      :showModal="showDestinationOptionModal"
      :formToCreate="formToCreateDestinationOption"
      @handleDestinationOptionModalEvent="handleDestinationOptionModal"
    />
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
  </div>
</template>

<script>
import { useVuelidate } from '@vuelidate/core';
import { required } from '@vuelidate/validators';
import { mapActions, mapState } from 'vuex';
import DestinationOptionsTable from '@/components/supervisor/ivrs/DestinationOptionsTable';
import DestinationOptionModal from '@/components/supervisor/ivrs/DestinationOptionModal';
import AudioFile from '@/components/supervisor/ivrs/form/AudioFile';
import Destination from '@/components/supervisor/ivrs/form/Destination';
import {
    MAIN_AUDIO,
    TIME_OUT_AUDIO,
    INVALID_AUDIO,
    TIME_OUT_DEST,
    INVALID_DEST,
    CAMPAIGN,
    VALIDATION_DATE,
    IVR,
    HANGUP,
    ID_CLIENT,
    CUSTOM_DST,
    INTERNAL_AUDIO,
    EXTERNAL_AUDIO
} from '@/globals/supervisor/ivr';
import { HTTP_STATUS } from '@/globals';

export default {
    setup: () => ({ v$: useVuelidate({ $scope: false }) }),
    validations () {
        return {
            ivrForm: {
                name: { required },
                description: { required },
                time_out: { required },
                time_out_retries: { required },
                invalid_retries: { required },
                // Audios Internos
                main_audio: { required },
                time_out_audio: { required },
                invalid_audio: { required },
                // Destinos Fijos
                time_out_destination: { required },
                invalid_destination: { required }
            }
        };
    },
    components: {
        AudioFile,
        Destination,
        DestinationOptionModal,
        DestinationOptionsTable
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
            repeatedIVRName: false,
            optionAudio: MAIN_AUDIO,
            optionDestination: TIME_OUT_DEST,
            // Main audio
            showMainAudioModal: false,
            formToCreateMainAudio: false,
            mainAudioInfo: null,
            // Time out audio
            showTimeOutAudioModal: false,
            formToCreateTimeOutAudio: false,
            timeOutAudioInfo: null,
            // Invalid Audio
            showInvalidAudioModal: false,
            formToCreateInvalidAudio: false,
            invalidAudioInfo: null,
            // Destino de time out
            showTimeOutDestinationModal: false,
            formToCreateTimeOutDestination: false,
            timeOutDestination: null,
            timeOutDestinationType: null,
            // Destino invalido
            showInvalidDestinationModal: false,
            formToCreateInvalidDestination: false,
            invalidDestination: null,
            invalidDestinationType: null,
            // Destination Options
            showDestinationOptionModal: false,
            formToCreateDestinationOption: false,
            destinationOption: null,
            destination_types: [
                {
                    option: this.$t('forms.ivr.destination_types.campaign'),
                    value: CAMPAIGN
                },
                {
                    option: this.$t('forms.ivr.destination_types.validation_date'),
                    value: VALIDATION_DATE
                },
                {
                    option: this.$t('forms.ivr.destination_types.ivr'),
                    value: IVR
                },
                {
                    option: this.$t('forms.ivr.destination_types.hangup'),
                    value: HANGUP
                },
                {
                    option: this.$t('forms.ivr.destination_types.id_client'),
                    value: ID_CLIENT
                },
                {
                    option: this.$t('forms.ivr.destination_types.custom_dst'),
                    value: CUSTOM_DST
                }
            ]
        };
    },
    computed: {
        ...mapState(['ivrs', 'ivrForm', 'ivrAudios', 'ivrDestinations'])
    },
    async created () {
        await this.initIVRDestinations();
        await this.initIVRAudios();
        await this.initIVRs();
        this.initializeData();
    },
    methods: {
        ...mapActions([
            'createIVR',
            'updateIVR',
            'initIVRs',
            'initIVRAudios',
            'initIVRDestinations',
            'initDestinationOption'
        ]),
        initializeData () {
            this.submitted = false;
            this.showTimeValidationModal = false;
            this.emptyTimeValidations = false;
            this.repeatedIVRName = false;
            this.formToCreateTimeValidation = true;
            this.timeValidation = null;
        },
        checkEmptyTimeValidations () {
            this.emptyTimeValidations = this.ivr.validaciones_de_tiempo.length === 0;
        },
        inputIVRNameEvent () {
            this.repeatedIVRName = this.ivrs.find(
                (data) => data.name === this.ivrForm.name
            );
        },
        handleDestinationOptionModal ({
            showModal = false,
            formToCreate = false,
            destinationOption = null
        }) {
            this.initDestinationOption(destinationOption);
            this.showDestinationOptionModal = showModal;
            this.formToCreateDestinationOption = formToCreate;
            this.destinationOption = destinationOption;
        },
        getAudioInfo (type = null, internalAudio = null, externalAudio = null) {
            var typeInfo = '------';
            var audioInfo = '------';
            if (type === INTERNAL_AUDIO) {
                typeInfo = this.$t('views.ivr.audios.types.internal');
            } else if (type === EXTERNAL_AUDIO) {
                typeInfo = this.$t('views.ivr.audios.types.external');
            }
            if (this.ivrAudios.length > 0 || this.ivrAudios !== null) {
                if (type === INTERNAL_AUDIO && internalAudio) {
                    const audio = this.ivrAudios.find((a) => a.id === internalAudio);
                    audioInfo = audio ? audio.descripcion : audioInfo;
                } else if (type === EXTERNAL_AUDIO && externalAudio) {
                    audioInfo = externalAudio.name;
                }
            }
            return `${typeInfo}: ${audioInfo}`;
        },
        getDestinationInfo (type = null, destinationId = null) {
            var typeInfo = '------';
            var destInfo = '------';
            if (this.ivrDestinations.length > 0 || this.ivrDestinations !== null) {
                if (type && destinationId) {
                    const destinationType = this.destination_types.find(
                        (dt) => dt.value === type
                    );
                    typeInfo = destinationType ? destinationType.option : typeInfo;
                    const destination = this.ivrDestinations[`${type}`].find(
                        (d) => d.id === destinationId
                    );
                    destInfo = destination ? destination.nombre : destInfo;
                }
            }
            return `${typeInfo}: ${destInfo}`;
        },
        // Audios
        handleAudioModal ({
            showModal = false,
            formToCreate = true,
            internalAudio = null,
            externalAudio = null,
            audioType = INTERNAL_AUDIO,
            option = MAIN_AUDIO
        }) {
            this.optionAudio = option;
            if (option === MAIN_AUDIO) {
                // Main audio
                this.showMainAudioModal = showModal;
                this.formToCreateMainAudio = formToCreate;
                this.mainAudioInfo = {
                    internalAudio,
                    externalAudio,
                    audioType
                };
            } else if (option === TIME_OUT_AUDIO) {
                // Time out audio
                this.showTimeOutAudioModal = showModal;
                this.formToCreateTimeOutAudio = formToCreate;
                this.timeOutAudioInfo = {
                    internalAudio,
                    externalAudio,
                    audioType
                };
            } else if (option === INVALID_AUDIO) {
                // Invalid audio
                this.showInvalidAudioModal = showModal;
                this.formToCreateInvalidAudio = formToCreate;
                this.invalidAudioInfo = {
                    internalAudio,
                    externalAudio,
                    audioType
                };
            }
        },
        // Destinos
        handleDestinationModal ({
            showModal = false,
            formToCreate = false,
            destination = null,
            destinationType = null,
            option = TIME_OUT_DEST
        }) {
            this.optionDestination = option;
            if (option === TIME_OUT_DEST) {
                // Time out destination
                this.showTimeOutDestinationModal = showModal;
                this.formToCreateTimeOutDestination = formToCreate;
                this.timeOutDestination = destination;
                this.timeOutDestinationType = destinationType;
            } else if (option === INVALID_DEST) {
                // Invalid destination
                this.showInvalidDestinationModal = showModal;
                this.formToCreateInvalidDestination = formToCreate;
                this.invalidDestination = destination;
                this.invalidDestinationType = destinationType;
            }
        },
        async save (isFormValid) {
            this.submitted = true;
            if (!isFormValid || this.repeatedIVRName) {
                return null;
            }
            this.$swal.fire({
                title: this.$t('globals.processing_request'),
                timerProgressBar: true,
                allowOutsideClick: false,
                didOpen: () => {
                    this.$swal.showLoading();
                }
            });
            var response = null;
            if (this.formToCreate) {
                response = await this.createIVR(this.ivrForm);
            } else {
                response = await this.updateIVR({
                    id: this.ivrForm.id,
                    data: this.ivrForm
                });
            }
            const { status, message } = response;
            this.$swal.close();
            if (status === HTTP_STATUS.SUCCESS) {
                await this.initIVRs();
                this.$router.push({ name: 'supervisor_ivrs' });
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
        ivrForm: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
