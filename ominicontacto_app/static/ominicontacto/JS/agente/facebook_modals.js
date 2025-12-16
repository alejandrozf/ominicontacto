const modalTransferChatFacebook = $('#facebook-modal-transfer-chat');
const modalTemplatesFacebook = $('#facebook-modal-templates');
const modalDispositionFormFacebook = $('#facebook-modal-disposition-form');
const modalMediaImageFormFacebook = $('#facebook-modal-media-image-form');
const modalMediaFileFormFacebook = $('#facebook-modal-media-file-form');
const modalContactFormFacebook = $('#facebook-modal-contact-form');
const modalConversationNewFacebook = $('#facebook-modal-conversation-new');
const whatsappWrapperFacebook = $('#wrapperFacebook');

const onFacebookTransferChatEvent = ($event) => {
    const { transfer_chat } = $event.detail;
    modalTransferChatFacebook.modal(transfer_chat === true ? 'show' : 'hide');
};

const onFacebookTemplatesEvent = ($event) => {
    const { templates, conversationId } = $event.detail;
    if (conversationId) {
        localStorage.setItem('agtFacebookConversationId', conversationId);
    }
    modalTemplatesFacebook.modal(templates === true ? 'show' : 'hide');
};

const onFacebookDispositionFormEvent = ($event) => {
    const { disposition_form } = $event.detail;
    modalDispositionFormFacebook.modal(disposition_form === true ? 'show' : 'hide');
};

const onFacebookMediaFormEvent = ($event) => {
    const { media_form, fileType } = $event.detail;
    if (media_form) {
        if (fileType === 'img') {
            modalMediaImageFormFacebook.modal('show');
        } else {
            modalMediaFileFormFacebook.modal('show');
        }
    } else {
        modalMediaFileFormFacebook.modal('hide');
        modalMediaImageFormFacebook.modal('hide');
    }
};

const onFacebookContactFormEvent = ($event) => {
    const { contact_form } = $event.detail;
    modalContactFormFacebook.modal(contact_form === true ? 'show' : 'hide');
};

const onFacebookConversationNewEvent = ($event) => {
    const { conversation_new } = $event.detail;
    modalConversationNewFacebook.modal(conversation_new === true ? 'show' : 'hide');
};

const onFacebookCloseContainerEvent = ($event) => {
    whatsappWrapperFacebook.addClass('hidden');
};

const setEventListenersFacebook = () => {
    window.document.addEventListener('onFacebookCloseContainerEvent', onFacebookCloseContainerEvent, false);
    window.document.addEventListener('onFacebookTransferChatEvent', onFacebookTransferChatEvent, false);
    window.document.addEventListener('onFacebookTemplatesEvent', onFacebookTemplatesEvent, false);
    window.document.addEventListener('onFacebookDispositionFormEvent', onFacebookDispositionFormEvent, false);
    window.document.addEventListener('onFacebookMediaFormEvent', onFacebookMediaFormEvent, false);
    window.document.addEventListener('onFacebookContactFormEvent', onFacebookContactFormEvent, false);
    window.document.addEventListener('onFacebookConversationNewEvent', onFacebookConversationNewEvent, false);
    $('#facebookChat').on('click', function () {
        $('#wrapperFacebook').toggleClass('hidden');
        $('#wrapperWebphone').removeClass('active');
        $('#newChat').addClass('invisible');
    });
};

const setFacebookStatusIcon = (tiene_facebook = false) => {
    $('#facebookChat').css({ color: tiene_facebook ? '#52C159' : '#6A716A' });
};

$(function () {
    setEventListenersFacebook();
});