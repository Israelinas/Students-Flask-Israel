let photos = ["/static/img/1.jpg", "/static/img/2.jpg", "/static/img/3.jpg"];
let i = 0;

function next() {
  if (i < photos.length - 1) {
    i++;
  } else {
    i = 0;
  }
  sliderPhoto.src = photos[i];
}

let interval = setInterval(next, 3000);

function moveNext() {
  next();
  clearInterval(interval);
  interval = setInterval(next, 3000);
}

previous.onclick = function() {
  if (i > 0) {
    i--;
  } else {
    i = photos.length - 1;
  }
  sliderPhoto.src = photos[i];
  clearInterval(interval);
  interval = setInterval(next, 3000);
}

next.onclick = function() {
  moveNext();
};

sliderPhoto.addEventListener('click', moveNext);
