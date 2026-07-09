document.addEventListener('DOMContentLoaded', () => {
  // Jahr im Footer
  const yearEl = document.getElementById('year');
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  // Mobiles Menü öffnen/schließen
  const navToggle = document.getElementById('navToggle');
  const mainNav = document.getElementById('mainNav');

  if (navToggle && mainNav) {
    navToggle.addEventListener('click', () => {
      const isOpen = mainNav.classList.toggle('is-open');
      navToggle.setAttribute('aria-expanded', String(isOpen));
    });

    mainNav.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        mainNav.classList.remove('is-open');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // Aktiven Nav-Link je nach sichtbarem Abschnitt markieren
  const sections = document.querySelectorAll('main section[id]');
  const navLinks = document.querySelectorAll('.main-nav a');

  const setActiveLink = (id) => {
    navLinks.forEach((link) => {
      link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
    });
  };

  if (sections.length && navLinks.length) {
    const sectionObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveLink(entry.target.id);
          }
        });
      },
      { rootMargin: '-45% 0px -45% 0px' }
    );

    sections.forEach((section) => sectionObserver.observe(section));
  }

  // Sanftes Einblenden der Abschnitte beim Scrollen
  const revealTargets = document.querySelectorAll(
    '.about-grid, .usp-grid, .process-grid, .menu-grid, .gallery-grid, .reviews-grid, .faq-list, .contact-grid'
  );

  revealTargets.forEach((el) => el.classList.add('reveal'));

  const revealObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );

  revealTargets.forEach((el) => revealObserver.observe(el));

  // Google-Maps-Karte erst nach Klick laden (kein automatischer Datenabruf bei Google)
  document.querySelectorAll('.map-placeholder').forEach((placeholder) => {
    const btn = placeholder.querySelector('.map-load-btn');
    if (!btn) return;

    btn.addEventListener('click', () => {
      const iframe = document.createElement('iframe');
      iframe.src = placeholder.dataset.mapSrc;
      iframe.title = placeholder.dataset.mapTitle || 'Karte';
      iframe.width = '100%';
      iframe.height = '100%';
      iframe.style.border = '0';
      iframe.loading = 'lazy';
      iframe.referrerPolicy = 'no-referrer-when-downgrade';
      placeholder.replaceWith(iframe);
    });
  });
});
