const BASE_WHATSAPP_URL = '/api/v1/whatsapp';

export default {
    Templates: (campaignId, lineId = null) => {
        if (lineId !== null) {
            return `${BASE_WHATSAPP_URL}/templates/${campaignId}?line_id=${lineId}`;
        }
        return `${BASE_WHATSAPP_URL}/templates/${campaignId}`;
    }
};
