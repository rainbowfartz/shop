var button1 = document.getElementById("button1");
var button2 = document.getElementById("button2");
var div1 = document.getElementById("div1");
var div2 = document.getElementById("div2");
button1.addEventListener("click", function () {
  div1.classList.add("active");
  div2.classList.remove("active");
  button1.classList.add("active_button");
  button2.classList.remove("active_button");
});
button2.addEventListener("click", function () {
  div1.classList.remove("active");
  div2.classList.add("active");
  button1.classList.remove("active_button");
  button2.classList.add("active_button");
});

function togglePasswordVisibility() {
  var passwordInput = document.getElementById("passwordInput");
  var showPasswordCheckbox = document.getElementById("showPasswordCheckbox");
  passwordInput.type = showPasswordCheckbox.checked ? "text" : "password";
}
