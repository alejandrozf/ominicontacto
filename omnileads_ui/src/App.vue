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
</style>
