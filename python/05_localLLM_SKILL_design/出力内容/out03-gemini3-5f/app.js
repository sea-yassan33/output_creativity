
    document.addEventListener("DOMContentLoaded", () => {
      // Set Copyright Year
      document.getElementById("currentYear").textContent = new Date().getFullYear();

      // 1. Initial Hero Fade In (200ms delay)
      const heroContent = document.getElementById("heroContent");
      setTimeout(() => {
        heroContent.classList.add("hero-loaded");
      }, 200);

      // 2. Header Scroll Transition Effects
      const siteHeader = document.getElementById("siteHeader");
      window.addEventListener("scroll", () => {
        if (window.scrollY > 50) {
          siteHeader.classList.add("scrolled");
        } else {
          siteHeader.classList.remove("scrolled");
        }
      });

      // 3. Scroll Reveal Animation (Intersection Observer)
      const reveals = document.querySelectorAll(".reveal");
      const observerOptions = {
        root: null,
        rootMargin: "0px",
        threshold: 0.12 // 12% threshold exactly as designed
      };

      const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target); // Trigger only once
          }
        });
      }, observerOptions);

      reveals.forEach(el => revealObserver.observe(el));

      // 4. Mobile Navigation Drawer & ARIA Control
      const menuToggle = document.getElementById("menuToggle");
      const navMenu = document.getElementById("navMenu");
      const navLinks = document.querySelectorAll(".nav-link");

      const toggleMobileMenu = () => {
        const isOpen = navMenu.classList.contains("active");
        navMenu.classList.toggle("active");
        siteHeader.classList.toggle("menu-open");
        menuToggle.setAttribute("aria-expanded", !isOpen);

        // Body Scroll Lock toggling
        if (!isOpen) {
          document.body.style.overflow = "hidden";
        } else {
          document.body.style.overflow = "";
        }
      };

      menuToggle.addEventListener("click", toggleMobileMenu);

      // Close menu when a link inside the mobile drawer is clicked
      navLinks.forEach(link => {
        link.addEventListener("click", () => {
          if (navMenu.classList.contains("active")) {
            toggleMobileMenu();
          }
        });
      });

      // Close menu on ESC keypress
      document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && navMenu.classList.contains("active")) {
          toggleMobileMenu();
        }
      });
    });

    // 5. Booking Form Submission Demo Handler
    function handleFormSubmit(event) {
      event.preventDefault();
      const submitBtn = document.getElementById("submitBtn");
      const bookingForm = document.getElementById("bookingForm");
      
      // Visual feedback flow
      submitBtn.disabled = true;
      submitBtn.textContent = "送信中...";

      setTimeout(() => {
        submitBtn.style.backgroundColor = "var(--aged-brass)";
        submitBtn.style.color = "var(--charcoal-earth)";
        submitBtn.textContent = "空室のご案内を送付しました。";
        
        // Reset form controls after elegant confirmation
        setTimeout(() => {
          bookingForm.reset();
          submitBtn.disabled = false;
          submitBtn.style.backgroundColor = "";
          submitBtn.style.color = "";
          submitBtn.textContent = "空室状況を確認し予約へ進む";
        }, 5000);
      }, 1500);
    }
  