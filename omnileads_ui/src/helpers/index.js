import { getToasConfig, openLoader, closeLoader } from './sweet_alerts_helper';
import { formatTime, getDatetimeFormat } from './time_format_helper';

function getRandomColors (numColors) {
    const randomColor = () => Math.floor(Math.random() * 256); // Genera un número aleatorio entre 0 y 255
    const rgbColors = [];
    const rgbaColors = [];
    for (let i = 0; i < numColors; i++) {
        const red = randomColor();
        const green = randomColor();
        const blue = randomColor();

        rgbColors.push(`rgb(${red}, ${green}, ${blue})`);
        rgbaColors.push(`rgba(${red}, ${green}, ${blue}, 0.5)`);
    }
    return { rgbColors, rgbaColors };
}

export default {
    getToasConfig,
    openLoader,
    closeLoader,
    formatTime,
    getDatetimeFormat,
    isPhoneValid: (phone) => {
        // const regex = /^(\+\d{1,2}\s?)?(\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}$/;
        const regex = /^[\d()+\s-]{0,15}$/;
        return regex.test(phone);
    },
    getRandomColors
};
