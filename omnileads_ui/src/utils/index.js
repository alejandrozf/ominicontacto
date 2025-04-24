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


export function removeInPlace(array, item) {
    var foundIndex, fromIndex;

    // Look for the item (the item can have multiple indices)
    fromIndex = array.length - 1;
    foundIndex = array.lastIndexOf(item, fromIndex);

    while (foundIndex !== -1) {
        // Remove the item (in place)
        array.splice(foundIndex, 1);

        // Bookkeeping
        fromIndex = foundIndex - 1;
        foundIndex = array.lastIndexOf(item, fromIndex);
    }

    // Return the modified array
    return array;
}