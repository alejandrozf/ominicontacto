export function resetStoreDataByAction ({ action, data }) {
    window.parent.postMessage({ action, data }, '*');
}

export function listenerStoreDataByAction (action, callback) {
    window.parent.addEventListener('message', (event) => {
        if (event.data.action === action) {
            callback(event.data.data);
        }
    });
}
