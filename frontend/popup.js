const backendUrl = 'fastapi-gwc8fxewc8dheufx.eastus-01.azurewebsites.net';

// Handle Google Sign-In
function onSignIn(googleUser) {
    var profile = googleUser.getBasicProfile();
    var idToken = googleUser.getAuthResponse().id_token;

    // Save user info in localStorage
    localStorage.setItem('userName', profile.getName());
    localStorage.setItem('userEmail', profile.getEmail());
    localStorage.setItem('idToken', idToken);

    // Display the sign-out button and hide the sign-in button
    document.querySelector('.g-signin2').style.display = 'none';
    document.getElementById('signout-btn').style.display = 'inline-block';

    // Show the input section for uploading the image
    document.getElementById('input-section').style.display = 'block';
}

// Handle Google Sign-Out
function signOut() {
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {
        console.log('User signed out.');

        // Clear user info from localStorage
        localStorage.removeItem('userName');
        localStorage.removeItem('userEmail');
        localStorage.removeItem('idToken');

        // Show the sign-in button and hide the sign-out button
        document.querySelector('.g-signin2').style.display = 'inline-block';
        document.getElementById('signout-btn').style.display = 'none';

        // Hide the input section
        document.getElementById('input-section').style.display = 'none';
    });
}

// Check if the user is already signed in when the page loads
window.addEventListener('load', function() {
    if (localStorage.getItem('userName')) {
        // User is signed in, show the sign-out button and image input section
        document.querySelector('.g-signin2').style.display = 'none';
        document.getElementById('signout-btn').style.display = 'inline-block';
        document.getElementById('input-section').style.display = 'block';
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

    const response = await fetch(`${backendUrl}//upload-model-image/`, {
        method: 'POST',
        body: formData
    });

    if (response.ok) {
        const result = await response.json();
        const modelImagePath = result.model_image_url; // The URL of the uploaded image

        // Store the URL of the uploaded image
        window.localStorage.setItem('modelImageUrl', modelImageUrl);

        document.getElementById('upload-feedback').textContent = 'Model image uploaded successfully!';
        document.getElementById('upload-feedback').style.display = 'block';

        // Hide input section and show item details section
        document.getElementById('input-section').style.display = 'none';
        document.getElementById('item-section').style.display = 'block';

    } else {
        document.getElementById('upload-feedback').textContent = 'Error uploading model image.';
        document.getElementById('upload-feedback').style.display = 'block';
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
        console.error('Error classifying item');
    }
});

// Fetch the item details when the page loads
window.addEventListener('load', fetchItemDetails);


// run by git bash terminal : ./start.sh to run the server