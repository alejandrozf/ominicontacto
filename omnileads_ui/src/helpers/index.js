import { getToasConfig } from './sweet_alerts_helper';
import { formatTime } from './time_format_helper';

export default {
    getToasConfig,
    formatTime,
    isPhoneValid: (phone) => {
        const regex = /^\d{10}$/;
        return regex.test(phone);
    }
};
