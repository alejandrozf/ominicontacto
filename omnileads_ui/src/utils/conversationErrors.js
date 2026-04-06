const META_ATTACHMENT_ERROR_CODE = 131053;

export const getConversationErrorCode = (errorEx) => {
    if (!errorEx || typeof errorEx !== 'object') {
        return null;
    }
    const code = Number(errorEx.code);
    return Number.isNaN(code) ? null : code;
};

export const isAttachmentDeliveryError = (errorEx) => {
    const code = getConversationErrorCode(errorEx);
    if (code === META_ATTACHMENT_ERROR_CODE) {
        return true;
    }
    const details = errorEx?.error_data?.details || '';
    const title = errorEx?.title || '';
    const message = errorEx?.message || '';
    const normalizedText = `${title} ${message} ${details}`.toLowerCase();
    return normalizedText.includes('media upload error') ||
        normalizedText.includes('downloading media from weblink failed');
};
