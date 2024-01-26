export default {
    agtWhatsContactListInit (state, contacts) {
        state.agtWhatsContactList = contacts;
    },
    agtWhatsContactDBFieldsInit (state, fields) {
        state.agtWhatsContactDBFields = fields;
    },
    agtWhatsContactSearchInit (state, contacts) {
        state.agtWhatsContactSearchResults = [];
        const contactsToAdd = [];
        for (const contact of contacts) {
            if (contact.id && !contactsToAdd.find(c => c.id === contact.id)) {
                contactsToAdd.push(contact);
            }
        }
        state.agtWhatsContactSearchResults = contactsToAdd;
    }
};
