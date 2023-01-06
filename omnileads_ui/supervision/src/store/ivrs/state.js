import { INTERNAL_AUDIO } from '@/globals/ivr';

export default {
    ivrs: [],
    ivrDestinations: [],
    ivrAudios: [],
    ivrForm: {
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
    },
    INTERNAL_AUDIO: 1,
    EXTERNAL_AUDIO: 2
};
