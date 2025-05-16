// filepath: /home/utku/portfolio-project/portfolio/static/js/scripts.js
document.addEventListener("DOMContentLoaded", function() {
    // Handle preloader
    const preloader = document.querySelector(".preloader");
    if (preloader) {
        window.addEventListener("load", function() {
            setTimeout(function() {
                preloader.classList.add("fade-out");
            }, 500);
        });
        
        // If the page takes too long to load, hide preloader after 2.5s
        setTimeout(function() {
            if (preloader) {
                preloader.classList.add("fade-out");
            }
        }, 2500);
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
    var links = document.querySelectorAll("a[href^='#']");
    for(var i = 0; i < links.length; i++) {
        links[i].addEventListener("click", function(event) {
            event.preventDefault();
            var target = document.querySelector(this.getAttribute("href"));
            if(target) {
                var topOffset = target.offsetTop;
                window.scrollTo({
                    top: topOffset - 20,
                    behavior: "smooth"
                });
            }
        });
    }
    
    // Section reveal animations
    function revealSections() {
        const sections = document.querySelectorAll(".reveal");
        for (let i = 0; i < sections.length; i++) {
            const windowHeight = window.innerHeight;
            const elementTop = sections[i].getBoundingClientRect().top;
            const elementVisible = 150;
            if (elementTop < windowHeight - elementVisible) {
                sections[i].classList.add("active");
            }
        }
    }
    
    window.addEventListener("scroll", revealSections);
    
    // Initialize section reveals on page load
    revealSections();
    
    // Enhanced hover effects for project cards
    const projectCards = document.querySelectorAll(".project-card");
    
    projectCards.forEach(card => {
        // Add a subtle lift effect on hover
        card.addEventListener("mouseenter", function() {
            this.style.transform = "translateY(-8px) scale(1.02)";
            this.style.transition = "all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1)";
            
            // Add a slight border highlight
            const cardElement = this.querySelector(".card");
            if (cardElement) {
                cardElement.style.borderColor = "#3498db";
                cardElement.style.boxShadow = "0 15px 30px rgba(0, 0, 0, 0.12)";
            }
            
            // Highlight the title
            const cardTitle = this.querySelector(".card-title");
            if (cardTitle) {
                cardTitle.style.color = "#3498db";
            }
        });
        
        card.addEventListener("mouseleave", function() {
            this.style.transform = "translateY(0) scale(1)";
            
            const cardElement = this.querySelector(".card");
            if (cardElement) {
                cardElement.style.borderColor = "";
                cardElement.style.boxShadow = "";
            }
            
            const cardTitle = this.querySelector(".card-title");
            if (cardTitle) {
                cardTitle.style.color = "";
            }
            
            // Reset tech tags style
            const techTags = this.querySelectorAll(".tech-tag");
            techTags.forEach(tag => {
                tag.style.transform = "";
                tag.style.background = "";
            });
        });
    });
    
    // Animate skill bars when they come into view
    function animateSkillBars() {
        const skillBars = document.querySelectorAll(".skill-progress");
        skillBars.forEach(bar => {
            const level = bar.getAttribute("data-level");
            const bounding = bar.getBoundingClientRect();
            
            if (
                bounding.top >= 0 &&
                bounding.left >= 0 &&
                bounding.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                bounding.right <= (window.innerWidth || document.documentElement.clientWidth)
            ) {
                bar.style.width = level + "%";
            }
        });
    }
    
    // Run on scroll to animate skills when in view
    window.addEventListener("scroll", animateSkillBars);
    
    // Run once on load
    setTimeout(animateSkillBars, 500);
    
    // Typing effect for header tagline
    const tagline = document.querySelector(".tagline");
    if (tagline) {
        const text = tagline.textContent;
        tagline.textContent = "";
        let i = 0;
        
        function typeWriter() {
            if (i < text.length) {
                tagline.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 30); // Adjust speed as needed
            }
        }
        
        // Start typing effect after a delay
        setTimeout(typeWriter, 1200);
    }
});
