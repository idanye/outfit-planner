
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

            // Hide sign-in section
            document.getElementById('signin-section').style.display = 'none';
            
            // Check if model image exists in localStorage
            const modelImageUrl = localStorage.getItem('modelImageUrl');
            // if (modelImageUrl) {
            //     fetchItemDetails(); // Only fetch details if model image exists
            // }
        })
        .catch(error => console.error("Error fetching user info: ", error));
    });
}

// Function to handle Google sign-out
function signOut() {
    // Display confirmation dialog
    const confirmSignOut = confirm("Are you sure you want to sign out?");
    
    if (confirmSignOut) {
        chrome.identity.getAuthToken({interactive: false}, function(token) {
            if (token) {
                // Revoke the token on Google's server
                fetch(`https://accounts.google.com/o/oauth2/revoke?token=${token}`)
                    .then(() => {
                        console.log('Token revoked at Google server');

                        // Clear the cached token
                        chrome.identity.removeCachedAuthToken({token: token}, function() {
                            console.log('Token removed from cache');

                            // Clear all cached tokens
                            chrome.identity.clearAllCachedAuthTokens(() => {
                                console.log('All tokens cleared');

                                // Remove the g_state cookie to reset exponential backoff
                                chrome.cookies.remove({
                                    url: "https://accounts.google.com",
                                    name: "g_state"
                                }, function(details) {
                                    if (details) {
                                        console.log('g_state cookie removed:', details);
                                    } else {
                                        console.error('Failed to remove g_state cookie');
                                    }
                                });

                                // Clear local storage
                                localStorage.removeItem('userName');
                                localStorage.removeItem('userEmail');
                                localStorage.removeItem('userImage');
                                localStorage.removeItem('modelImageUrl');

                                // Reset UI and Update UI to display sign-in section
                                showSection('signin-section');
                                document.getElementById('user-info').style.display = 'none';
                            });
                        });
                    })
                    .catch(error => console.error('Error revoking token:', error));
            }
        });
    }
}

// Add event listener for the sign-in button
document.getElementById('signin-button').addEventListener('click', signInWithGoogle);

// Attach event listener to user image for sign-out
document.getElementById('user-image').addEventListener('click', signOut);

// Check if the user is already signed in when the page loads
window.addEventListener('load', function() {
    const savedSection = localStorage.getItem('currentSection');
    const userName = localStorage.getItem('userName');
    const userImage = localStorage.getItem('userImage');
    const modelImageUrl = localStorage.getItem('modelImageUrl');  // Check if model image is uploaded

    console.log('user name: ', userName);
    console.log('user image: ', userImage);

    if (userName && userImage && modelImageUrl) {
        // Always check the current page and fetch details, even on load
        checkCurrentPageAndFetchDetails();

        showSection('input-section');

        document.getElementById('user-name').textContent = userName;
        document.getElementById('user-image').src = userImage;
        document.getElementById('user-info').style.display = 'flex';

        if (savedSection === 'item-section') {
            showSection('item-section');
        }

        if (savedSection === 'result-section') {
            showSection('result-section');
        }

        const itemImageElement = document.getElementById('item-image');

        // handle the case where the item-image element does not exist
        if (itemImageElement.value === undefined) {
            document.getElementById('show-result-btn').style.display = 'none';
            document.getElementById('item-image').style.display = 'none';
            document.getElementById('item-name').textContent = "Nothing to display";
            console.log('item-image element does not exists');
        } else {
            console.log('item-image element exist');
        }
    } else {
        // If not signed in, show the sign-in section
        showSection('signin-section');
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

    // Check if the selected file is an image
    const validImageTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validImageTypes.includes(file.type)) {
        document.getElementById('upload-feedback').textContent = 'Please upload a valid image file (JPEG, PNG, WebP).';
        document.getElementById('upload-feedback').style.display = 'block';
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`http://localhost:8000/upload-model-image/`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            console.log('Model image uploaded successfully');
            const result = await response.json();

            // Store the URL of the uploaded image
            window.localStorage.setItem('modelImageUrl', result.model_image_url);

            document.getElementById('upload-feedback').textContent = 'Model image uploaded successfully!';
            showSection('item-section');

            // Now fetch item details since the model image has been uploaded
            checkCurrentPageAndFetchDetails();

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

// Function to show a specific section and save it to localStorage
function showSection(sectionId) {
    // Hide all sections first
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.style.display = 'none');
    document.getElementById(sectionId).style.display = 'block';
    localStorage.setItem('currentSection', sectionId);
}

// Function to check the current page and fetch item details
function checkCurrentPageAndFetchDetails() {
    // Check if the user is signed in (i.e., if userName exists in localStorage)
    const userName = localStorage.getItem('userName');
    const modelImageUrl = localStorage.getItem('modelImageUrl');  // Get the model image URL from local storage

    if (!userName) {
        console.log('User is not signed in. Not fetching details.');
        showSection('signin-section');
        return;
    }

    if (!modelImageUrl) {
        console.log('No model image uploaded. Not fetching details.');
        // showNothingToDisplay("Please upload a model image first.");
        return;
    }

    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        const currentUrl = tabs[0].url;
        console.log('Checking the current URL:', currentUrl);

        const lastScrapedUrl = localStorage.getItem('lastScrapedUrl');
        const lastFetchedData = localStorage.getItem('lastFetchedData');
        const lastResultImage = localStorage.getItem('lastResultImage');

        console.log('Checking the last scraped URL:', lastScrapedUrl);

        // Only scrape if the URL hasn't been scraped last
        if (currentUrl === lastScrapedUrl && lastFetchedData) {
            console.log('URL was already the last scraped, skipping scraping.');
            // If the URL is the same, and we have fetched data, display it
            console.log('Using cached data for URL:', currentUrl);

            const data = JSON.parse(lastFetchedData);

            if (localStorage.getItem('hasViewedResult') === 'true') {
                displayResultImage(lastResultImage, data.item_name);
            } else {
                displayItemDetails(data);
            }
        } else {
            // Otherwise, fetch new data
            console.log('Fetching new data...');
            fetchItemDetails(currentUrl);
        }
    });
}

// Fetch item details from the API and display them
async function fetchItemDetails(currentUrl) {
    // Ensure result section is hidden during scraping
    document.getElementById('result-section').style.display = 'none';

    // Show loading icon
    showLoadingIcon();

    // Create a URL object from the current URL
    const urlObject = new URL(currentUrl);

    // 1. Check if the URL starts with https://www.zara.com/
    const domainRegex = /^https:\/\/www\.zara\.com\//;
    if (!domainRegex.test(currentUrl)) {
        console.log('Not a Zara URL');
        hideLoadingIcon();
        showNothingToDisplay("Nothing to display");
        return;
    }

    // 2. Extract the pathname and check if it contains "/p" followed by digits (product ID)
    const productPathRegex = /-p\d{8}\.html$/;
    if (!domainRegex.test(currentUrl) || !productPathRegex.test(urlObject.pathname)) {
        console.log('Url does not contain product path');
        hideLoadingIcon();
        showNothingToDisplay("Nothing to display");
        return;
    }

    // 3. Check if the query parameters contain v1 and v2 with numeric values
    const v1 = urlObject.searchParams.get("v1");
    const v2 = urlObject.searchParams.get("v2");

    if (!v1 || !v2 || isNaN(v1) || isNaN(v2)) {
        console.log('URL does not contain valid v1 and v2 parameters');
        hideLoadingIcon();
        showNothingToDisplay("Nothing to display");
        return;
    }

    // If all validations pass, make the API request
    fetch(`http://localhost:8000/scrape-images/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({url: currentUrl})
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(result => {
            hideLoadingIcon();

            if (result === "None") {
                // If there's an error, display the error message to the user
                showNothingToDisplay("Error fetching item details, try again later.");
            } else {
                // Display the item details and image
                displayItemDetails(result);

                console.log("SETTING lastScrapedUrl to:", currentUrl);

                // Save the last scraped URL
                localStorage.setItem('lastScrapedUrl', currentUrl);
                localStorage.setItem('lastFetchedData', JSON.stringify(result));
                localStorage.removeItem('hasViewedResult'); // Reset result view status
            }
        })
        .catch(error => {
            hideLoadingIcon();
            console.error('Error fetching item details:', error);
            showNothingToDisplay("Error fetching item details, try again later.");
        }
    );
}

// Helper function to show "Nothing to display" message
function showNothingToDisplay(message) {
    document.getElementById('item-name').textContent = `${message}`;// `"Nothing to display"
    document.getElementById('item-section').style.display = 'block';
    document.getElementById('result-section').style.display = 'none';
    document.getElementById('item-image').style.display = 'none';
    document.getElementById('show-result-btn').style.display = 'none';
}

// Helper function to show the loading icon
function showLoadingIcon() {
    document.getElementById('loading-icon').style.display = 'block';
    document.getElementById('item-name').textContent = "";
    document.getElementById('item-image').style.display = 'none';
    document.getElementById('show-result-btn').style.display = 'none';

    document.getElementById('result').style.display = 'none'; // Hide the result image
    document.getElementById('result-item-name').style.display = 'none'; // Hide the result item name
    document.getElementById('result-buttons').style.display = 'none'; // Hide the result buttons
}

// Helper function to hide the loading icon
function hideLoadingIcon() {
    document.getElementById('loading-icon').style.display = 'none';
}

// Function to display the item details
function displayItemDetails(data) {
    console.log("displayItemDetails started with:", data);
    // Make sure result section is hidden when showing item details
    document.getElementById('result-section').style.display = 'none';

    document.getElementById('item-section').style.display = 'block';
    document.getElementById('item-name').textContent = toTitleCase(data.item_name);
    document.getElementById('item-image').src = `http://localhost:8000${data.garment_image_path}`;
    document.getElementById('item-image').style.display = 'block';
    document.getElementById('show-result-btn').style.display = 'block';

    console.log("hasViewedResult before:", localStorage.getItem('hasViewedResult'));
    // Reset hasViewedResult to avoid showing result section automatically
    localStorage.removeItem('hasViewedResult');

    localStorage.setItem('lastFetchedData', JSON.stringify(data));
}

// Handle the show result button click to process the image
document.getElementById('show-result-btn').addEventListener('click', async () => {
    const garmentImageUrl = document.getElementById('item-image').src;
    const itemName = document.getElementById('item-name').textContent;
    console.log('show-result-btn clicked');

    document.getElementById('item-section').style.display = 'none';
    document.getElementById('result-section').style.display = 'block';
    document.getElementById('result-section-title').style.display = 'block';

    showLoadingIcon();

    const response = await fetch(`http://localhost:8000/classify-item/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ item_name: itemName })
    });

    if (response.ok) {
        const classifyResult = await response.json();
        const category = classifyResult.category;

        // Extract the correct relative path for the garment image
        const garmentImageRelativePath = garmentImageUrl.replace(`${window.location.origin}/garments-images/`, "garmentsImages/");
        const modelImageUrl = localStorage.getItem('modelImageUrl');

        if (modelImageUrl) { // Only proceed if modelImageUrl exists
            const processResponse = await fetch(`http://localhost:8000/model-process-image/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model_image_path: modelImageUrl,
                    garment_image_path: garmentImageRelativePath,
                    category: category
                })
            });
            if (!processResponse.ok) {
                hideLoadingIcon();
                showNothingToDisplay("Error processing image with the model, try again later.");
                console.error('Error processing image');
                return;
            }

            const result = await processResponse.json();
            if (result === 'None') {
                hideLoadingIcon();
                showNothingToDisplay("Failed to process the image with the model, try again later.");
                return;
            }
            if (processResponse.ok) {
                const imageUrl = `http://localhost:8000${result}`;

                hideLoadingIcon();
                displayResultImage(imageUrl, itemName);

                // Save the result image URL in localStorage
                localStorage.setItem('lastResultImage', imageUrl);

                console.log("hasViewedResult after:", localStorage.getItem('hasViewedResult'));
                // Now that the result is viewed, set hasViewedResult
                localStorage.setItem('hasViewedResult', 'true');
            }
        } else {
            hideLoadingIcon();
            showNothingToDisplay("Error processing image");
            console.error('Model image URL not found. Skipping image processing.');
        }
    } else {
        hideLoadingIcon();
        console.error('Error classifying item');
    }
});

// Function to display the result image
function displayResultImage(imageUrl, itemName) {
    const formattedItemName = toTitleCase(itemName);

    document.getElementById('result').innerHTML = `<img src="${imageUrl}" alt="Model Result Image" />`;
    document.getElementById('result').style.display = `flex`;
    document.getElementById('result-item-name').textContent = formattedItemName;
    document.getElementById('result-item-name').style.display = 'block'; // Hide the result item name
    document.getElementById('result-buttons').style.display = 'block'; // Hide the result buttons

    showSection('result-section');
    localStorage.setItem('hasViewedResult', 'true');

    document.getElementById('result-buttons').innerHTML = `
        <button id="return-to-details-btn">Return to Get Item Details</button>
        <button id="download-result-photo-btn">Download Result Image</button>
    `;

    document.getElementById('return-to-details-btn').addEventListener('click', () => {
        localStorage.setItem('hasViewedResult', 'false');

        checkCurrentPageAndFetchDetails();
        showSection('item-section');
    });

    document.getElementById('download-result-photo-btn').addEventListener('click', () => {
        downloadImage(imageUrl);
    });
}

// Function to convert item name to Title Case (not in all caps)
function toTitleCase(itemName) {
    return itemName
        .toLowerCase() // Convert the entire string to lowercase
        .split(' ') // Split the string by spaces into an array of words
        .map(word => word.charAt(0).toUpperCase() + word.slice(1)) // Capitalize the first letter of each word
        .join(' '); // Join the words back into a single string
}

// Helper function to download an image
function downloadImage(url) {
    const link = document.createElement('a');
    link.href = url;
    link.download = 'result-image.png'; // You can customize the filename here
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Additional HTML elements
document.getElementById('result-section').innerHTML += `<div id="result-buttons"></div>`;

// run by git bash terminal : ./start.sh to run the server
