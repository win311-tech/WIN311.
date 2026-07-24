// Navigation Toggle Functions
function toggleNav() {
  const nav = document.getElementById("navbar");
  const overlay = document.getElementById("menuOverlay");
  nav.classList.toggle("show");
  overlay.classList.toggle("show");
}

function closeNav() {
  const nav = document.getElementById("navbar");
  const overlay = document.getElementById("menuOverlay");
  nav.classList.remove("show");
  overlay.classList.remove("show");
}

// Initialize: Ensure navbar is closed on page load
document.addEventListener('DOMContentLoaded', () => {
  closeNav();
  
  // Add extra safeguard: close menu after a small delay to ensure it's really closed
  setTimeout(() => {
    const nav = document.getElementById("navbar");
    const overlay = document.getElementById("menuOverlay");
    if (nav && nav.classList.contains("show")) {
      nav.classList.remove("show");
    }
    if (overlay && overlay.classList.contains("show")) {
      overlay.classList.remove("show");
    }
  }, 100);
});

// Fade-in Animation on Scroll
const fadeInObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('is-visible');
    } else {
      
      entry.target.classList.remove('is-visible');
    }
  });
}, {
  threshold: 0.1,
  rootMargin: '0px 0px -50px 0px'
});

// Observe all fade-in sections
document.addEventListener('DOMContentLoaded', () => {
  const fadeInSections = document.querySelectorAll('.fade-in-section');
  fadeInSections.forEach(section => {
    fadeInObserver.observe(section);
  });
});

// Close menu when clicking on a navigation link
document.addEventListener('DOMContentLoaded', () => {
  const navLinks = document.querySelectorAll('.sidenav a');
  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      closeNav();
    });
  });
});

// Smooth scrolling for anchor links
document.addEventListener('DOMContentLoaded', () => {
  const anchorLinks = document.querySelectorAll('a[href^="#"]');
  anchorLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');
      if (href !== '#' && href !== '#home') {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      }
    });
  });
});

// Add subtle parallax effect to content
document.addEventListener('DOMContentLoaded', () => {
  let ticking = false;
  
  window.addEventListener('scroll', () => {
    if (!ticking) {
      window.requestAnimationFrame(() => {
        const scrolled = window.pageYOffset;
        const content = document.querySelector('.content');
        if (content) {
          content.style.transform = `translateY(${scrolled * 0.05}px)`;
        }
        ticking = false;
      });
      ticking = true;
    }
  });
});

// Form validation for contact page
document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form');
  if (form) {
    form.addEventListener('submit', (e) => {
      const inputs = form.querySelectorAll('input[required], textarea[required]');
      let isValid = true;
      
      inputs.forEach(input => {
        if (!input.value.trim()) {
          isValid = false;
          input.style.borderColor = 'red';
        } else {
          input.style.borderColor = '#ccc';
        }
      });
      
      if (!isValid) {
        e.preventDefault();
        alert('Please fill in all required fields.');
      }
    });
  }
});