// Professional Portfolio JavaScript
document.addEventListener("DOMContentLoaded", function() {
    // Function to set the theme to dark
    const setDarkTheme = () => {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark'); // Keep localStorage for consistency if other parts rely on it
        
        // Update Mermaid theme if it exists
        if (typeof mermaid !== 'undefined') {
            mermaid.initialize({
                theme: 'dark'
            });
        }
        
        // Update highlight.js theme if it exists
        const lightTheme = document.getElementById('light-highlight-theme');
        const darkTheme = document.getElementById('dark-highlight-theme');
        if (lightTheme && darkTheme) {
            lightTheme.disabled = true;
            darkTheme.disabled = false;
        }
    };
    
    // Set dark theme by default
    setDarkTheme();
    
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
    
    // Handle tab switching
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            button.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });

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

    // Dynamic experience duration calculations (LinkedIn-style)
    const PRESENT_KEYWORDS = ['present', 'current', 'now'];
    const monthFormatters = {
        short: new Intl.DateTimeFormat('en-US', { month: 'short', year: 'numeric' }),
        long: new Intl.DateTimeFormat('en-US', { month: 'long', year: 'numeric' })
    };

    const isPresentValue = (value) => {
        if (value === undefined || value === null) {
            return true;
        }
        const normalized = value.toString().trim().toLowerCase();
        return normalized === '' || PRESENT_KEYWORDS.includes(normalized);
    };

    const parseDurationDate = (value, { defaultDay = 1 } = {}) => {
        if (value === undefined || value === null) {
            return null;
        }

        const trimmed = value.toString().trim();
        if (!trimmed) {
            return null;
        }

        if (isPresentValue(trimmed)) {
            return new Date();
        }

        const parts = trimmed.split(/[-\/]/).map((part) => Number(part));
        if (!parts.length || Number.isNaN(parts[0])) {
            return null;
        }

        const year = parts[0];
        const month = parts.length > 1 && !Number.isNaN(parts[1]) ? parts[1] - 1 : 0;
        const day = parts.length > 2 && !Number.isNaN(parts[2]) ? parts[2] : defaultDay;

        const parsedDate = new Date(year, month, day);

        return Number.isNaN(parsedDate.getTime()) ? null : parsedDate;
    };

    const formatMonthYear = (date, style = 'short') => {
        const formatter = monthFormatters[style] || monthFormatters.short;
        return formatter.format(date);
    };

    const calculateInclusiveMonths = (startDate, endDate) => {
        if (!(startDate instanceof Date) || !(endDate instanceof Date)) {
            return 0;
        }

        let totalMonths = (endDate.getFullYear() - startDate.getFullYear()) * 12;
        totalMonths += endDate.getMonth() - startDate.getMonth();

        if (endDate.getDate() >= startDate.getDate()) {
            totalMonths += 1;
        }

        return totalMonths < 0 ? 0 : totalMonths;
    };

    const pluralizeUnit = (value, singular, plural) => {
        if (!Number.isFinite(value) || value <= 0) {
            return '';
        }
        return `${value} ${value === 1 ? singular : plural}`;
    };

    const buildDurationText = (startDate, endDate, lessThanLabel = 'Less than a month') => {
        const totalMonths = calculateInclusiveMonths(startDate, endDate);

        if (totalMonths <= 0) {
            return lessThanLabel;
        }

        const years = Math.floor(totalMonths / 12);
        const months = totalMonths % 12;
        const parts = [];

        const yearLabel = pluralizeUnit(years, 'year', 'years');
        const monthLabel = pluralizeUnit(months, 'month', 'months');

        if (yearLabel) {
            parts.push(yearLabel);
        }

        if (monthLabel) {
            parts.push(monthLabel);
        }

        return parts.length ? parts.join(' ') : lessThanLabel;
    };

    const updateDurationBlocks = () => {
        const durationBlocks = document.querySelectorAll('[data-duration-start]');
        if (!durationBlocks.length) {
            return;
        }

        const now = new Date();

        durationBlocks.forEach((block) => {
            const { durationStart, durationEnd, durationFormat } = block.dataset;

            const startDate = parseDurationDate(durationStart, { defaultDay: 1 });
            const treatAsPresent = isPresentValue(durationEnd);
            const endDate = treatAsPresent ? now : parseDurationDate(durationEnd, { defaultDay: 1 });

            if (!(startDate instanceof Date) || !(endDate instanceof Date)) {
                return;
            }

            const periodSpan = block.querySelector('.period');
            if (periodSpan && periodSpan.dataset.periodAuto !== 'false') {
                const formatStyle = periodSpan.dataset.periodFormat || durationFormat || 'short';
                const uppercase = periodSpan.dataset.periodUppercase !== 'false';
                const startLabel = formatMonthYear(startDate, formatStyle);
                const endLabel = treatAsPresent ? 'Present' : formatMonthYear(endDate, formatStyle);
                const periodText = `${startLabel} - ${endLabel}`;
                periodSpan.textContent = uppercase ? periodText.toUpperCase() : periodText;
            }

            const lengthSpan = block.querySelector('.length');
            if (lengthSpan) {
                const lessThanLabel = lengthSpan.dataset.lessThanMonth || 'Less than a month';
                const prefix = lengthSpan.dataset.prefix !== undefined ? lengthSpan.dataset.prefix : '(';
                const suffix = lengthSpan.dataset.suffix !== undefined ? lengthSpan.dataset.suffix : ')';
                const durationLabel = buildDurationText(startDate, endDate, lessThanLabel);
                lengthSpan.textContent = durationLabel ? `${prefix}${durationLabel}${suffix}` : '';
            }
        });
    };

    const initializeDynamicDurations = () => {
        if (!document.querySelector('[data-duration-start]')) {
            return;
        }

        const runUpdate = () => updateDurationBlocks();

        runUpdate();

        const DURATION_REFRESH_MS = 1000 * 60 * 60; // Refresh every hour to keep "Present" roles accurate
        setInterval(runUpdate, DURATION_REFRESH_MS);

        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                runUpdate();
            }
        });
    };

    initializeDynamicDurations();
});
