<template>
  <div id="app" class="h-full">
    <router-view />
  </div>
</template>

<script>
import Cookies from 'universal-cookie';

export default {
    name: 'app',
    data () {
        return {
            cookies: new Cookies()
        };
    },
    methods: {
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
    created() {
        document.documentElement.style.setProperty(
            '--primary-color',
            window.parent.document.documentElement.style.getPropertyValue('--primary-color')
        )
        document.documentElement.style.setProperty(
            '--primary-light-color',
            window.parent.document.documentElement.style.getPropertyValue('--primary-light-color')
        )
        document.documentElement.style.setProperty(
            '--secondary-color',
            window.parent.document.documentElement.style.getPropertyValue('--secondary-color')
        )
        
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
        this.listenCookieChange(({ newValue }) => {
            this.$i18n.locale = newValue;
        }, 1000);
    }
};
</script>

<style>
#app {
  font-family: sans-serif;
  font-weight: unset;
}

.swal2-popup {
  font-family: sans-serif;
  font-weight: unset;
}

.swal2-popup .swal2-styled:focus {
    box-shadow: none !important;
}

h1, h2, h3, h4 {
    font-weight: unset;
}

/* --- Dark Mode Variables and Overrides --- */
html.dark-mode {
  --bg-main: #36393f;
  --bg-sidebar: #2f3136;
  --bg-topbar: #202225;
  --text-main: #dcddde;
  --text-heading: #ffffff;
  --bg-card: #2f3136;
  --border-color: #202225;
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
