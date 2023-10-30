import Cookies from 'universal-cookie';
import { createApp } from 'vue';
import VueSweetalert2 from 'vue-sweetalert2';
import store from '@/store';
import router from '@/router';
import App from './App.vue';
import Helpers from '@/helpers';

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
import Calendar from 'primevue/calendar';
import Steps from 'primevue/steps';
import Toast from 'primevue/toast';
import ToastService from 'primevue/toastservice';
import Textarea from 'primevue/textarea';
import InlineMessage from 'primevue/inlinemessage';
import Password from 'primevue/password';
import FileUpload from 'primevue/fileupload';
import RadioButton from 'primevue/radiobutton';
import Fieldset from 'primevue/fieldset';
import Tag from 'primevue/tag';
import ProgressSpinner from 'primevue/progressspinner';
import Image from 'primevue/image';
import InputMask from 'primevue/inputmask';
import Avatar from 'primevue/avatar';
import Chip from 'primevue/chip';
import Badge from 'primevue/badge';
import BadgeDirective from 'primevue/badgedirective';
import Listbox from 'primevue/listbox';
import SplitButton from 'primevue/splitbutton';
import TabView from 'primevue/tabview';
import TabPanel from 'primevue/tabpanel';
import Panel from 'primevue/panel';
import SpeedDial from 'primevue/speeddial';

// Idiomas
import { createI18n } from 'vue-i18n';
import messages from '@/locales';

// Configuramos los idiomas
const cookies = new Cookies();
const locale = cookies.get('django_language');
const i18n = createI18n({
    locale,
    allowComposition: true,
    fallbackLocale: 'en',
    messages
});

const app = createApp(App);

// Directives Primevue
app.directive('badge', BadgeDirective);
app.directive('tooltip', Tooltip);

// Components Primevue
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
app.component('Calendar', Calendar);
app.component('Steps', Steps);
app.component('Toast', Toast);
app.component('Textarea', Textarea);
app.component('InlineMessage', InlineMessage);
app.component('Password', Password);
app.component('FileUpload', FileUpload);
app.component('RadioButton', RadioButton);
app.component('Fieldset', Fieldset);
app.component('Tag', Tag);
app.component('ProgressSpinner', ProgressSpinner);
app.component('Avatar', Avatar);
app.component('Image', Image);
app.component('InputMask', InputMask);
app.component('Chip', Chip);
app.component('Badge', Badge);
app.component('Listbox', Listbox);
app.component('SplitButton', SplitButton);
app.component('TabView', TabView);
app.component('TabPanel', TabPanel);
app.component('Panel', Panel);
app.component('SpeedDial', SpeedDial);

// Register Helpers
app.provide('$helpers', Helpers);

app.use(i18n)
    .use(store)
    .use(router)
    .use(VueSweetalert2)
    .use(PrimeVue)
    .use(ToastService)
    .mount('#app');
