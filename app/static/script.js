console.log("Script loaded");

async function fetchPostTypes() {
    try {
        console.log("Fetching post types...");
        const response = await fetch("/post-types");
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        console.log("Post types received:", data);
        const select = document.getElementById("postTypeSelect");
        select.innerHTML = '<option value="">-- Select --</option>'; // Clear and reset
        data.post_types.forEach(type => {
            const option = document.createElement("option");
            option.value = type;
            option.text = type;
            select.appendChild(option);
        });
    } catch (error) {
        console.error("Error fetching post types:", error);
        alert("Failed to load post types. Please try again later.");
    }
}

async function loadNewsByCategory() {
    const category = document.getElementById("categorySelect").value;
    const newsSelect = document.getElementById("newsSelect");
    if (!category) {
        newsSelect.innerHTML = '<option value="">-- Select News --</option>';
        return;
    }
    try {
        const response = await fetch(`/trends?category=${category}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        console.log("News received:", data);
        newsSelect.innerHTML = '<option value="">-- Select News --</option>';
        data.articles.forEach(article => {
            const option = document.createElement("option");
            option.value = article.title;
            option.text = article.title;
            newsSelect.appendChild(option);
        });
        updateTrend();
    } catch (error) {
        console.error("Error loading news by category:", error);
        newsSelect.innerHTML = '<option value="">Error loading news</option>';
        alert("Failed to load news. Please check the category and try again.");
    }
}

async function loadNewsByTopic() {
    const topic = document.getElementById("topicSearch").value.trim();
    const newsSelect = document.getElementById("newsSelect");
    if (!topic) {
        alert("Please enter a topic to search.");
        newsSelect.innerHTML = '<option value="">-- Select News --</option>';
        return;
    }
    try {
        const response = await fetch(`/fetch_trends/${encodeURIComponent(topic)}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        console.log("News received for topic:", data);
        newsSelect.innerHTML = '<option value="">-- Select News --</option>';
        data.articles.forEach(article => {
            const option = document.createElement("option");
            option.value = article.title;
            option.text = article.title;
            newsSelect.appendChild(option);
        });
        updateTrend();
    } catch (error) {
        console.error("Error loading news by topic:", error);
        newsSelect.innerHTML = '<option value="">Error loading news</option>';
        alert("Failed to load news for the topic. Please try a different topic.");
    }
}

async function loadForm() {
    const postType = document.getElementById("postTypeSelect").value;
    const formFieldsDiv = document.getElementById("formFields");
    const generateBtn = document.getElementById("generateBtn");
    const updateTrendsBtn = document.getElementById("updateTrendsBtn");

    // Guard against empty or invalid postType
    if (!postType) {
        formFieldsDiv.innerHTML = "";
        generateBtn.disabled = true;
        updateTrendsBtn.style.display = "none";
        return;
    }

    // Prevent duplicate execution
    if (formFieldsDiv.dataset.lastPostType === postType) return;
    formFieldsDiv.dataset.lastPostType = postType;

    formFieldsDiv.innerHTML = "";
    generateBtn.disabled = true;
    updateTrendsBtn.style.display = "inline-block";

    try {
        const response = await fetch(`/generate_prompt_form?post_type=${postType}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        console.log("Form data received:", data);

        const fields = [...data.required_fields, ...data.optional_fields];
        fields.forEach(field => {
            const div = document.createElement("div");
            div.className = "input-group";
            const label = document.createElement("label");
            label.textContent = `${field} ${data.required_fields.includes(field) ? '*' : ''}:`;
            label.htmlFor = field;
            div.appendChild(label);

            if (field === "trend") {
                const input = document.createElement("input");
                input.type = "hidden";
                input.id = field;
                input.name = field;
                input.value = document.getElementById("newsSelect").value || "";
                div.appendChild(input);
                const span = document.createElement("span");
                span.id = "trendDisplay";
                span.textContent = document.getElementById("newsSelect").value || "Select a news item above";
                div.appendChild(span);
            } else {
                const input = document.createElement("input");
                input.type = "text";
                input.id = field;
                input.name = field;
                input.placeholder = data.example[field] || `Enter ${field}`;
                div.appendChild(input);
            }
            formFieldsDiv.appendChild(div);
        });

        const newsSelectValue = document.getElementById("newsSelect").value;
        generateBtn.disabled = !newsSelectValue && data.required_fields.includes("trend");
    } catch (error) {
        console.error("Error loading form:", error);
        alert("Failed to load form fields. Please select a valid post type.");
        formFieldsDiv.innerHTML = "<p>Error loading form fields.</p>";
    }
}

// Ensure loadForm is only called via event listener
document.getElementById("postTypeSelect").addEventListener("change", loadForm);

async function updateTrends() {
    const category = document.getElementById("categorySelect").value;
    if (!category) {
        alert("Please select a category first.");
        return;
    }
    try {
        const response = await fetch(`/update_trends?category=${category}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        console.log("Trends updated");
        loadNewsByCategory();
        const generateBtn = document.getElementById("generateBtn");
        const newsSelectValue = document.getElementById("newsSelect").value;
        generateBtn.disabled = !newsSelectValue;
    } catch (error) {
        console.error("Error updating trends:", error);
        alert("Failed to update trends. Please try again.");
    }
}

function updateTrend() {
    const newsSelect = document.getElementById("newsSelect");
    const trendInput = document.getElementById("trend");
    const trendDisplay = document.getElementById("trendDisplay");
    if (trendInput && trendDisplay) {
        trendInput.value = newsSelect.value;
        trendDisplay.textContent = newsSelect.value || "Select a news item above";
        console.log("Trend updated to:", trendInput.value);
        const generateBtn = document.getElementById("generateBtn");
        generateBtn.disabled = !newsSelect.value;
    }
}

async function generatePrompt() {
    const postType = document.getElementById("postTypeSelect").value;
    const payload = { post_type: postType };
    
    updateTrend();
    
    const fields = document.querySelectorAll("#formFields input");
    fields.forEach(field => {
        if (field.value) {
            payload[field.id] = field.value;
        }
    });
    console.log("Payload sent:", payload);

    const resultDiv = document.getElementById("result");
    resultDiv.textContent = "Generating prompt...";
    resultDiv.classList.add("loading");

    let generateResult = null;
    try {
        // Step 1: Generate the prompt
        const generateResponse = await fetch("/generate_prompt", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        });
        if (!generateResponse.ok) {
            const errorText = await generateResponse.text();
            throw new Error(`HTTP error! status: ${generateResponse.status}, details: ${errorText}`);
        }
        generateResult = await generateResponse.json();
        console.log("Generated Prompt Response:", generateResult);
        resultDiv.textContent = generateResult.generated_prompt || "No prompt generated";
        resultDiv.classList.remove("loading");

        // Step 2: Generate the image using the workflow data
        resultDiv.innerHTML = `
            <div>${generateResult.generated_prompt}</div>
            <div>Generating image...</div>
            <div class="image-loading">Loading image...</div>
        `;
        resultDiv.classList.add("loading");

        const generateImageResponse = await fetch("/generate_image", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ workflow_data: generateResult.workflow_data })
        });
        if (!generateImageResponse.ok) {
            const errorText = await generateImageResponse.text();
            throw new Error(`HTTP error! status: ${generateImageResponse.status}, details: ${errorText}`);
        }

        // Step 3: Convert the image response to a base64 URL
        const imageBlob = await generateImageResponse.blob();
        if (!imageBlob || imageBlob.size === 0) {
            throw new Error("Received an empty image response");
        }
        const reader = new FileReader();
        const base64Image = await new Promise((resolve, reject) => {
            reader.onloadend = () => resolve(reader.result);
            reader.onerror = () => reject(new Error("Failed to convert image to base64"));
            reader.readAsDataURL(imageBlob);
        });

        // Step 4: Display the prompt and image in the div
        resultDiv.innerHTML = `
            <div>${generateResult.generated_prompt}</div>
            <div>Image generated successfully!</div>
            <img src="${base64Image}" alt="Generated Image" class="generated-image" />
        `;
        resultDiv.classList.remove("loading");
    } catch (error) {
        console.error("Error:", error);
        resultDiv.innerHTML = `
            <div>${generateResult ? generateResult.generated_prompt : "Error generating prompt"}</div>
            <div class="error-message">Error: ${error.message}</div>
        `;
        resultDiv.classList.remove("loading");
        alert(`Failed to process request. Error: ${error.message}`);
    }
}

// Add event listener for form changes to enable/disable generate button
document.getElementById("newsSelect").addEventListener("change", updateTrend);
document.getElementById("postTypeSelect").addEventListener("change", loadForm);

// Initial calls
fetchPostTypes();

// Add basic CSS for loading state
const style = document.createElement("style");
style.textContent = `
    .loading {
        font-style: italic;
        color: #888;
    }
    pre {
        white-space: pre-wrap; /* Allow text wrapping */
    }
`;
document.head.appendChild(style);