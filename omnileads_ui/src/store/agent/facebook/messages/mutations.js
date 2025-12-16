export default {
    agtFacebookSendMessageStatus (state, info = null) {
        if (info) {
            state.agtFacebookConversationMessages.forEach((message) => {
                if (message.id === info.message_id) {
                    message.status = info.status;
                    message.fail_reason = info.fail_reason;
                }
            });
        }
    }
};
