// Number Animation ================================

function animateValue(el, start, end, duration, suffix = "", format = "") {
    let startTime = null;

    function step(timestamp) {
        if (!startTime) startTime = timestamp;
        const progress = Math.min((timestamp - startTime) / duration, 1);
        let value = progress * (end - start) + start;

        // formatting
        if (format === "k") {
            value = (value / 1000).toFixed(1) + "K";
        } else {
            value = Math.floor(value);
        }

        el.textContent = value + suffix;

        if (progress < 1) {
            requestAnimationFrame(step);
        }
    }

    requestAnimationFrame(step);
}

const counters = document.querySelectorAll(".about_card_body h1");

if (counters.length > 0) {
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = +counter.getAttribute("data-target");
                const suffix = counter.getAttribute("data-suffix") || "";
                const format = counter.getAttribute("data-format") || "";

                animateValue(counter, 0, target, 5000, suffix, format);
                observer.unobserve(counter); // animate once per counter
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(counter => observer.observe(counter));
}



// favorite_card ==================== 

document.querySelectorAll('.favorite-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        const icon = this.querySelector('i');
        if (icon.classList.contains('bi-heart')) {
            icon.classList.replace('bi-heart', 'bi-heart-fill');
            icon.style.color = "red"; // highlight when favorited
        } else {
            icon.classList.replace('bi-heart-fill', 'bi-heart');
            icon.style.color = "black"; // reset color
        }
    });
});



// onscroll change background ===============

window.addEventListener("scroll", function () {
    const header = document.querySelector(".header_inner_main");
    if (header) {
        if (window.scrollY > 50) { // adjust scroll value
            header.classList.add("scrolled");
        } else {
            header.classList.remove("scrolled");
        }
    }
});



// navbar_Active ====================

document.querySelectorAll(".navbar ul li a").forEach(link => {
    link.addEventListener("click", function () {
        // remove active class from all
        document.querySelectorAll(".navbar ul li a").forEach(el => el.classList.remove("active"));

        // add active to clicked one
        this.classList.add("active");
    });
});



// color_select_=====================

const circles = document.querySelectorAll(".color-options p");
const selectedColorText = document.getElementById("selectedColor");

circles.forEach(circle => {
    circle.addEventListener("click", () => {
        // Remove active class from all
        circles.forEach(c => c.classList.remove("active"));

        // Add active class to clicked one
        circle.classList.add("active");

        // Update text
        selectedColorText.textContent = circle.getAttribute("data-color");
    });
});


// Product_Detail_Seize_Select  ==================

const sizeButtons = document.querySelectorAll(".sizebtn");
const selectedSizeText = document.getElementById("selectedSize");

sizeButtons.forEach(button => {
    button.addEventListener("click", () => {
        if (button.classList.contains("disabled")) return;

        // Remove active from all
        sizeButtons.forEach(btn => btn.classList.remove("active"));

        // Add active to clicked one
        button.classList.add("active");

        // Update text
        selectedSizeText.textContent = button.getAttribute("data-size");
    });
});


// Quantity Js

const minusBtn = document.querySelector(".minus");
const plusBtn = document.querySelector(".plus");
const quantityValue = document.getElementById("quantityvalue");

let quantity = 0;

minusBtn.addEventListener("click", () => {
    if (quantity > 0) {
        quantity--;
        quantityValue.textContent = quantity;
    }
});

plusBtn.addEventListener("click", () => {
    quantity++;
    quantityValue.textContent = quantity;
});
