// Handle user interactions and communicate with the backend.

document.getElementById('process-btn').addEventListener('click', async () => {
    const userImage = document.getElementById('user-image').files[0];
    if (userImage) {
        const formData = new FormData();
        formData.append('user_image', userImage);

        const response = await fetch('http://localhost:8000/process', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            document.getElementById('result').innerHTML = `<img src="${result.image_url}" />`;
        } else {
            console.error('Error processing image');
        }
    } else {
        console.error('No image selected');
    }
});
