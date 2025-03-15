const imageInput = document.getElementById('imageInput');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const brushSize = document.getElementById('brushSize');
const brushSizeValue = document.getElementById('brushSizeValue');
const sendToComfyBtn = document.getElementById('sendToComfy');
let painting = false;
let currentBrushSize = brushSize.value;
let originalImageData = null;

imageInput.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                canvas.width = img.naturalWidth;
                canvas.height = img.naturalHeight;
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 0, 0);
                canvas.classList.remove('d-none');
                originalImageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});

brushSize.addEventListener('input', (e) => {
    currentBrushSize = e.target.value;
    brushSizeValue.textContent = currentBrushSize;
});

canvas.addEventListener('mousedown', () => painting = true);
canvas.addEventListener('mouseup', () => painting = false);
canvas.addEventListener('mouseleave', () => painting = false);
canvas.addEventListener('mousemove', draw);

function draw(e) {
    if (!painting) return;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;
    ctx.beginPath();
    ctx.arc(x, y, currentBrushSize, 0, Math.PI * 2);
    ctx.closePath();
    ctx.save();
    ctx.globalCompositeOperation = 'destination-out'; // Makes the drawn areas transparent
    ctx.fill();
    ctx.restore();
}

document.getElementById('saveMask').addEventListener('click', () => {
    const link = document.createElement('a');
    link.download = 'alpha_masked_image.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
});

const responseContainer = document.getElementById("responseContainer");
const responseText = document.getElementById("responseText");

// Send to ComfyUI API
sendToComfyBtn.addEventListener("click", async () => {
    if (!canvas || !imageInput.files[0]) {
        alert("Please upload an image and create a mask before sending.");
        return;
    }

    // Get positive and negative prompts
    const positivePrompt = document.getElementById("positive_prompt").value.trim();
    const negativePrompt = document.getElementById("negative_prompt").value.trim();

    if (!positivePrompt) {
        alert("Please enter a positive prompt.");
        return;
    }

    try {
        // Fetch the existing workflow JSON
        const workflowResponse = await fetch("./assets/inpaint_api.json");
        if (!workflowResponse.ok) throw new Error("Failed to load workflow JSON");
        const jsonBlob = await workflowResponse.blob();

        // Convert canvas (mask) to a Blob
        const maskBlob = await new Promise(resolve => canvas.toBlob(resolve, "image/png"));
        const imageFile = imageInput.files[0];

        if (!imageFile || !maskBlob) {
            alert("Missing image or mask.");
            return;
        }

        const formData = new FormData();
        formData.append("positive_prompt", positivePrompt);
        formData.append("negative_prompt", negativePrompt);
        formData.append("prompt_file", jsonBlob, "inpaint_api.json");
        formData.append("image", imageFile, "uploaded_image.png");
        formData.append("mask", maskBlob, "mask.png");

        const inpaintResponse = await fetch("http://127.0.0.1:8000/inpaint", {
            method: "POST",
            body: formData,
        });

        if (!inpaintResponse.ok) throw new Error("Failed to get the generated image");
        const imageBlob = await inpaintResponse.blob();

        // Display the generated image
        const imageUrl = URL.createObjectURL(imageBlob);
        let imgElement = document.getElementById("generatedImage");

        // If image already exists, update it; otherwise, create a new one
        if (!imgElement) {
            imgElement = document.createElement("img");
            imgElement.id = "generatedImage"; // Assign an ID to track it
            imgElement.classList.add("img-fluid", "mt-3", "border", "rounded");
            document.getElementById("responseContainer").appendChild(imgElement);
        }

        imgElement.src = imageUrl;
        imgElement.alt = "Generated Image";
        responseContainer.classList.remove("d-none");
    } catch (error) {
        console.error("Error:", error);
        responseText.textContent = `Error: ${error.message}`;
        responseContainer.classList.remove("d-none");
    }
});
