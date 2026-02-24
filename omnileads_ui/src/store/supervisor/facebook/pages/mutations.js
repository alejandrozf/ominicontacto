export default {
    initFacebookPages (state, pages) {
        console.log('initFacebookPages >>>', pages)
        state.supFacebookPages = pages;
    },
    initFacebookPage (state, page = null) {
        if (page) {
            state.supFacebookPage = {
                id: page.id,
                name: page.name,
                description: page.description,
                access_token: page.access_token,
                verify_token: page.verify_token,
                app_id: page.app_id,
                page_id: page.page_id,
                destination: {
                    data: page.destination ? page.destination.data : null,
                    type: page.destination ? page.destination.type : null,
                    id_tmp: page.destination && page.destination.type === 13 ? page.destination.id : 0
                },
                schedule: page.horario,
                welcome_message: page.welcome_message,
                goodbye_message: page.goodbye_message,
                out_of_hours_message: page.out_of_hours_message
            };
            state.supFacebookPageDestinationMenuOptions = page.destination ? page.destination.data : []
            console.log('state.supFacebookPage >>>>>>>`>', state.supFacebookPage)
        } else {
            state.supFacebookPage = {
                id: null,
                name: '',
                description: '',
                access_token: null,
                verify_token: '',
                app_id: '',
                page_id: '',
                destination: {
                    data: null,
                    type: 0,
                    id_tmp: 0,
                    is_main: true
                },
                schedule: null,
                welcome_message: '',
                goodbye_message: '',
                out_of_hours_message: ''
            };
            // state.supWhatsappLineOptions = [];
        }
    },
    initFormFlag (state, flag) {
        state.isFormToCreate = flag;
    },
    initFacebookPageCampaigns (state, campaigns) {
        console.log('initFacebookPageCampaigns >>>', campaigns)
        state.supFacebookPageCampaigns = campaigns;
    },
    initFacebookPageOptionForm (state, option = null) {
        state.supFacebookPageOptionForm = {
            id: option ? option.id : null,
            index: option ? option.index : 0,
            value: option ? option.value : '',
            description: option ? option.description : '',
            type_option: option ? option.type_option : 0,
            destination: option ? option.destination : null,
        };
        console.log('initFacebookPageOptionForm >>>', state.supFacebookPageOptionForm)
    },
    createFacebookPageOption (state, { data, menuId }) {
        const ultimoElemento = state.supFacebookPageOptions[state.supFacebookPageOptions.length - 1];
        const index = ultimoElemento ? ultimoElemento.index + 1 : 0;
        state.supFacebookPageOptions.push({
            index: index,
            id: index,
            value: data.value,
            description: data.description,
            type_option: data.type_option,
            destination: data.destination,
            menuId: menuId,
        });
        console.log('createFacebookPageOption >>>', state.supFacebookPageOptions)
    },
    updateFacebookPageOption (state, { id, data, menuId }) {
        const destinationOptions = state.supFacebookPage.destination.data.filter(item => item.id_tmp === menuId);
        const element = destinationOptions[0].options.find(item => item.id === id);
        if (element) {
            element.value = data.value;
            element.description = data.description;
            element.type_option = data.type_option;
            element.destination = data.destination;
        }
    },
    deleteFacebookPageOption (state, { id, menuId }) {
        const destinationOptions = state.supFacebookPage.destination.data.filter(item => item.id_tmp === menuId);
        destinationOptions[0].options = destinationOptions[0].options.filter(item => item.id !== id);
    }
};
