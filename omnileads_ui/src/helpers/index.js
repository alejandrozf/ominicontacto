import { getToasConfig } from './sweet_alerts_helper';
import { formatTime } from './time_format_helper';

export default {
    getToasConfig,
    formatTime,
    isPhoneValid: (phone) => {
        const regex = /^(\+\d{1,2}\s?)?(\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}$/;
        return regex.test(phone);
    }
};
