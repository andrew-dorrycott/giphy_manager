
function buildUX() {
  var username = document.getElementById("username");
  var password = document.getElementById("password");
  username.addEventListener("keyup", function(event) {
    if (event.keyCode === 13) {
      event.preventDefault();
      password.setFocus(); // I doubt this is correct
    }
  });
  password.addEventListener("keyup", function(event) {
    if (event.keyCode === 13) {
      event.preventDefault();
      document.getElementById("login").click();
    }
  });
}
