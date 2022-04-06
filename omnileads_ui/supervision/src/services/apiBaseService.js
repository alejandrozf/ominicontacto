import Cookies from 'universal-cookie';

export const HTTP = {
    POST: 'POST',
    GET: 'GET',
    PUT: 'PUT',
    DELETE: 'DELETE'
};

export class BaseService {
    constructor () {
        this.cookies = new Cookies();
        this.headers = {
            'X-CSRFToken': this.cookies.get('csrftoken'),
            'Content-Type': 'application/json'
        };
        this.initPayload();
    }

    setPayload (method = HTTP.POST, body = null) {
        if (body) {
            this.payload.body = body;
        }
        this.payload.method = method;
    }

    initPayload () {
        this.payload = {
            method: HTTP.GET,
            credentials: 'same-origin',
            headers: this.headers
        };
    }
}
