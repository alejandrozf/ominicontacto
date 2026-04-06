import Index from '@/views/agent/facebook/conversation/Index';
import ConversationNew from '@/views/agent/facebook/conversation/New';
import ImageUploader from '@/views/agent/facebook/conversation/ImageUploader';
import FileUploader from '@/views/agent/facebook/conversation/FileUploader';
import { FACEBOOK_URL_NAME } from '@/globals/agent/facebook';

export default [
    {
        path: `/${FACEBOOK_URL_NAME}_conversation/:id`,
        name: `${FACEBOOK_URL_NAME}_conversation_detail`,
        component: Index
    },
    {
        path: `/${FACEBOOK_URL_NAME}_conversation_new.html`,
        name: `${FACEBOOK_URL_NAME}_conversation_new`,
        component: ConversationNew
    },
    {
        path: `/${FACEBOOK_URL_NAME}_image_uploader.html`,
        name: `${FACEBOOK_URL_NAME}_image_uploader`,
        component: ImageUploader
    },
    {
        path: `/${FACEBOOK_URL_NAME}_file_uploader.html`,
        name: `${FACEBOOK_URL_NAME}_file_uploader`,
        component: FileUploader
    }
];
