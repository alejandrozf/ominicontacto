<template>
  <div id="app" class="h-full">
    <router-view v-slot="{ Component }">
      <transition name="route" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script>
import Cookies from 'universal-cookie';
import { resolveUiLocale, setI18nLocale } from '@/utils/locale';

export default {
    name: 'app',
    data () {
        return {
            cookies: new Cookies()
        };
    },
    methods: {
        syncLocale () {
            setI18nLocale(this.$i18n, resolveUiLocale(this.cookies));
        },
        listenCookieChange (callback, interval = 1000) {
            let lastCookie = this.cookies.get('django_language');
            setInterval(() => {
                const cookie = this.cookies.get('django_language');
                if (cookie !== lastCookie) {
                    try {
                        // eslint-disable-next-line node/no-callback-literal
                        callback({ newValue: cookie });
                    } finally {
                        lastCookie = cookie;
                    }
                }
            }, interval);
        }
    },
    created () {
        document.documentElement.style.setProperty(
            '--primary-color',
            window.parent.document.documentElement.style.getPropertyValue('--primary-color')
        );
        document.documentElement.style.setProperty(
            '--primary-light-color',
            window.parent.document.documentElement.style.getPropertyValue('--primary-light-color')
        );
        document.documentElement.style.setProperty(
            '--secondary-color',
            window.parent.document.documentElement.style.getPropertyValue('--secondary-color')
        );

        // Sync dark mode class from parent
        const syncDarkMode = () => {
            if (window.parent.document.documentElement.classList.contains('dark-mode')) {
                document.documentElement.classList.add('dark-mode');
            } else {
                document.documentElement.classList.remove('dark-mode');
            }
        };
        syncDarkMode(); // initial sync

        // Attempt to observe parent for class changes if cross-origin policy allows
        try {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.attributeName === 'class') {
                        syncDarkMode();
                    }
                });
            });
            observer.observe(window.parent.document.documentElement, { attributes: true });
        } catch (e) {
            // Fallback for strict cross-origin if needed
            setInterval(syncDarkMode, 1000);
        }
    },
    mounted () {
        this.syncLocale();
        this.listenCookieChange(() => {
            this.syncLocale();
        }, 1000);
    }
};
</script>

<style>
/* Global Premium Layout & Typography */
#app {
  font-family: 'Asap', sans-serif;
  font-weight: unset;
}

.swal2-popup {
  font-family: 'Asap', sans-serif;
  font-weight: unset;
}

/* Global PrimeVue Structural Overrides (Both Light/Dark) */
.p-card,
.p-dialog,
.p-datatable-wrapper,
.p-button {
  border-radius: 12px !important;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.p-card,
.p-dialog {
  box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
  border: none !important;
}

/* Micro-interactions */
.p-card:hover, .p-button:not(.p-disabled):hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.12) !important;
}

/* Glassmorphism */
.p-dialog-mask {
  backdrop-filter: blur(8px);
  background-color: rgba(0, 0, 0, 0.4) !important;
}

.p-inputtext,
.p-dropdown,
.p-multiselect {
  border-radius: 8px !important;
  transition: border-color 0.2s, box-shadow 0.2s;
}

/* Route Transitions */
.route-enter-active,
.route-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.route-enter-from,
.route-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

.swal2-popup .swal2-styled:focus {
    box-shadow: none !important;
}

h1, h2, h3, h4 {
    font-weight: unset;
}

/* --- Dark Mode Variables and Overrides --- */
html.dark-mode {
  --bg-main: #2b2d31; /* Discord Deep */
  --bg-sidebar: #1e1f22; /* Discord Darkest */
  --bg-topbar: #1e1f22;
  --text-main: #dbdee1;
  --text-heading: #f2f3f5;
  --bg-card: #313338;
  --border-color: rgba(255,255,255,0.05);
  background-color: var(--bg-main) !important;
}

html.dark-mode body,
html.dark-mode #app,
html.dark-mode .p-component {
  background-color: var(--bg-main) !important;
  color: var(--text-main) !important;
}

html.dark-mode .p-card,
html.dark-mode .p-panel,
html.dark-mode .p-dialog .p-dialog-content,
html.dark-mode .p-dialog .p-dialog-header,
html.dark-mode .p-dialog .p-dialog-footer,
html.dark-mode .p-datatable-wrapper,
html.dark-mode .p-datatable-header,
html.dark-mode .p-datatable-footer,
html.dark-mode .p-paginator {
  background-color: var(--bg-card) !important;
  color: var(--text-heading) !important;
  border-color: var(--border-color) !important;
}

html.dark-mode .p-datatable .p-datatable-thead > tr > th,
html.dark-mode .p-datatable .p-datatable-tbody > tr > td {
  background-color: var(--bg-card) !important;
  color: var(--text-main) !important;
  border-color: var(--border-color) !important;
}

html.dark-mode input,
html.dark-mode .p-inputtext,
html.dark-mode .p-dropdown,
html.dark-mode .p-multiselect {
  background-color: var(--bg-main) !important;
  color: var(--text-main) !important;
  border-color: rgba(255,255,255,0.2) !important;
}

html.dark-mode .p-button.p-button-secondary {
  background-color: var(--bg-card) !important;
  color: var(--text-heading) !important;
  border-color: rgba(255,255,255,0.2) !important;
}
</style>
