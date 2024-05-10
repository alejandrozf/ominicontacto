export default {
    initSupWhatsReportGeneral (state, data = null) {
        state.supWhatsReportGeneral = {
            sent_messages: data ? data.sent_messages : 0,
            received_messages: data ? data.received_messages : 0,
            interactions_started: data ? data.interactions_started : 0,
            attended_chats: data ? data.attended_chats : 0,
            not_attended_chats: data ? data.not_attended_chats : 0,
            inbound_chats_attended: data ? data.inbound_chats_attended : 0,
            inbound_chats_not_attended: data
                ? data.inbound_chats_not_attended
                : 0,
            inbound_chats_expired: data ? data.inbound_chats_expired : 0,
            outbound_chats_attended: data ? data.outbound_chats_attended : 0,
            outbound_chats_not_attended: data
                ? data.outbound_chats_not_attended
                : 0,
            outbound_chats_expired: data ? data.outbound_chats_expired : 0,
            outbound_chats_failed: data ? data.outbound_chats_failed : 0
        };
    },
    initSupWhatsReportGeneralColors (state, colors = null) {
        state.supWhatsReportGeneralColors = {
            rgbColors: colors ? colors.rgbColors : [],
            rgbaColors: colors ? colors.rgbaColors : []
        };
    }
};
