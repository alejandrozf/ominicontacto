const SUPPORTED_LOCALES = ['es', 'en', 'fa', 'pt-br'];

function getParentDocument () {
    try {
        return window.parent?.document || null;
    } catch (error) {
        return null;
    }
}

function getParentLanguageSelectorValue () {
    const parentDocument = getParentDocument();
    return parentDocument?.getElementById('cambiarIdiomaSelect')?.value || null;
}

function getParentDocumentLanguage () {
    const parentDocument = getParentDocument();
    return parentDocument?.documentElement?.lang || null;
}

export function normalizeLocale (locale) {
    if (!locale) {
        return null;
    }

    const normalizedLocale = String(locale).trim().replace(/_/g, '-').toLowerCase();
    if (!normalizedLocale) {
        return null;
    }

    if (SUPPORTED_LOCALES.includes(normalizedLocale)) {
        return normalizedLocale;
    }

    const baseLocale = normalizedLocale.split('-')[0];
    if (SUPPORTED_LOCALES.includes(baseLocale)) {
        return baseLocale;
    }

    if (baseLocale === 'pt') {
        return 'pt-br';
    }

    return null;
}

export function resolveUiLocale (cookies) {
    const candidates = [
        cookies?.get('django_language'),
        getParentLanguageSelectorValue(),
        getParentDocumentLanguage(),
        document.documentElement.lang,
        window.navigator?.language
    ];

    for (const candidate of candidates) {
        const locale = normalizeLocale(candidate);
        if (locale) {
            return locale;
        }
    }

    return 'es';
}

export function setI18nLocale (i18n, locale) {
    const normalizedLocale = normalizeLocale(locale);
    if (!normalizedLocale || !i18n) {
        return;
    }

    if (i18n.global?.locale && typeof i18n.global.locale === 'object' && 'value' in i18n.global.locale) {
        i18n.global.locale.value = normalizedLocale;
        return;
    }

    if (typeof i18n.global?.locale === 'string') {
        i18n.global.locale = normalizedLocale;
        return;
    }

    if (i18n.locale && typeof i18n.locale === 'object' && 'value' in i18n.locale) {
        i18n.locale.value = normalizedLocale;
        return;
    }

    i18n.locale = normalizedLocale;
}
