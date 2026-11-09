function toggleNav() {
  const nav = document.getElementById('navbar');
  const overlay = document.getElementById('menuOverlay');
  const toggle = document.querySelector('.menu-toggle');
  const isOpen = nav.classList.toggle('show');
  overlay.classList.toggle('show', isOpen);
  toggle.setAttribute('aria-expanded', String(isOpen));
  toggle.setAttribute('aria-label', isOpen ? 'Close navigation' : 'Open navigation');
  document.body.classList.toggle('nav-open', isOpen);
}

function closeNav() {
  const nav = document.getElementById('navbar');
  const overlay = document.getElementById('menuOverlay');
  const toggle = document.querySelector('.menu-toggle');
  if (!nav || !overlay || !toggle) return;
  nav.classList.remove('show');
  overlay.classList.remove('show');
  toggle.setAttribute('aria-expanded', 'false');
  toggle.setAttribute('aria-label', 'Open navigation');
  document.body.classList.remove('nav-open');
}

document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('.menu-toggle');
  const closeButton = document.querySelector('.menu-close');
  const overlay = document.getElementById('menuOverlay');
  const navLinks = document.querySelectorAll('.sidenav a, .nav-cta');

  toggle?.addEventListener('click', toggleNav);
  closeButton?.addEventListener('click', closeNav);
  overlay?.addEventListener('click', closeNav);
  navLinks.forEach(link => link.addEventListener('click', closeNav));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') closeNav();
  });

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!prefersReducedMotion && 'IntersectionObserver' in window) {
    const revealTargets = document.querySelectorAll(
      '.inner-hero, .section-heading, .pathway-card, .systems-preview, .services-preview, .approach-section, .capability-card, .service-card, .lifecycle-list > div, .closing-cta, .contact-form-wrap'
    );
    document.documentElement.classList.add('motion-ready');
    const revealObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        entry.target.classList.toggle('is-visible', entry.isIntersecting);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    revealTargets.forEach(target => {
      target.classList.add('reveal-on-scroll');
      revealObserver.observe(target);
    });
  }
});
