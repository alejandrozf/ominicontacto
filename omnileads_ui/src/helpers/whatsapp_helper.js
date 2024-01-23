import { WhatsappConsumer } from '@/web_sockets/whatsapp_consumer';
import Swal from 'sweetalert2';

export function isSocketConnected ($t) {
    const consumer = WhatsappConsumer.getInstance({ $t });
    if (!consumer.isConnected()) {
        Swal.fire({
            title: $t('globals.warning_notification'),
            text: $t('globals.whatsapp.validations.socket_disconnect'),
            icon: $t('globals.icon_warning'),
            footer: $t('globals.whatsapp.validations.contact_admin'),
            html: null,
            timer: 5000,
            showConfirmButton: false,
            showCloseButton: true,
            position: 'top-end',
            toast: true
        });
        return false;
    }
    return true;
}
