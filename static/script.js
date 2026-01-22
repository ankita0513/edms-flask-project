document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector(".mobile-menu-toggle");
    const nav = document.querySelector(".nav-links");
    toggle.addEventListener("click", () => {
        nav.classList.toggle("show");
    });

    // Flash auto hide
    const flashes = document.querySelectorAll(".flash");
    flashes.forEach(f => {
        setTimeout(() => {
            f.style.opacity = 0;
        }, 4000);
    });
});
