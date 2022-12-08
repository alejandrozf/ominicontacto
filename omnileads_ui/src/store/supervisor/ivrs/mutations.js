import { INTERNAL_AUDIO } from '@/globals/supervisor/ivr';

export default {
    initIVRs (state, ivrs) {
        state.ivrs = ivrs;
    },
    initIVR (state, ivr = null) {
        if (ivr) {
            state.ivrForm = {
                id: ivr.id,
                name: ivr.name,
                description: ivr.description,
                // Time Out
                time_out: ivr.time_out,
                time_out_retries: ivr.time_out_retries,
                // Invalid destination
                invalid_retries: ivr.invalid_retries,
                // Audios Internos
                main_audio: ivr.audio_principal,
                time_out_audio: ivr.time_out_audio,
                invalid_audio: ivr.invalid_audio,
                // Tipos de audio
                type_main_audio: INTERNAL_AUDIO,
                type_time_out_audio: INTERNAL_AUDIO,
                type_invalid_audio: INTERNAL_AUDIO,
                // Audios externos
                main_audio_ext: null,
                time_out_audio_ext: null,
                invalid_audio_ext: null,
                // Destinos Fijos
                time_out_destination: ivr.time_out_destination,
                time_out_destination_type: ivr.time_out_destination_type,
                invalid_destination: ivr.invalid_destination,
                invalid_destination_type: ivr.invalid_destination_type,
                // Destinos
                destination_options: ivr.destination_options
            };
        } else {
            state.ivrForm = {
                id: null,
                name: '',
                description: '',
                // Time Out
                time_out: null,
                time_out_retries: null,
                // Invalid destination
                invalid_retries: null,
                // Audios Internos
                main_audio: null,
                time_out_audio: null,
                invalid_audio: null,
                // Tipos de audio
                type_main_audio: INTERNAL_AUDIO,
                type_time_out_audio: INTERNAL_AUDIO,
                type_invalid_audio: INTERNAL_AUDIO,
                // Audios externos
                main_audio_ext: null,
                time_out_audio_ext: null,
                invalid_audio_ext: null,
                // Destinos Fijos
                time_out_destination: null,
                time_out_destination_type: null,
                invalid_destination: null,
                invalid_destination_type: null,
                // Destinos
                destination_options: []
            };
        }
    },
    initIVRAudios (state, audios) {
        state.ivrAudios = audios;
    },
    initIVRDestinations (state, destinations) {
        state.ivrDestinations = destinations;
    },
    updateTimeOutDestination (state, { type, destination }) {
        state.ivrForm.time_out_destination_type = type;
        state.ivrForm.time_out_destination = destination;
    },
    updateInvalidDestination (state, { type, destination }) {
        state.ivrForm.invalid_destination_type = type;
        state.ivrForm.invalid_destination = destination;
    },
    setMainAudio (state, { internalAudio, externalAudio, audioType }) {
        state.ivrForm.main_audio = internalAudio;
        state.ivrForm.main_audio_ext = externalAudio;
        state.ivrForm.type_main_audio = audioType;
    },
    setTimeOutAudio (state, { internalAudio, externalAudio, audioType }) {
        state.ivrForm.time_out_audio = internalAudio;
        state.ivrForm.time_out_audio_ext = externalAudio;
        state.ivrForm.type_time_out_audio = audioType;
    },
    setInvalidAudio (state, { internalAudio, externalAudio, audioType }) {
        state.ivrForm.invalid_audio = internalAudio;
        state.ivrForm.invalid_audio_ext = externalAudio;
        state.ivrForm.type_invalid_audio = audioType;
    },
    initDestinationOption (state, destinationOption = null) {
        if (destinationOption) {
            state.destinationOption = {
                id: destinationOption.id,
                dtmf: destinationOption.dtmf,
                destination: destinationOption.destination,
                destination_type: destinationOption.destination_type
            };
        } else {
            state.destinationOption = {
                id: null,
                dtmf: null,
                destination: null,
                destination_type: null
            };
        }
    },
    addDestinationOption (state, destinationOption) {
        state.ivrForm.destination_options.push(destinationOption);
    },
    removeDestinationOption (state, destinationOption) {
        if (destinationOption.id) {
            state.ivrForm.destination_options = state.ivrForm.destination_options.filter(data => data.id !== destinationOption.id);
        } else {
            state.ivrForm.destination_options = state.ivrForm.destination_options.filter(
                data => !(destinationOption.dtmf === data.dtmf));
        }
    },
    editDestinationOption (state, destinationOption) {
        state.ivrForm.destination_options.find(function (data) {
            if (destinationOption.id) {
                if (data.id === state.destinationOption.id) {
                    data.dtmf = destinationOption.dtmf;
                    data.destination = destinationOption.destination;
                    data.destination_type = destinationOption.destination_type;
                }
            } else {
                if (data.dtmf === state.destinationOption.dtmf) {
                    data.dtmf = destinationOption.dtmf;
                    data.destination = destinationOption.destination;
                    data.destination_type = destinationOption.destination_type;
                }
            }
        });
    }
};
