import urls from '../const/group_of_hour_urls';
import { BaseService } from './base_service';

export default class GroupOfHourService extends BaseService {
    constructor () {
        super(urls, 'Grupo Horario');
    }
}
