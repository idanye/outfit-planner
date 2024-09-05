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
  

// const GA_ENDPOINT = 'https://www.google-analytics.com/mp/collect';
// const MEASUREMENT_ID = os.getenv('MEASUREMENT_ID');
// const API_SECRET = os.getenv('API_SECRET');

async function sendAnalyticsEvent() {
    // Generate or retrieve a unique client ID for the user
    const clientId = await getOrCreateClientId();
  
    // Generate or retrieve a session ID for the user session
    const sessionId = await getOrCreateSessionId(); // Implement this function to create or retrieve a session ID
  
    // Define engagement time in milliseconds
    const engagementTimeMsec = 1000; // Example: 1000ms (1 second); adjust based on actual engagement
  
    // Send the event to Google Analytics
    fetch(
      `${GA_ENDPOINT}?measurement_id=${MEASUREMENT_ID}&api_secret=${API_SECRET}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          client_id: clientId,
          events: [
            {
              name: 'button_clicked',
              params: {
                id: 'my-button',
                session_id: sessionId,
                engagement_time_msec: engagementTimeMsec,
              },
            },
          ],
        }),
      }
    ).then(response => response.json())
      .then(data => console.log('Event sent:', data))
      .catch(error => console.error('Error sending event:', error));
  }
  
  
  // // Call the function to send an event
  // sendAnalyticsEvent();

async function sendAnalyticsEvent() {
    const clientId = await getOrCreateClientId();
    const sessionId = await getOrCreateSessionId();
    const engagementTimeMsec = 1000; // Example: 1000ms (1 second); adjust as needed

    // Send the event to your backend API instead of directly to Google Analytics
    // fetch('http://127.0.0.1:8000/send-analytics', {
    fetch('http://localhost:8000/send-analytics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            client_id: clientId,
            event_name: 'button_clicked',
            event_params: {
                id: 'my-button',
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




