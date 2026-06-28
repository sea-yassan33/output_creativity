
    // 1. Dynamic Header transformation on Scroll
    const header = document.getElementById('header');
    
    window.addEventListener('scroll', () => {
      if (window.scrollY > 50) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
    });

    // 2. Intersection Observer for Smooth Scroll-Reveal Animations
    const revealElements = document.querySelectorAll('.reveal');
    
    const revealOnScroll = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('active');
          // Once animated, we don't need to observe it anymore
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.1, // trigger when 10% of element is visible
      rootMargin: "0px 0px -50px 0px" // subtle offset
    });

    revealElements.forEach(element => {
      revealOnScroll.observe(element);
    });

    // 3. Set Default Date values for the Reservation Form
    window.addEventListener('DOMContentLoaded', () => {
      const checkinInput = document.getElementById('checkin');
      const checkoutInput = document.getElementById('checkout');
      
      const today = new Date();
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);
      const dayAfterTomorrow = new Date(today);
      dayAfterTomorrow.setDate(dayAfterTomorrow.getDate() + 3);

      // Format to YYYY-MM-DD
      const formatDate = (date) => {
        const d = new Date(date);
        let month = '' + (d.getMonth() + 1);
        let day = '' + d.getDate();
        const year = d.getFullYear();

        if (month.length < 2) month = '0' + month;
        if (day.length < 2) day = '0' + day;

        return [year, month, day].join('-');
      };

      checkinInput.value = formatDate(tomorrow);
      checkoutInput.value = formatDate(dayAfterTomorrow);
    });
  