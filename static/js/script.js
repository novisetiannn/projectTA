(function() {
  document.addEventListener("DOMContentLoaded", function() {
    // SIDEBAR DROPDOWN
    const allDropdown = document.querySelectorAll("#sidebar .side-dropdown");
    const sidebar = document.getElementById("sidebar");

    allDropdown.forEach((item) => {
      const a = item.parentElement.querySelector("a:first-child");
      a.addEventListener("click", function (e) {
        e.preventDefault();

        if (!this.classList.contains("active")) {
          allDropdown.forEach((i) => {
            const aLink = i.parentElement.querySelector("a:first-child");
            aLink.classList.remove("active");
            i.classList.remove("show");
          });
        }

        this.classList.toggle("active");
        item.classList.toggle("show");
      });
    });

    // SIDEBAR COLLAPSE
    const toggleSidebar = document.querySelector("nav .toggle-sidebar");
    const allSideDivider = document.querySelectorAll("#sidebar .divider");

    if (sidebar) {
      if (sidebar.classList.contains("hide")) {
        allSideDivider.forEach((item) => {
          item.textContent = "-";
        });
        allDropdown.forEach((item) => {
          const a = item.parentElement.querySelector("a:first-child");
          a.classList.remove("active");
          item.classList.remove("show");
        });
      } else {
        allSideDivider.forEach((item) => {
          item.textContent = item.dataset.text;
        });
      }

      if (toggleSidebar) {
        toggleSidebar.addEventListener("click", function () {
          sidebar.classList.toggle("hide");
          if (sidebar.classList.contains("hide")) {
            allSideDivider.forEach((item) => {
              item.textContent = "-";
            });
            allDropdown.forEach((item) => {
              const a = item.parentElement.querySelector("a:first-child");
              a.classList.remove("active");
              item.classList.remove("show");
            });
          } else {
            allSideDivider.forEach((item) => {
              item.textContent = item.dataset.text;
            });
          }
        });
      }
      
      sidebar.addEventListener("mouseleave", function () {
        if (this.classList.contains("hide")) {
          allDropdown.forEach((item) => {
            const a = item.parentElement.querySelector("a:first-child");
            a.classList.remove("active");
            item.classList.remove("show");
          });
          allSideDivider.forEach((item) => {
            item.textContent = "-";
          });
        }
      });

      sidebar.addEventListener("mouseenter", function () {
        if (this.classList.contains("hide")) {
          allDropdown.forEach((item) => {
            const a = item.parentElement.querySelector("a:first-child");
            a.classList.remove("active");
            item.classList.remove("show");
          });
          allSideDivider.forEach((item) => {
            item.textContent = item.dataset.text;
          });
        }
      });
    } else {
      console.error("Sidebar element not found.");
    }

    // PROFILE DROPDOWN
    const profile = document.querySelector("nav .profile");
    if (profile) {
      const imgProfile = profile.querySelector("img");
      const dropdownProfile = profile.querySelector(".profile-link");

      if (imgProfile && dropdownProfile) {
        imgProfile.addEventListener("click", function (e) {
          e.stopPropagation(); // Prevent the window click event
          dropdownProfile.classList.toggle("show");
        });
      } else {
        console.error("Profile image or dropdown not found.");
      }

      window.addEventListener("click", function (e) {
        if (!profile.contains(e.target)) {
          dropdownProfile.classList.remove("show");
        }
      });
    } else {
      console.error("Profile element not found.");
    }

    // MENU
    const allMenu = document.querySelectorAll("main .content-data .head .menu");
    allMenu.forEach((item) => {
      const icon = item.querySelector(".icon");
      const menuLink = item.querySelector(".menu-link");

      if (icon) {
        icon.addEventListener("click", function () {
          menuLink.classList.toggle("show");
        });
      } else {
        console.error("Menu icon not found.");
      }
    });

    window.addEventListener("click", function (e) {
      allMenu.forEach((item) => {
        const icon = item.querySelector(".icon");
        const menuLink = item.querySelector(".menu-link");

        if (icon && e.target !== icon && !menuLink.contains(e.target)) {
          menuLink.classList.remove("show");
        }
      });
    });

    // PROGRESSBAR
    const allProgress = document.querySelectorAll("main .card .progress");
    allProgress.forEach((item) => {
      item.style.setProperty("--value", item.dataset.value);
    });

    new DataTable("#example");
    new DataTable("#example1");
  });

  function showImage() {
    // Get the actual image element
    var actualImage = document.getElementById("actualImage");

    // Replace the placeholder image source with the actual image source
    actualImage.src = "path/to/your/image.jpg";

    // Display the image container
    var imageContainer = document.getElementById("imageContainer");
    imageContainer.style.display = "block";
  }
})();