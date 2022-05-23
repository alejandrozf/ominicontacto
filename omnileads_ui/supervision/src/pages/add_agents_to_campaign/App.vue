<template>
    <router-view />
</template>

<script>
import Cookies from 'universal-cookie';
const cookies = new Cookies();

export default {
    name: 'app',
    methods: {
        listenCookieChange (callback, interval = 1000) {
            let lastCookie = cookies.get('django_language');
            setInterval(() => {
                const cookie = cookies.get('django_language');
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
