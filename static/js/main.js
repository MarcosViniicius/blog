// Dark Mode Toggle Logic
const body = document.body;
const html = document.documentElement;
const themeToggle = document.getElementById('theme-toggle');
const sunIcon = document.getElementById('sun-icon');
const moonIcon = document.getElementById('moon-icon');

function updateTheme(isDark) {
    if (isDark) {
        html.classList.add('dark');
        sunIcon.classList.add('hidden');
        moonIcon.classList.remove('hidden');
        localStorage.setItem('theme', 'dark');
    } else {
        html.classList.remove('dark');
        sunIcon.classList.remove('hidden');
        moonIcon.classList.add('hidden');
        localStorage.setItem('theme', 'light');
    }
}

// Initialize theme from storage
const savedTheme = localStorage.getItem('theme') || 'dark';
updateTheme(savedTheme === 'dark');

themeToggle.addEventListener('click', () => {
    const isDark = html.classList.contains('dark');
    updateTheme(!isDark);
});

// Mobile Menu Control logic
const menuToggle = document.getElementById('menu-toggle');
const menuClose = document.getElementById('menu-close');
const overlay = document.getElementById('mobile-overlay');

if (menuToggle) {
    menuToggle.addEventListener('click', () => {
        overlay.classList.add('active');
        body.classList.add('menu-open');
    });
}

if (menuClose) {
    menuClose.addEventListener('click', () => {
        overlay.classList.remove('active');
        body.classList.remove('menu-open');
    });
}

// Search functionality (Title only)
const searchInput = document.getElementById('search-input');
if (searchInput) {
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        const posts = document.querySelectorAll('.post-item');
        
        posts.forEach(post => {
            const titleLink = post.querySelector('.post-title-link');
            if (!titleLink) return;
            
            const title = titleLink.innerText.toLowerCase();
            if (title.includes(query)) {
                post.style.display = 'block';
            } else {
                post.style.display = 'none';
            }
        });

        // Hide empty groups
        document.querySelectorAll('.month-group').forEach(group => {
            const visibleInMonth = Array.from(group.querySelectorAll('.post-item')).some(p => p.style.display !== 'none');
            group.style.display = visibleInMonth ? 'block' : 'none';
        });
        
        document.querySelectorAll('.year-group').forEach(group => {
            const visibleInYear = Array.from(group.querySelectorAll('.month-group')).some(m => m.style.display !== 'none');
            group.style.display = visibleInYear ? 'block' : 'none';
        });
    });
}

// Close overlay on escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && overlay && overlay.classList.contains('active')) {
        overlay.classList.remove('active');
        body.classList.remove('menu-open');
    }
});