FIELD_PROMPT_MAP = {
    "trend": lambda value: f"Capturing the latest trend: **{value}**. Ensure a bold, high-contrast typography style for clear visibility.",
    "brand_name": lambda value: f"Highlight the brand identity: **{value}**. Use sharp, legible text with strong visual impact to enhance recognition.",
    "product_desc": lambda value: f"Showcase the product: **{value}**. Maintain a clean, well-defined typography style to ensure readability and appeal.",
    "job_desc": lambda value: f"Convey job opportunity details: **{value}**. Structure the text professionally using a clear, corporate font.",
    "message": lambda value: f"Craft a compelling message: **{value}**. Use large, bold text with high readability, and center it for maximum impact.",
    "font": lambda value: f"Choose typography for readability and strong visual presence: **{value}**. Keep it clean, distortion-free, and high-definition.",
    "colors": lambda value: f"Align the color palette with brand identity and aesthetics: **{value}**. Maintain strong contrast for better text clarity.",
    "festival_name": lambda value: f"Celebrate the spirit of **{value}** with vibrant yet readable festive-themed typography.",
    "event_desc": lambda value: f"Highlight the event details: **{value}**. Use an eye-catching, structured font for clear visibility.",
    "achievement": lambda value: f"Showcase a remarkable achievement: **{value}**. Use sharp, bold text to ensure prominence and recognition.",
}

post_type_prompts = {
    "social_media_post": (
        "You are a Professional Prompt Engineer. Your task is to create a **visually compelling, engaging, and high-impact** image prompt "
        "tailored for social media engagement. The image should be dynamic, bold, and attention-grabbing, ensuring high shareability.\n"
    ),
    "meme_post": (
        "You are a **Meme Artist & AI Prompt Engineer**, specializing in creating **hilarious, relatable, and viral** meme images.\n"
    ),
    "job_post": (
        "You are a **Corporate Graphic Designer** creating a **modern, professional, and visually engaging** job announcement image.\n"
    ),
    "festival_post": (
        "You are a **Creative Digital Artist** creating a **vibrant and festive** image that captures the spirit of the festival.\n"
    ),
    "achievement_post": (
        "You are a **Success Story Visualizer** tasked with creating a **grand, inspiring, and celebratory** image that highlights a major milestone.\n"
    ),
    "event_announcement": (
        "You are a **Professional Event Designer** creating an **exclusive, visually polished event announcement** poster.\n"
    ),
}

post_type_properties = {
    "social_media_post": {
        "style": "modern, eye-catching, digital artwork",
        "lighting": "vivid and well-lit",
        "focus": "sharp and well-defined elements",
        "mood": "energetic and engaging",
        "composition": "dynamic angles, depth, and movement",
        "color_scheme": "vibrant and high-contrast\n",
    },
    "meme_post": {
        "style": "cartoonish, exaggerated, expressive",
        "lighting": "flat and high contrast",
        "focus": "fun and humorous elements",
        "mood": "playful and comedic",
        "composition": "structured to maximize punchline impact",
        "color_scheme": "bold and attention-grabbing\n",
    },
}

post_type_fields = {
    "social_media_post": ["trend", "product_desc"],
    "meme_post": ["trend", "product_desc"],  
    "festival_post": ["festival_name"],
    "event_announcement": ["event_desc"],
    "achievement_post": ["achievement"],
    "job_post": ["job_desc"],
}


creative_guidelines = {
    "social_media_post": (
        "\n### **Creative Guidelines:**\n"
        "**Think Outside the Box:** Explore fresh perspectives, unique storytelling, or unexpected visual elements.\n"
        "**Striking Typography:** Use bold, readable text that integrates seamlessly without overpowering the image.\n"
        "**Vibrant & Trendy Aesthetics:** Ensure a modern, stylish, and appealing color scheme suitable for fast-scrolling feeds.\n"
        "**Engaging Composition:** Consider unconventional angles, depth of field, and asymmetry to enhance visual impact.\n"
        "**Subtle Brand Integration:** Incorporate brand aesthetics naturally without making the product placement feel forced.\n"
        "**Platform Optimization:** Ensure design aesthetics fit well with Instagram, Twitter, LinkedIn, or Facebook.\n"
    ),
    "meme_post": (
        "### **Meme Image Guidelines:**\n"
        "**Recognizable Meme Format:** Use popular meme styles (e.g., Wojak, NPC, Distracted Boyfriend, Drakeposting, or custom).\n"
        "**Expressive Characters & Scenes:** The AI should generate exaggerated facial expressions and clear emotions.\n"
        "**Sharp, Readable Text:** Ensure bold, high-contrast text with classic meme typography (e.g., Impact font, black outline).\n"
        "**Funny & Relatable Composition:** The image should convey humor instantly using clever framing and contrasting elements.\n"
        "**Subtle Yet Clear Branding:** Integrate brand elements naturally (e.g., as a character prop, background reference, or witty placement).\n"
        "**Bold, Cartoonish Aesthetic:** Use an expressive, comic-book, or exaggerated art style to ensure high visibility.\n"
    ),
    "job_post": (
        "### **Design Guidelines:**\n"
        "**Elegant & Professional:** Use modern aesthetics with smooth gradients and dynamic composition.\n"
        "**Typography Focus:** The job title and company name should be **bold and eye-catching**, while supporting text remains subtle.\n"
        "**Depth & Soft Lighting:** Incorporate depth effects, soft lighting, or minimal abstract design elements.\n"
        "**Branding Consistency:** Use company colors subtly while ensuring clarity and contrast.\n"
        "**Minimal but Engaging:** Reduce rigid structure—opt for a dynamic, open composition.\n"
        "**Subtle Call to Action:** Ensure an elegant yet noticeable CTA such as ‘Apply Now’ or ‘Join Our Team.’\n"
    ),
    "festival_post": (
        "### **Design Guidelines:**\n"
        "**Warm, Radiant Colors:** Use rich golds, reds, oranges, and culturally significant hues.\n"
        "**Cultural Symbolism:** Incorporate traditional patterns, motifs, or festival-related elements.\n"
        "**Joyful & Celebratory Mood:** Ensure the composition exudes happiness, togetherness, and festivity.\n"
        "**Elegant Typography:** Use decorative fonts or calligraphy-inspired text while maintaining readability.\n"
        "**Dynamic Visuals:** Ensure a lively composition with confetti, lanterns, fireworks, or floral designs.\n"
    ),
    "achievement_post": (
        "### **Design Guidelines:**\n"
        "**Golden & Triumphant Aesthetic:** Use gold, deep blues, and metallic accents for a premium look.\n"
        "**Strong Symbolism:** Include elements like trophies, laurels, stars, or a podium for success representation.\n"
        "**Dramatic Lighting:** Use highlights, spotlights, or dynamic backdrops to enhance the sense of achievement.\n"
        "**Motivational Mood:** Ensure the image inspires pride and confidence, with a bold yet refined look.\n"
    ),
    "event_announcement": (
        "### **Design Guidelines:**\n"
        "1. **Structured, Elegant Layout:** Ensure a clear hierarchy with well-aligned elements.\n"
        "2. **Bold, Readable Typography:** The event name, date, and location should be the focal points.\n"
        "3. **Premium & Sleek Aesthetic:** Use modern gradients, subtle textures, and refined color palettes.\n"
        "4. **Prestigious Atmosphere:** The image should evoke a sense of exclusivity and anticipation.\n"
    ),
}

extension = (
    "\nGenerate a **unique, highly detailed, and visually compelling** AI image prompt for Stable Diffusion 3.5 Large Model."
    "The output should strictly contain only two components:\n"
    "**1. Positive Prompt**\n"
    "**2. Negative Prompt**\n"
    "Ensure the prompts are **concise yet highly descriptive**, optimizing for visually compelling results."
)
