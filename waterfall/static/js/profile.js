function editProfile() {
    if (document.getElementById("change-settings").style.display === "none") {
      enableProfileForm()
    } else {
      disableProfileForm()
    }
}

function disableProfileForm() {
  // Disable all the edit profile form.
  var form = document.forms["edit-form"].getElementsByTagName('input');
  for (var i = 0; i < form.length; ++i) {
    form[i].setAttribute('readonly', true);
  }
  // Disable profile settings edit.
  document.getElementById("upload-pic").style.display = "none"
  document.getElementById("change-settings").style.display = "none"
}

function enableProfileForm() {
  // Enable form editing of existing profile data.
  var form = document.forms["edit-form"].getElementsByTagName('input');
  for (var i = 0; i < form.length; ++i) {
    form[i].removeAttribute('readonly');
  }
  // Enable profile settings editds.
  document.getElementById("upload-pic").style.display = "block"
  document.getElementById("change-settings").style.display = "block"
}
