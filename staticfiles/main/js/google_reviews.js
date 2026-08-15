document.addEventListener("DOMContentLoaded", function () {
  const carouselEl = document.getElementById("googleReviewsCarousel");
  if (!carouselEl || typeof bootstrap === "undefined") {
    return;
  }

  new bootstrap.Carousel(carouselEl, {
    interval: 7000,
    ride: "carousel",
    touch: true,
    pause: "hover",
  });
});
