/* eslint-disable camelcase */
import { EXTERNAL_AUDIO, DTMF_REGEX } from '@/globals/ivr';

export function isDTMFValid (dtmf) {
    return DTMF_REGEX.test(dtmf);
}

export function getNewFormData (data) {
    const {
        id,
        name,
        description,
        time_out,
        time_out_retries,
        invalid_retries,
        main_audio,
        time_out_audio,
        invalid_audio,
        type_main_audio,
        type_time_out_audio,
        type_invalid_audio,
        main_audio_ext,
        time_out_audio_ext,
        invalid_audio_ext,
        time_out_destination,
        time_out_destination_type,
        invalid_destination,
        invalid_destination_type,
        destination_options
    } = data;
    var newData = {
        id,
        nombre: name,
        descripcion: description,
        time_out,
        time_out_retries,
        invalid_retries,
        main_audio,
        time_out_audio,
        invalid_audio,
        type_main_audio,
        type_time_out_audio,
        type_invalid_audio,
        main_audio_ext,
        time_out_audio_ext,
        invalid_audio_ext,
        time_out_destination,
        time_out_destination_type,
        invalid_destination,
        invalid_destination_type,
        destination_options: destination_options.map(function (d) {
            return {
                id: d.id,
                dtmf: d.dtmf,
                destination_type: d.destination_type,
                destination: d.destination
            };
        })
    };
    if (newData.type_main_audio === EXTERNAL_AUDIO) {
        newData.main_audio = null;
    }
    if (newData.type_time_out_audio === EXTERNAL_AUDIO) {
        newData.time_out_audio = null;
    }
    if (newData.type_invalid_audio === EXTERNAL_AUDIO) {
        newData.invalid_audio = null;
    }
    return newData;
}
