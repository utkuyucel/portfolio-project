// Professional Portfolio JavaScript
document.addEventListener("DOMContentLoaded", function() {
    // Handle scroll-to-top button
    const scrollToTopBtn = document.getElementById("scrollToTopBtn");
    if (scrollToTopBtn) {
        window.addEventListener("scroll", function() {
            if (window.pageYOffset > 300) {
                scrollToTopBtn.classList.add("show");
            } else {
                scrollToTopBtn.classList.remove("show");
            }
        });
        
        scrollToTopBtn.addEventListener("click", function() {
            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });
        });
    }
    
    // Smooth scrolling for anchor links
    const links = document.querySelectorAll("a[href^='#']");
    for(let i = 0; i < links.length; i++) {
        links[i].addEventListener("click", function(event) {
            event.preventDefault();
            const target = document.querySelector(this.getAttribute("href"));
            if(target) {
                const topOffset = target.offsetTop;
                window.scrollTo({
                    top: topOffset - 20,
                    behavior: "smooth"
                });
            }
        });
    }
    
    // Initialize Mermaid diagrams if present
    if (typeof mermaid !== 'undefined') {
        mermaid.initialize({
            startOnLoad: true,
            theme: 'neutral',
            securityLevel: 'loose',
            flowchart: { useMaxWidth: true }
        });
    }

    // Apply syntax highlighting to code blocks if highlight.js is loaded
    if (typeof hljs !== 'undefined') {
        document.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    }
});
