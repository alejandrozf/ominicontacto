import Cookies from 'universal-cookie';
import { createI18n } from 'vue-i18n';
import messages from '@/locales';
import { resolveUiLocale } from '@/utils/locale';

const cookies = new Cookies();
const locale = resolveUiLocale(cookies);

const i18n = createI18n({
    locale,
    allowComposition: true,
    fallbackLocale: 'en',
    messages
});

export default i18n;
