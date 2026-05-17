import { ofetch } from 'ofetch';
export function createRequest(options) {
    const request = ofetch.create(options);
    return request;
}
export default createRequest;
