const BASE_FACEBOOK_URL = '/api/v1/facebook';

export default {
    Templates: (campaignId, pageId = null) => {
        if (pageId !== null) {
            return `${BASE_FACEBOOK_URL}/templates/${campaignId}?page_id=${pageId}`;
        }
        return `${BASE_FACEBOOK_URL}/templates/${campaignId}`;
    }
};
