import urls from '@/api_urls/supervisor/call_disposition_urls';
import { BaseService } from './../base_service';

export default class CallDispositionService extends BaseService {
    constructor () {
        super(urls, 'Calificacion');
    }
}
