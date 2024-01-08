const modalTransferChat = $('#whatsapp-modal-transfer-chat');
const modalTemplates = $('#whatsapp-modal-templates');
const modalDispositionForm = $('#whatsapp-modal-disposition-form');
const modalMediaImageForm = $('#whatsapp-modal-media-image-form');
const modalMediaFileForm = $('#whatsapp-modal-media-file-form');
const modalContactForm = $('#whatsapp-modal-contact-form');
const modalConversationNew = $('#whatsapp-modal-conversation-new');
const whatsappWrapper = $('#wrapperWhatsapp');

const onWhatsappTransferChatEvent = ($event) => {
    const { transfer_chat } = $event.detail;
    modalTransferChat.modal(transfer_chat === true ? 'show' : 'hide');
};

const onWhatsappTemplatesEvent = ($event) => {
    const { templates, conversationId } = $event.detail;
    if (conversationId) {
        localStorage.setItem('agtWhatsappConversationId', conversationId);
    }
    modalTemplates.modal(templates === true ? 'show' : 'hide');
};

const onWhatsappDispositionFormEvent = ($event) => {
    const { disposition_form } = $event.detail;
    modalDispositionForm.modal(disposition_form === true ? 'show' : 'hide');
};

const onWhatsappMediaFormEvent = ($event) => {
    const { media_form, fileType } = $event.detail;
    if (media_form) {
        if (fileType === 'img') {
            modalMediaImageForm.modal('show');
        } else {
            modalMediaFileForm.modal('show');
        }
    } else {
        modalMediaFileForm.modal('hide');
        modalMediaImageForm.modal('hide');
    }
};

const onWhatsappContactFormEvent = ($event) => {
    const { contact_form } = $event.detail;
    modalContactForm.modal(contact_form === true ? 'show' : 'hide');
};

const onWhatsappConversationNewEvent = ($event) => {
    const { conversation_new } = $event.detail;
    modalConversationNew.modal(conversation_new === true ? 'show' : 'hide');
};

const onWhatsappCloseContainerEvent = ($event) => {
    whatsappWrapper.addClass('hidden');
};

const setEventListeners = () => {
    window.document.addEventListener('onWhatsappCloseContainerEvent', onWhatsappCloseContainerEvent, false);
    window.document.addEventListener('onWhatsappTransferChatEvent', onWhatsappTransferChatEvent, false);
    window.document.addEventListener('onWhatsappTemplatesEvent', onWhatsappTemplatesEvent, false);
    window.document.addEventListener('onWhatsappDispositionFormEvent', onWhatsappDispositionFormEvent, false);
    window.document.addEventListener('onWhatsappMediaFormEvent', onWhatsappMediaFormEvent, false);
    window.document.addEventListener('onWhatsappContactFormEvent', onWhatsappContactFormEvent, false);
    window.document.addEventListener('onWhatsappConversationNewEvent', onWhatsappConversationNewEvent, false);
    $('#whatsappChat').on('click', function () {
        $('#wrapperWhatsapp').toggleClass('hidden');
        $('#wrapperWebphone').removeClass('active');
        $('#newChat').addClass('invisible');
    });
};

const setWhatsappStatusIcon = (tiene_whatsapp = false) => {
    $('#whatsappChat').css({ color: tiene_whatsapp ? '#52C159' : '#6A716A' });
};

$(function () {
    setEventListeners();
});