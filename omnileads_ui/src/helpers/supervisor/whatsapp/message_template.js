import {
    TEMPLATE_TYPES
} from '@/globals/supervisor/whatsapp/message_template';

export const getConfigurationByType = (type = TEMPLATE_TYPES.TEXT, config = null) => {
    if (type === TEMPLATE_TYPES.TEXT) {
        const TEXT_FIELDS = {
            type: 'text',
            text: ''
        };
        if (config) {
            TEXT_FIELDS.text = config.text;
        }
        return TEXT_FIELDS;
    } else if (type === TEMPLATE_TYPES.IMAGE) {
        const IMAGE_FIELDS = {
            type: 'image',
            originalUrl: '',
            previewUrl: '',
            caption: ''
        };
        if (config) {
            IMAGE_FIELDS.originalUrl = config.originalUrl;
            IMAGE_FIELDS.previewUrl = config.previewUrl;
            IMAGE_FIELDS.caption = config.caption;
        }
        return IMAGE_FIELDS;
    } else if (type === TEMPLATE_TYPES.AUDIO) {
        const AUDIO_FIELDS = {
            type: 'audio',
            url: ''
        };
        if (config) {
            AUDIO_FIELDS.url = config.url;
        }
        return AUDIO_FIELDS;
    } else if (type === TEMPLATE_TYPES.FILE) {
        const FILE_FIELDS = {
            type: 'file',
            url: '',
            filename: ''
        };
        if (config) {
            FILE_FIELDS.url = config.url;
            FILE_FIELDS.filename = config.filename;
        }
        return FILE_FIELDS;
    } else if (type === TEMPLATE_TYPES.STICKER) {
        const STICKER_FIELDS = {
            type: 'sticker',
            url: ''
        };
        if (config) {
            STICKER_FIELDS.url = config.url;
        }
        return STICKER_FIELDS;
    } else if (type === TEMPLATE_TYPES.VIDEO) {
        const VIDEO_FIELDS = {
            type: 'video',
            url: '',
            caption: ''
        };
        if (config) {
            VIDEO_FIELDS.url = config.url;
            VIDEO_FIELDS.caption = config.caption;
        }
        return VIDEO_FIELDS;
    }
};
