document.addEventListener("DOMContentLoaded", () => {
    /*
    
    const guidePopup = document.getElementById("guide-popup");
    const closeGuide = document.getElementById("close-guide");
    const nextButton = document.getElementById("next-button");
    const guideSteps = document.getElementById("guide-steps");
    const progressBar = document.querySelector(".progress");
    const userTypeSelection = document.getElementById("user-type-selection");
    const guideContent = document.getElementById("guide-content");
    const guideTitle = document.getElementById("guide-title");
    const travelerButton = document.getElementById("traveler-button");
    const jobSeekerButton = document.getElementById("job-seeker-button");

    const travelerSteps = [
        "Explore exciting destinations worldwide",
        "Book your dream vacation with ease",
        "Enjoy personalized travel experiences",
        "Get 24/7 travel support from CasQid"
    ];

    const agentSteps = [
        "Register as a CasQid Travel Agent",
        "Access exclusive travel deals",
        "Manage bookings for your clients",
        "Grow your travel business with CasQid"
    ];

    const jobSeekerSteps = [
        "Browse overseas job opportunities",
        "Submit your application through CasQid",
        "Get assistance with work permits and visas",
        "Start your new career abroad"
    ];

    let currentStep = 0;
    let currentUserType = null;

    function showGuide() {
        guidePopup.classList.remove("hidden");
    }

    function hideGuide() {
        guidePopup.classList.add("hidden");
    }

    function updateSteps() {
        guideSteps.innerHTML = "";
        const steps = currentUserType === "traveler" ? travelerSteps : currentUserType === "agent" ? agentSteps : jobSeekerSteps;
        steps.forEach((step, index) => {
            const li = document.createElement("li");
            li.textContent = step;
            if (index === currentStep) {
                li.classList.add("active");
            }
            guideSteps.appendChild(li);
        });

        nextButton.textContent = currentStep < steps.length - 1 ? "NEXT" : "FINISH";
        updateProgress();
    }

    function updateProgress() {
        const steps = currentUserType === "traveler" ? travelerSteps : currentUserType === "agent" ? agentSteps : jobSeekerSteps;
        const progress = ((currentStep + 1) / steps.length) * 100;
        progressBar.style.width = `${progress}%`;
    }

    function nextStep() {
        const steps = currentUserType === "traveler" ? travelerSteps : currentUserType === "agent" ? agentSteps : jobSeekerSteps;
        if (currentStep < steps.length - 1) {
            currentStep++;
            updateSteps();
        } else {
            redirectUser();
        }
    }

    function setUserType(type) {
        currentUserType = type;
        userTypeSelection.classList.add("hidden");
        guideContent.classList.remove("hidden");
        nextButton.classList.remove("hidden");
        guideTitle.textContent = `Guide for ${type === "traveler" ? "Travelers" : type === "agent" ? "Agents" : "Job Seekers"}`;
        currentStep = 0;
        updateSteps();
    }

    function redirectUser() {
        if (currentUserType === "traveler") {
            window.location.href = "/"; // Adjust URL as needed
        } else if (currentUserType === "job-seeker") {
            window.location.href = "/"; // Adjust URL as needed
        }
    }

    closeGuide.addEventListener("click", hideGuide);
    nextButton.addEventListener("click", nextStep);
    travelerButton.addEventListener("click", () => setUserType("traveler"));
    jobSeekerButton.addEventListener("click", () => setUserType("job-seeker"));

    if (window.showGuide) {
        showGuide();
    }
*/ 
    const statsSection = document.getElementById("stats");
    const statCards = document.querySelectorAll(".stat-card");

    // Counter animation function
    function animateCounter(element, target) {
        let count = 0;
        const increment = Math.ceil(target / 100);
        const interval = setInterval(() => {
            count += increment;
            if (count >= target) {
                count = target;
                clearInterval(interval);
            }
            element.textContent = count;
        }, 20);
    }

    // GSAP Scroll Trigger Animation
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                gsap.to(entry.target, { opacity: 1, scale: 1, duration: 1, ease: "power2.out" });
            }
        });
    }, { threshold: 0.5 });

    statCards.forEach((card) => observer.observe(card));

    // Start the counter animations when section is in view
    const startCounters = () => {
        animateCounter(document.getElementById("travelers-count"), 5000);
        animateCounter(document.getElementById("years"), 3);
        animateCounter(document.getElementById("jobs-count"), 2500);
    };

    const statsObserver = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
            startCounters();
            statsObserver.disconnect(); // Run once
        }
    }, { threshold: 0.6 });

    statsObserver.observe(statsSection);


    // Testimonial slider
    const testimonialSlider = document.querySelector(".testimonial-slider")
    const testimonials = testimonialSlider.querySelectorAll(".testimonial-card")
    let currentTestimonial = 0
  
    function showTestimonial(index) {
      testimonials.forEach((testimonial, i) => {
        testimonial.style.display = i === index ? "block" : "none"
      })
    }
  
    function nextTestimonial() {
      currentTestimonial = (currentTestimonial + 1) % testimonials.length
      showTestimonial(currentTestimonial)
    }
  
    showTestimonial(currentTestimonial)
    setInterval(nextTestimonial, 5000)
  
    // Animate elements on scroll
    const animateOnScroll = () => {
      const elements = document.querySelectorAll(".testimonial-card")
      elements.forEach((element) => {
        const elementTop = element.getBoundingClientRect().top
        const elementBottom = element.getBoundingClientRect().bottom
        if (elementTop < window.innerHeight && elementBottom > 0) {
          element.style.animation = "fadeIn 1s ease-out forwards"
        }
      })
    }
  
    window.addEventListener("scroll", animateOnScroll)
    animateOnScroll() // Initial check on page load
});
