<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '50vw' }"
    :closable="false"
    :modal="false"
  >
    <template #header>
      <h3>{{ modalTitle }}</h3>
    </template>
    <div class="card">
      <div class="grid formgrid mt-4">
        <div class="field col-4">
          <div class="field-radiobutton">
            <RadioButton
              id="internal"
              :value="INTERNAL_AUDIO"
              v-model="audioType"
              @click="internalFile"
            />
            <label for="internal">{{ $t('views.ivr.audios.types.internal') }}</label>
          </div>
          <div class="field-radiobutton">
            <RadioButton
              id="external"
              :value="EXTERNAL_AUDIO"
              v-model="audioType"
              @click="externalFile"
            />
            <label for="external">{{ $t('views.ivr.audios.types.external') }}</label>
          </div>
        </div>
        <div class="field col-8">
          <label
            id="internal_audio"
            :class="[
              audioType === EXTERNAL_AUDIO ? 'text-gray-500' : '',
              emptyInternalAudio ? 'p-error' : '',
            ]"
            >{{ internalAudioTitle }}</label
          >
          <Dropdown
            id="internal_audio"
            v-model="internalAudio"
            class="w-full mt-2"
            :class="[emptyInternalAudio ? 'p-invalid' : '']"
            :options="ivrAudios"
            @change="internalAudioChange"
            placeholder="-----"
            optionLabel="descripcion"
            optionValue="id"
            :disabled="inputInternalAudioDisabled"
            :emptyFilterMessage="$t('globals.without_data')"
          />
          <small v-if="emptyInternalAudio" class="p-error"
            >{{ $t('forms.ivr.audios.validations.required_internal_file') }}</small
          >
        </div>
      </div>
      <div class="grid formgrid mt-4">
        <div class="field col-12">
          <label
            id="external_audio"
            :class="[
              audioType === INTERNAL_AUDIO ? 'text-gray-500' : '',
              emptyExternalAudio ? 'p-error' : '',
            ]"
            class="mb-2"
            >{{ externalAudioTitle }}</label
          >
          <FileUpload
            id="external_audio"
            :class="[emptyExternalAudio ? 'p-invalid' : '']"
            :fileLimit="fileLimit"
            :accept="fileType"
            @select="externalAudioSelected"
            @remove="removeExternalAudio"
            :disabled="inputExternalAudioDisabled"
            :showUploadButton="false"
            :showCancelButton="false"
            :maxFileSize="1000000"
          >
            <template #empty>
              <div v-if="externalAudio">
                <div class="p-fileupload-files">
                  <div class="p-fileupload-row">
                    <div></div>
                    <div class="p-fileupload-filename">
                      {{ externalAudio.name }}
                    </div>
                    <div>{{ externalAudio.size / 1000 }} KB</div>
                    <div>
                      <button
                        class="p-button p-component p-button-icon-only"
                        type="button"
                        @click="removeExternalAudio"
                      >
                        <span class="pi pi-times p-button-icon"></span
                        ><span class="p-button-label">&nbsp;</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else>
                <p>{{ $t('forms.ivr.audios.external.drag_and_drop') }}</p>
              </div>
            </template>
          </FileUpload>
          <small v-if="emptyExternalAudio" class="p-error"
            >{{ $t('forms.ivr.audios.validations.required_external_file') }}</small
          >
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
        <Button
          :label="$t('globals.save')"
          class="p-button-info"
          @click="save"
        />
      </div>
    </template>
  </Dialog>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { INTERNAL_AUDIO, MAIN_AUDIO } from '@/globals/ivr';
export default {
    props: {
        modalTitle: {
            type: String,
            default: ''
        },
        internalAudioTitle: {
            type: String,
            default: ''
        },
        externalAudioTitle: {
            type: String,
            default: ''
        },
        showModal: {
            type: Boolean,
            default: false
        },
        formToCreate: {
            type: Boolean,
            default: true
        },
        audioInfo: {
            type: Object,
            default: null
        },
        optionAudio: {
            type: Number,
            default: MAIN_AUDIO
        }
    },
    created () {
        this.audioType = INTERNAL_AUDIO;
    },
    computed: {
        ...mapState(['ivrAudios', 'INTERNAL_AUDIO', 'EXTERNAL_AUDIO'])
    },
    data () {
        return {
            submitted: false,
            audioType: INTERNAL_AUDIO,
            requiredFields: {
                externalAudio: false,
                internalAudio: true
            },
            emptyExternalAudio: false,
            emptyInternalAudio: false,
            inputInternalAudioDisabled: false,
            inputExternalAudioDisabled: true,
            fileType: '.wav',
            fileLimit: 1,
            internalAudio: null,
            externalAudio: null
        };
    },
    methods: {
        ...mapActions(['setAudio']),
        internalFile () {
            this.inputInternalAudioDisabled = false;
            this.inputExternalAudioDisabled = true;
            this.requiredFields.externalAudio = false;
            this.requiredFields.internalAudio = true;
            this.emptyExternalAudio = false;
            this.emptyInternalAudio = false;
            this.externalAudio = null;
        },
        externalFile () {
            this.inputInternalAudioDisabled = true;
            this.inputExternalAudioDisabled = false;
            this.requiredFields.externalAudio = true;
            this.requiredFields.internalAudio = false;
            this.emptyExternalAudio = false;
            this.emptyInternalAudio = false;
            this.internalAudio = null;
        },
        externalAudioSelected (event) {
            this.emptyExternalAudio = false;
            this.emptyInternalAudio = false;
            this.externalAudio = event.files[0];
            this.internalAudio = this.externalAudio.name;
        },
        removeExternalAudio () {
            this.emptyExternalAudio = false;
            this.emptyInternalAudio = false;
            this.externalAudio = null;
            this.internalAudio = null;
        },
        internalAudioChange () {
            this.emptyInternalAudio = false;
            this.emptyExternalAudio = false;
            this.externalAudio = null;
        },
        initializeData () {
            this.submitted = false;
            this.audioType = INTERNAL_AUDIO;
            this.requiredFields = {
                externalAudio: false,
                internalAudio: true
            };
            this.emptyExternalAudio = false;
            this.emptyInternalAudio = false;
            this.inputInternalAudioDisabled = false;
            this.inputExternalAudioDisabled = true;
            this.internalAudio = null;
            this.externalAudio = null;
        },
        closeModal () {
            this.$emit('handleAudioModalEvent', { option: this.optionAudio });
            this.initializeData();
        },
        save () {
            // Validamos audio interno invalido
            this.emptyInternalAudio =
        this.requiredFields.internalAudio && this.internalAudio === null;
            if (this.emptyInternalAudio) {
                return null;
            }
            // Validamos audio externo invalido
            this.emptyExternalAudio =
        this.requiredFields.externalAudio && this.externalAudio === null;
            if (this.emptyExternalAudio) {
                return null;
            }
            this.setAudio({
                data: {
                    internalAudio: this.internalAudio,
                    externalAudio: this.externalAudio,
                    audioType: this.audioType
                },
                option: this.optionAudio
            });
            this.closeModal();
        }
    },
    watch: {
        audioInfo: {
            handler () {
                if (this.audioInfo) {
                    this.internalAudio = this.audioInfo.internalAudio;
                    this.externalAudio = this.audioInfo.externalAudio;
                    this.audioType = this.audioInfo.audioType;
                    if (this.audioType === INTERNAL_AUDIO) {
                        this.inputExternalAudioDisabled = true;
                        this.inputInternalAudioDisabled = false;
                        this.requiredFields = {
                            externalAudio: false,
                            internalAudio: true
                        };
                    } else {
                        this.inputExternalAudioDisabled = false;
                        this.inputInternalAudioDisabled = true;
                        this.requiredFields = {
                            externalAudio: true,
                            internalAudio: false
                        };
                    }
                    this.submitted = false;
                    this.emptyExternalAudio = false;
                    this.emptyInternalAudio = false;
                }
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
