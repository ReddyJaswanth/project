const signupRedirect = document.getElementById("signup");
const loginRedirect = document.getElementById("login");
const signupForm = document.getElementById("signup_form");
const loginForm = document.getElementById("login_form");

signupRedirect.addEventListener("click", () => {
  loginForm.style.display = "none";
  signupForm.style.display = "block";
});

loginRedirect.addEventListener("click", () => {
  signupForm.style.display = "none";
  loginForm.style.display = "block";
});
