import Index from '@/views/supervisor/facebook/group_of_message_templates/Index';
import New from '@/views/supervisor/facebook/group_of_message_templates/New';
import Edit from '@/views/supervisor/facebook/group_of_message_templates/Edit';
import { FACEBOOK_URL_NAME } from '@/globals/supervisor/facebook';

export default [
    {
        path: `/${FACEBOOK_URL_NAME}_group_of_message_templates.html`,
        name: `${FACEBOOK_URL_NAME}_group_of_message_templates`,
        component: Index
    },
    {
        path: `/${FACEBOOK_URL_NAME}_group_of_message_templates/new`,
        name: `${FACEBOOK_URL_NAME}_group_of_message_templates_new`,
        component: New
    },
    {
        path: `/${FACEBOOK_URL_NAME}_group_of_message_templates/:id/edit`,
        name: `${FACEBOOK_URL_NAME}_group_of_message_templates_edit`,
        component: Edit
    }
];
