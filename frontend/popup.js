const backendUrl = 'https://fastapi-gwc8fxewc8dheufx.eastus-01.azurewebsites.net';

// Function to handle Google sign-in using Chrome Identity API
function signInWithGoogle() {
    chrome.identity.getAuthToken({ interactive: true }, function(token) {
        if (chrome.runtime.lastError || !token) {
            console.error("Sign-in failed: ", chrome.runtime.lastError);
            return;
        }

        // Use the token to get user information from the Google API
        fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
            headers: {
                'Authorization': 'Bearer ' + token
            }
        })
        .then(response => response.json())
        .then(userInfo => {
            // Extract first name from full name
            const fullName = userInfo.name;
            const firstName = fullName.split(' ')[0]; // Get the first word (assumed to be the first name)

            // Save user info in localStorage
            localStorage.setItem('userName', firstName);
            localStorage.setItem('userEmail', userInfo.email);
            localStorage.setItem('userImage', userInfo.picture);

            // Update UI to display user info
            document.getElementById('user-name').textContent = firstName;
            document.getElementById('user-image').src = userInfo.picture;
            document.getElementById('user-info').style.display = 'flex';
            document.getElementById('input-section').style.display = 'block';

            // Check if model image exists in localStorage
            const modelImageUrl = localStorage.getItem('modelImageUrl');
            if (modelImageUrl) {
                fetchItemDetails(); // Only fetch details if model image exists
            }
        })
        .catch(error => console.error("Error fetching user info: ", error));
    });
}

// Function to handle Google sign-out
function signOut() {
    chrome.identity.clearAllCachedAuthTokens(() => {
        // Clear local storage
        localStorage.removeItem('userName');
        localStorage.removeItem('userEmail');
        localStorage.removeItem('userImage');
        localStorage.removeItem('modelImageUrl');

        // Reset UI
        document.getElementById('user-info').style.display = 'none';
        document.getElementById('input-section').style.display = 'none';

        // Automatically trigger sign-in again
        signInWithGoogle();
    });
}

/// Attach event listener to user image for sign-out
document.getElementById('user-image').addEventListener('click', signOut);

// Check if the user is already signed in when the page loads
window.addEventListener('load', function() {
    const userName = localStorage.getItem('userName');
    const userImage = localStorage.getItem('userImage');
    const modelImageUrl = localStorage.getItem('modelImageUrl');

    if (userName && userImage) {
        document.getElementById('user-name').textContent = userName;
        document.getElementById('user-image').src = userImage;
        document.getElementById('user-info').style.display = 'flex';
        document.getElementById('input-section').style.display = 'block';

        // Only run the APIs if the model image is saved
        if (modelImageUrl) {
            fetchItemDetails();
        }
    } else {
        // Automatically sign in if not signed in
        signInWithGoogle();
    }
});

// Handle the upload model image button click
document.getElementById('upload-model-btn').addEventListener('click', async () => {
    const fileInput = document.getElementById('model-image-input');
    const file = fileInput.files[0];

    if (!file) {
        document.getElementById('upload-feedback').textContent = 'Please select a file.';
        document.getElementById('upload-feedback').style.display = 'block';
        return;
    }

    const formData = new FormData();
    formData.append('model_image', file);

    try {
        const response = await fetch(`${backendUrl}/upload-model-image/`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            const modelImageUrl = result.model_image_url; // The URL of the uploaded image

            // Store the URL of the uploaded image
            window.localStorage.setItem('modelImageUrl', modelImageUrl);

            document.getElementById('upload-feedback').textContent = 'Model image uploaded successfully!';
            document.getElementById('upload-feedback').style.display = 'block';

            // Hide input section and show item details section
            document.getElementById('input-section').style.display = 'none';
            document.getElementById('item-section').style.display = 'block';

            // Now fetch item details since the model image has been uploaded
            await fetchItemDetails();
        } else {
            const errorText = await response.text(); // Get error details from the response
            document.getElementById('upload-feedback').textContent = `Error uploading model image: ${errorText}`;
            document.getElementById('upload-feedback').style.display = 'block';
            console.error(`Error response: ${errorText}`);
        }
    } catch (error) {
        // Catch network or other errors
        document.getElementById('upload-feedback').textContent = `Error uploading model image: ${error.message}`;
        document.getElementById('upload-feedback').style.display = 'block';
        console.error('Upload error:', error);
    }
});


// Fetch item details from the API and display them
async function fetchItemDetails() {
    const response = await fetch(`${backendUrl}/scrape-images/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url: 'https://www.zara.com/il/en/cropped-shirt-with-cutwork-embroidery-p03564079.html?v1=365453566&v2=2352910' })
    });

    if (response.ok) {
        const result = await response.json();
        document.getElementById('item-name').textContent = result.item_name;
        document.getElementById('item-image').src = result.garment_image_path;
        document.getElementById('item-image').style.display = 'block';
        document.getElementById('show-result-btn').style.display = 'block';
    } else {
        console.error('Error fetching item details');
    }
}

// Handle the show result button click to process the image
document.getElementById('show-result-btn').addEventListener('click', async () => {
    const garmentImagePath = document.getElementById('item-image').src;
    const itemName = document.getElementById('item-name').textContent;

    const response = await fetch(`${backendUrl}/classify-item/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ item_name: itemName })
    });

    if (response.ok) {
        const classifyResult = await response.json();
        const category = classifyResult.category;

        // Retrieve the stored Blob URL
        const modelImageUrl = localStorage.getItem('modelImageUrl');

        if (modelImageUrl) { // Only proceed if modelImageUrl exists
            const processResponse = await fetch(`${backendUrl}/process-image/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model_image_path: modelImageUrl,
                    garment_image_path: garmentImagePath,
                    category: category
                })
            });

            if (processResponse.ok) {
                const result = await processResponse.json();
                document.getElementById('result').innerHTML = `<img src="${result.garment_image_path}" alt="Garment Image" />`;
                document.getElementById('result-section').style.display = 'block';
            } else {
                console.error('Error processing image');
            }
        } else {
            console.error('Model image URL not found. Skipping image processing.');
        }
    } else {
        console.error('Error classifying item');
    }
});

// Fetch the item details when the page loads
window.addEventListener('load', fetchItemDetails);

// run by git bash terminal : ./start.sh to run the server