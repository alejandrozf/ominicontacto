const modalRegisterServerPopUp = $('#registerServerPopUp');
const sizeModal = $('#sizeModalRegisterServer');
const iframe = $('#iframeRegisterServer');

const closeModalRegisterServerPopUp = () => {
    modalRegisterServerPopUp.modal('hide');
};

const successRegisterServer = () => {
    iframe.attr('style', 'height: 50vh');
    sizeModal.removeClass('modal-lg');
};

const setEventListeners = () => {
    window.document.addEventListener(
        'onCloseModalRegisterServerPopUpEvent',
        closeModalRegisterServerPopUp,
        false
    );
    window.document.addEventListener(
        'onSuccessRegisterServerEvent',
        successRegisterServer,
        false
    );
};

const showModalRegisterServer = (registered = false) => {
    if (registered) {
        iframe.attr('style', 'height: 50vh');
        sizeModal.removeClass('modal-lg');
    } else {
        iframe.attr('style', 'height: 90vh');
        sizeModal.addClass('modal-lg');
    }
    modalRegisterServerPopUp.modal('show');
};

$(function () {
    setEventListeners();
});
