export default {
    supFacebookPages: [],
    supFacebookPageCampaigns: [],
    supFacebookPage: {
        id: null,
        name: '',
        description: '',
        access_token: null,
        verify_token: '',
        app_id: '',
        page_id: '',
        destination: {
            data: null,
            type: 0
        },
        schedule: null,
        welcome_message: null,
        goodbye_message: null,
        out_of_hours_message: null
    },
    isFormToCreate: false,
    supFacebookPageOptionForm: {
        id: null,
        index: 0,
        value: '',
        description: '',
        type_option: 0,
        destination: null,
        destination_name: '',
        menuId: null
    },
    supFacebookPageOptions: [],
    supWhatsappDestinationMenuOptions: [],
    supFacebookPageIteractiveForm: {
        id_tmp: 0,
        is_main: true,
        text: '',
        wrongAnswer: '',
        successAnswer: '',
        timeout: 0,
        options: []
    }
};
