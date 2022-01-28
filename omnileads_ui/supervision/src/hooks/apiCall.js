import { ref } from 'vue';
import Cookies from 'universal-cookie';
 
const cookies = new Cookies();

export const httpMethods = {
    'POST': 'POST',
    'GET': 'GET',
    'PUT': 'PUT',
    'DELETE': 'DELETE',
};

export const apiCall = (url, method = httpMethods.GET, params = {}) => {
    const loading = ref(false);
    const error = ref(null);
    let res = null;
    const response = ref({
        error: null, 
        data: res
    });

    let formData = new FormData();

    for (var key in params) {
        formData.append(key, params[key]);
    }
 
    const headers= {
        'X-CSRFToken': cookies.get('csrftoken')
    };



    let payload = {
        method: method,
        credentials: 'same-origin',
        headers
    };

    if (Object.keys(params).length > 0 && method != httpMethods.GET) {
        payload['body'] = formData;
    }

    

    const invoke = async() => {
        loading.value = true;

        try {
            const result = await fetch(url, payload);
            res = await result.json();
        } catch (ex) {
            error.value = ex.message;
        } finally {
            if (res['status'] && res['status'] != 'OK') {
                error.value = res['message'];
            }
            const r = {
                data: res,
                error: error.value
            };
            console.log(r);
            response.value = r;
            loading.value = false;
        }
    };

    invoke();

    return { response, loading };

};