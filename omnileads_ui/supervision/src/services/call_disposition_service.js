import urls from '../const/call_disposition_urls';
import { BaseService } from './base_service';

export default class CallDispositionService extends BaseService {
    constructor () {
        super(urls, 'Calificacion');
    }
}
