function toggleElements(showElement, hideElements) {
    document.querySelectorAll(hideElements).forEach(el => el.style.display = "none");
    document.querySelector(showElement).style.display = "block";
  }