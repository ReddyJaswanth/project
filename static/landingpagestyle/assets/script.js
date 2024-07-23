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

var dropdown = document.getElementsByClassName("prev-chats-dropdown-btn");
var i;

for (i = 0; i < dropdown.length; i++) {
  dropdown[i].addEventListener("click", function () {
    this.classList.toggle("active");
    var dropdownContent = document.getElementById("chat-sessions-dropdown");
    if (dropdownContent.style.display === "block") {
      dropdownContent.style.display = "none";
    } else {
      dropdownContent.style.display = "block";
    }
  });
}
