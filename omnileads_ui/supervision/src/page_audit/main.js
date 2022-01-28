import { createApp } from 'vue';
import App from './App.vue';
import router from '../router';

// Primevue
import PrimeVue from 'primevue/config';
import 'primeflex/primeflex.css';
import 'primevue/resources/themes/saga-blue/theme.css';       //theme
import 'primevue/resources/primevue.min.css' ;               //core css
import 'primeicons/primeicons.css';                           //icons

// Components primevue
import Card from 'primevue/card';
import Button from 'primevue/button';

const app = createApp(App);

app.component('Card', Card);
app.component('Button', Button);

app.use(router)
    .use(PrimeVue)
    .mount('#app');