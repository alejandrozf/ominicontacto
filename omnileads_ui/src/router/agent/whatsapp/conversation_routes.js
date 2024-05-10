import Index from '@/views/agent/whatsapp/conversation/Index';
import ConversationNew from '@/views/agent/whatsapp/conversation/New';
import ImageUploader from '@/views/agent/whatsapp/conversation/ImageUploader';
import FileUploader from '@/views/agent/whatsapp/conversation/FileUploader';
import { WHATSAPP_URL_NAME } from '@/globals/agent/whatsapp';

export default [
    {
        path: `/${WHATSAPP_URL_NAME}_conversation/:id`,
        name: `${WHATSAPP_URL_NAME}_conversation_detail`,
        component: Index
    },
    {
        path: `/${WHATSAPP_URL_NAME}_conversation_new.html`,
        name: `${WHATSAPP_URL_NAME}_conversation_new`,
        component: ConversationNew
    },
    {
        path: `/${WHATSAPP_URL_NAME}_image_uploader.html`,
        name: `${WHATSAPP_URL_NAME}_image_uploader`,
        component: ImageUploader
    },
    {
        path: `/${WHATSAPP_URL_NAME}_file_uploader.html`,
        name: `${WHATSAPP_URL_NAME}_file_uploader`,
        component: FileUploader
    }
];
