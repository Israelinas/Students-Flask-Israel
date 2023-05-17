const slider = document.querySelector('.slider');
const slides = slider.querySelectorAll('img');
const prevButton = slider.querySelector('.prev');
const nextButton = slider.querySelector('.next');
let currentIndex = 0;

function showSlide(index) {
  slides.forEach(slide => slide.style.opacity = 0);
  slides[index].style.opacity = 1;
}

function nextSlide() {
  currentIndex = (currentIndex + 1) % slides.length;
  showSlide(currentIndex);
}

function prevSlide() {
  currentIndex = (currentIndex + slides.length - 1) % slides.length;
  showSlide(currentIndex);
}

function autoSlide() {
  nextSlide();
}

let interval = setInterval(autoSlide, 3000);

slider.addEventListener('mouseenter', () => clearInterval(interval));
slider.addEventListener('mouseleave', () => interval = setInterval(autoSlide, 3000));

prevButton.addEventListener('click', prevSlide);
nextButton.addEventListener('click', nextSlide);
