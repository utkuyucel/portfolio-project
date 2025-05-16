// Professional Portfolio JavaScript
document.addEventListener("DOMContentLoaded", function() {
    // Theme toggling functionality
    const themeToggle = document.getElementById("themeToggle");
    const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");
    
    // Function to set the theme
    const setTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Update Mermaid theme if it exists
        if (typeof mermaid !== 'undefined') {
            mermaid.initialize({
                theme: theme === 'dark' ? 'dark' : 'neutral'
            });
        }
        
        // Update highlight.js theme if it exists
        const lightTheme = document.getElementById('light-highlight-theme');
        const darkTheme = document.getElementById('dark-highlight-theme');
        if (lightTheme && darkTheme) {
            if (theme === 'dark') {
                lightTheme.disabled = true;
                darkTheme.disabled = false;
            } else {
                lightTheme.disabled = false;
                darkTheme.disabled = true;
            }
        }
    };
    
    // Check for saved theme preference or use the system preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        setTheme(savedTheme);
    } else {
        const systemTheme = prefersDarkScheme.matches ? 'dark' : 'light';
        setTheme(systemTheme);
    }
    
    // Theme toggle button handler
    if (themeToggle) {
        themeToggle.addEventListener("click", function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            setTheme(newTheme);
        });
    }
    
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
