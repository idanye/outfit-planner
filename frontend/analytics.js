async function getOrCreateClientId() {
    const result = await chrome.storage.local.get('clientId');
    let clientId = result.clientId;

    if (!clientId) {
        // Generate a unique client ID, the actual value is not relevant
        clientId = self.crypto.randomUUID();
        // Store the client ID in chrome.storage.local
        await chrome.storage.local.set({clientId});
        console.log('Client ID generated and stored:', clientId);
    } else {
        console.log('Existing Client ID:', result.client_id);
    }

    return clientId;
}

// Function to create or retrieve a session ID (for demonstration purposes)
async function getOrCreateSessionId() {
    let sessionId;
    // Check for an existing session ID in chrome.storage.local
    await chrome.storage.local.get('session_id', function (result) {
        sessionId = result.session_id;
        console.log('Session ID already exist: ', sessionId);
    });
  
    if (!sessionId) {
      // Generate a new session ID if not found
      sessionId = crypto.randomUUID(); // Use crypto.randomUUID() for a unique session ID
      chrome.storage.local.set({ session_id: sessionId });
      console.log('session id generated and stored successfully: ', sessionId);
    }
  
    return sessionId;
}

async function sendAnalyticsEvent(eventName, buttonId) {
    const clientId = await getOrCreateClientId();
    const sessionId = await getOrCreateSessionId();
    const engagementTimeMsec = 1000; // Example: 1000ms (1 second); adjust as needed

    console.log("Sending analytics event...");
      
    fetch('http://localhost:3000/send-analytics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            client_id: clientId,
            event_name: eventName,
            event_params: {
                id: buttonId,
                session_id: sessionId,
                engagement_time_msec: engagementTimeMsec,
            }
        }),
    })
    .then(response => response.json())
    .then(data => console.log('Event sent to backend:', data))
    .catch(error => console.error('Error sending event to backend:', error));
}

// Call the function to send an event
sendAnalyticsEvent();
