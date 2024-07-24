const toggleBtnEL = document.getElementById("toggle-btn");
const asideEl = document.getElementById("aside");
let isAsideOpen = false;

toggleBtnEL.addEventListener("click", () => {
  if (isAsideOpen) {
    asideEl.classList.remove("active");
    isAsideOpen = false;
  } else {
    asideEl.classList.add("active");
    isAsideOpen = true;
  }
});
