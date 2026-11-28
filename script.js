/* NBA Dashboard — Tab switching */

document.addEventListener("DOMContentLoaded", function () {
  var buttons = document.querySelectorAll(".tab-btn");
  var contents = document.querySelectorAll(".tab-content");

  buttons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var target = btn.getAttribute("data-tab");

      buttons.forEach(function (b) {
        b.classList.remove("active");
      });
      btn.classList.add("active");

      contents.forEach(function (c) {
        c.classList.remove("active");
      });
      var el = document.getElementById(target);
      if (el) {
        el.classList.add("active");
      }
    });
  });
});
