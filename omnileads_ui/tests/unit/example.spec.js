describe('frontend smoke test', () => {
    it('runs the unit test suite', () => {
        expect(true).toBe(true);
    });
});

describe('locale helpers', () => {
    beforeEach(() => {
        document.documentElement.lang = '';
        delete window.navigator.language;
        Object.defineProperty(window.navigator, 'language', {
            configurable: true,
            value: 'en-US'
        });
    });

    it('normalizes Spanish variants to es', async () => {
        const { normalizeLocale } = await import('@/utils/locale');
        expect(normalizeLocale('es_AR')).toBe('es');
        expect(normalizeLocale('es-es')).toBe('es');
    });

    it('resolves the language from the cookie before falling back', async () => {
        const { resolveUiLocale } = await import('@/utils/locale');
        const cookies = { get: jest.fn(() => 'pt_BR') };
        expect(resolveUiLocale(cookies)).toBe('pt-br');
    });
});
