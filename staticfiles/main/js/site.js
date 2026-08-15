(() => {
  "use strict";

  const navbar = document.getElementById('ndNavbar');
  const searchTrigger = document.getElementById('ndSearchTrigger');
  const searchPanel = document.getElementById('ndSearchPanel');
  const searchClose = document.getElementById('ndSearchClose');
  const searchInput = document.getElementById('ndSearchInput');
  const burger = document.getElementById('ndBurger');
  const offcanvas = document.getElementById('ndOffcanvas');
  const offcanvasClose = document.getElementById('ndOffcanvasClose');
  const scrollThreshold = 40;

  const updateNavbarState = () => {
    if (!navbar) {
      return;
    }

    navbar.classList.toggle('is-scrolled', window.scrollY > scrollThreshold);
  };

  document.addEventListener('scroll', updateNavbarState, { passive: true });
  updateNavbarState();

  const openSearch = () => {
    if (!searchPanel || !searchInput) {
      return;
    }

    searchPanel.classList.add('open');
    window.setTimeout(() => searchInput.focus(), 150);
  };

  const closeSearch = () => {
    if (!searchPanel) {
      return;
    }

    searchPanel.classList.remove('open');
    searchTrigger?.focus();
  };

  searchTrigger?.addEventListener('click', openSearch);
  searchClose?.addEventListener('click', closeSearch);
  searchPanel?.addEventListener('click', (event) => {
    if (event.target === searchPanel) {
      closeSearch();
    }
  });

  const openOffcanvas = () => {
    if (!offcanvas || !burger) {
      return;
    }

    offcanvas.classList.add('open');
    burger.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  };

  const closeOffcanvas = () => {
    if (!offcanvas || !burger) {
      return;
    }

    offcanvas.classList.remove('open');
    burger.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
    burger.focus();
  };

  burger?.addEventListener('click', openOffcanvas);
  offcanvasClose?.addEventListener('click', closeOffcanvas);

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && searchPanel?.classList.contains('open')) {
      closeSearch();
    }

    if (event.key === 'Escape' && offcanvas?.classList.contains('open')) {
      closeOffcanvas();
    }
  });

  document.querySelectorAll('.nd-acc-btn').forEach((button) => {
    const panel = button.nextElementSibling;

    button.addEventListener('click', () => {
      const isOpen = button.getAttribute('aria-expanded') === 'true';

      document.querySelectorAll('.nd-acc-btn').forEach((otherButton) => {
        if (otherButton !== button) {
          otherButton.setAttribute('aria-expanded', 'false');
          otherButton.nextElementSibling.style.maxHeight = null;
        }
      });

      if (isOpen) {
        button.setAttribute('aria-expanded', 'false');
        panel.style.maxHeight = null;
      } else {
        button.setAttribute('aria-expanded', 'true');
        panel.style.maxHeight = `${panel.scrollHeight}px`;
      }
    });
  });

  document.querySelectorAll('.nd-cta').forEach((cta) => {
    cta.addEventListener('click', (event) => {
      const rect = cta.getBoundingClientRect();
      const ripple = document.createElement('span');
      const size = Math.max(rect.width, rect.height);

      ripple.className = 'ripple';
      ripple.style.width = `${size}px`;
      ripple.style.height = `${size}px`;
      ripple.style.left = `${event.clientX - rect.left - size / 2}px`;
      ripple.style.top = `${event.clientY - rect.top - size / 2}px`;

      cta.appendChild(ripple);
      ripple.addEventListener('animationend', () => ripple.remove());
    });
  });

  document.querySelectorAll('.nd-nav-link-btn').forEach((button) => {
    button.addEventListener('click', () => {
      const expanded = button.getAttribute('aria-expanded') === 'true';

      document.querySelectorAll('.nd-nav-link-btn').forEach((otherButton) => {
        otherButton.setAttribute('aria-expanded', 'false');
      });

      button.setAttribute('aria-expanded', expanded ? 'false' : 'true');
    });
  });

  // Intersection Observer for fade animations
  const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.15
  };

  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  document.querySelectorAll('[data-animation]').forEach((el) => {
    observer.observe(el);
  });

  // Animated Counters
  const counterObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const counters = entry.target.querySelectorAll('.counter');
        counters.forEach(counter => {
          const target = +counter.getAttribute('data-target');
          const duration = 2000;
          const step = target / (duration / 16); 
          
          let current = 0;
          const updateCounter = () => {
            current += step;
            if (current < target) {
              counter.innerText = Math.ceil(current);
              requestAnimationFrame(updateCounter);
            } else {
              counter.innerText = target;
            }
          };
          updateCounter();
        });
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  const counterSection = document.getElementById('counter-section');
  if (counterSection) {
    counterObserver.observe(counterSection);
  }

})();
