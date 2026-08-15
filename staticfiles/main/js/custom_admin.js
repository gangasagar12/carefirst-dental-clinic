document.addEventListener("DOMContentLoaded", function() {
    // We target the table captions (or h2/h3 elements) that Unfold uses for app names
    // Unfold wraps app titles in elements, sometimes headers, sometimes div.font-semibold.
    const headings = document.querySelectorAll("h1, h2, h3, h4, h5, div.font-semibold, caption");
    
    headings.forEach(h => {
        // Only target elements that don't have deeply nested structures to avoid coloring inner UI elements
        if (h.children.length > 2) return;
        
        const text = h.innerText.trim().toLowerCase();
        
        // Apply beautiful curated colors depending on the text
        if (text === "authentication and authorization") {
            h.style.color = "#3b82f6"; // Tailwind Blue 500
        } else if (text === "blogs") {
            h.style.color = "#a855f7"; // Tailwind Purple 500
        } else if (text === "inquiries & appointments" || text === "appointments") {
            h.style.color = "#10b981"; // Tailwind Emerald 500
        } else if (text === "main") {
            h.style.color = "#d4af37"; // Custom Gold
        } else if (text === "recent actions") {
            h.style.color = "#6366f1"; // Tailwind Indigo 500
        }
        
        // If it was colored, make sure it overrides any important flags by using setProperty
        if (h.style.color) {
            h.style.setProperty("color", h.style.color, "important");
        }
    });
});
