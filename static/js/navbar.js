document.addEventListener("DOMContentLoaded", function() {
    const mainHeader = document.querySelector(".main-header");
    
    if (mainHeader) {
        // Sticky Navbar shadow on scroll
        window.addEventListener("scroll", function() {
            if (window.scrollY > 10) {
                mainHeader.classList.add("scrolled");
            } else {
                mainHeader.classList.remove("scrolled");
            }
        });
    }

    // Close mobile menu on clicking a link
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const navbarCollapse = document.getElementById('navbarCollapse');
    
    if (navbarCollapse) {
        const bsCollapse = new bootstrap.Collapse(navbarCollapse, {toggle: false});
        
        navLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                if (navbarCollapse.classList.contains('show')) {
                    bsCollapse.hide();
                }
            });
        });
    }
});
