const modalTransferChat = $('#whatsapp-modal-transfer-chat');
const modalTemplates = $('#whatsapp-modal-templates');
const modalDispositionForm = $('#whatsapp-modal-managenment-form');
const modalMediaImageForm = $('#whatsapp-modal-media-image-form');
const modalMediaFileForm = $('#whatsapp-modal-media-file-form');
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

const onWhatsappCloseContainerEvent = ($event) => {
    whatsappWrapper.addClass('hidden');
};

const setEventListeners = () => {
    window.document.addEventListener('onWhatsappCloseContainerEvent', onWhatsappCloseContainerEvent, false);
    window.document.addEventListener('onWhatsappTransferChatEvent', onWhatsappTransferChatEvent, false);
    window.document.addEventListener('onWhatsappTemplatesEvent', onWhatsappTemplatesEvent, false);
    window.document.addEventListener('onWhatsappDispositionFormEvent', onWhatsappDispositionFormEvent, false);
    window.document.addEventListener('onWhatsappMediaFormEvent', onWhatsappMediaFormEvent, false);
    $('#whatsappChat').on('click', function () {
        $('#wrapperWhatsapp').toggleClass('hidden');
        $('#wrapperWebphone').removeClass('active');
    });
};

const setWhatsappStatusIcon = (tiene_whatsapp = false) => {
    $('#whatsappChat').css({ color: tiene_whatsapp ? '#52C159' : '#6A716A' });
};

$(function () {
    setEventListeners();
});