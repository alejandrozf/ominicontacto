import Cookies from 'universal-cookie';
import { createApp } from 'vue';
import VueSweetalert2 from 'vue-sweetalert2';
import store from '@/store';
import router from '@/router';
import App from './App.vue';
import Helpers from '@/helpers';
// import { formatTime } from '@/helpers/time_format_helper';

// Primevue
import PrimeVue from 'primevue/config';
import 'primeflex/primeflex.css';
import 'primevue/resources/themes/saga-green/theme.css'; // theme
import 'primevue/resources/primevue.min.css'; // core css
import 'primeicons/primeicons.css'; // icons

// Sweetalert Vue
import 'sweetalert2/dist/sweetalert2.min.css';

// Components primevue
import Card from 'primevue/card';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import ColumnGroup from 'primevue/columngroup';
import MultiSelect from 'primevue/multiselect';
import Message from 'primevue/message';
import Tooltip from 'primevue/tooltip';
import Dropdown from 'primevue/dropdown';
import Knob from 'primevue/knob';
import Chart from 'primevue/chart';
import Toolbar from 'primevue/toolbar';
import Dialog from 'primevue/dialog';
import InputNumber from 'primevue/inputnumber';
import Checkbox from 'primevue/checkbox';

// Idiomas
import { createI18n } from 'vue-i18n';
import messages from '@/locales';

// Configuramos los idiomas
const cookies = new Cookies();
const locale = cookies.get('django_language');
const i18n = createI18n({
    locale,
    fallbackLocale: 'en',
    messages
});

const app = createApp(App);

app.directive('tooltip', Tooltip);
app.component('Card', Card);
app.component('Button', Button);
app.component('InputText', InputText);
app.component('DataTable', DataTable);
app.component('Column', Column);
app.component('ColumnGroup', ColumnGroup);
app.component('MultiSelect', MultiSelect);
app.component('Message', Message);
app.component('Dropdown', Dropdown);
app.component('Knob', Knob);
app.component('Chart', Chart);
app.component('Toolbar', Toolbar);
app.component('Dialog', Dialog);
app.component('InputNumber', InputNumber);
app.component('Checkbox', Checkbox);

// Register Helpers
app.provide('$helpers', Helpers);

app.use(i18n)
    .use(store)
    .use(router)
    .use(VueSweetalert2)
    .use(PrimeVue)
    .mount('#app');
