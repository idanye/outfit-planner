function generateUniqueId() {
    return self.crypto.randomUUID();
}

function storeUniqueId() {
    chrome.storage.local.get(['clientId'], function(result) {
        if (!result.clientId) {
            const uniqueId = generateUniqueId();
            chrome.storage.local.set({ clientId: uniqueId }, function() {
                console.log('Unique ID stored:', uniqueId);
            });
        } else {
            console.log('Unique ID already exists:', result.clientId);
        }
    });
}

function sendToGoogleAnalytics(eventName, eventParams) {
    const measurementId = window.MEASUREMENT_ID; // Access the global variable
    const apiSecret = window.API_SECRET; // Access the global variable

    chrome.storage.local.get(['clientId'], function(result) {
        const clientId = result.clientId || generateUniqueId();
        const url = `https://www.google-analytics.com/mp/collect?measurement_id=${measurementId}&api_secret=${apiSecret}`;
        const payload = {
            client_id: clientId,
            events: [
                {
                    name: eventName,
                    params: eventParams
                }
            ]
        };

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        .then(response => {
            if (response.status === 204) {
                console.log('Event sent successfully');
            } else {
                console.error('Failed to send event', response.status, response.statusText);
            }
        })
        .catch(error => {
            console.error('Error sending event', error);
        });
    });
}

// Example usage
storeUniqueId();
sendToGoogleAnalytics('page_view', { page_title: document.title, page_location: window.location.href });