/**
 * Main application entry point.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize recipe manager
    recipeManager.init();
    
    // Initialize meal plan manager
    mealPlanManager.init();
    
    // Set up navigation
    setupNavigation();
});

/**
 * Set up navigation between pages.
 */
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const pages = document.querySelectorAll('.page');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Get page ID from data attribute
            const pageId = link.dataset.page;
            
            // Remove active class from all links and pages
            navLinks.forEach(link => link.classList.remove('active'));
            pages.forEach(page => page.classList.remove('active'));
            
            // Add active class to clicked link and corresponding page
            link.classList.add('active');
            document.getElementById(`${pageId}-page`).classList.add('active');
        });
    });
}

/**
 * Show an error message.
 * 
 * @param {string} message - Error message
 * @param {number} duration - Duration in milliseconds
 */
function showError(message, duration = 5000) {
    // Create error element
    const errorElement = document.createElement('div');
    errorElement.className = 'error-message';
    errorElement.textContent = message;
    
    // Add to body
    document.body.appendChild(errorElement);
    
    // Remove after duration
    setTimeout(() => {
        errorElement.classList.add('fade-out');
        setTimeout(() => {
            document.body.removeChild(errorElement);
        }, 300);
    }, duration);
}

/**
 * Format date string.
 * 
 * @param {string} dateString - Date string in ISO format
 * @param {Object} options - Intl.DateTimeFormat options
 * @returns {string} - Formatted date string
 */
function formatDate(dateString, options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', options);
}

/**
 * Generate a random color.
 * 
 * @returns {string} - Random color in hex format
 */
function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

/**
 * Truncate text to a specified length.
 * 
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} - Truncated text
 */
function truncateText(text, maxLength) {
    if (text.length <= maxLength) {
        return text;
    }
    return text.substring(0, maxLength) + '...';
}
