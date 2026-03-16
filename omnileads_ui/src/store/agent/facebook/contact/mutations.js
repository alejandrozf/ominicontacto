export default {
    agtFacebookContactListInit (state, contacts) {
        state.agtFacebookContactList = contacts;
    },
    agtFacebookContactDBFieldsInit (state, fields) {
        state.agtFacebookContactDBFields = fields;
    },
    agtFacebookContactSearchInit (state, contacts) {
        state.agtFacebookContactSearchResults = [];
        const contactsToAdd = [];
        for (const contact of contacts) {
            if (contact.id && !contactsToAdd.find(c => c.id === contact.id)) {
                contactsToAdd.push(contact);
            }
        }
        state.agtFacebookContactSearchResults = contactsToAdd;
    },
    agtFacebookNewContact (state, contact){
        console.log('agtFacebookNewContact', contact)
        if (contact) {
            state.newContact = []
            state.newContact.push(contact);
        }
    },
};
