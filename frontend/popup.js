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

    const response = await fetch('http://localhost:8000/upload-model-image/', {
        method: 'POST',
        body: formData
    });

    if (response.ok) {
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
    const response = await fetch('http://localhost:8000/scrape-images/', {
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

    const response = await fetch('http://localhost:8000/classify-item/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ item_name: itemName })
    });

    if (response.ok) {
        const classifyResult = await response.json();
        const category = classifyResult.category;

        const modelImagePath = "../backend/modelsImages/model_2.jpg"; // This should be updated with the actual model image path

        const processResponse = await fetch('http://localhost:8000/process-image/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model_image_path: modelImagePath,
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