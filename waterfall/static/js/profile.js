/* Confirms profile change and gives relevant error alerts. */
function checkForm() {
  var error = validateForm();
  if (!error) {
    swal({
      title: "Success!",
      text:  "Your profile details have been updated.",
      icon:  "success",
    }).then((post) => {
      document.getElementById("edit-form").submit();
    });
    return;
  }
  swal({
    title: "Error",
    text:  error,
    icon:  "warning",
  });
}

/* Validates profile form entries, returning error messages. */
function validateForm() {
  var regex = new RegExp("[^A-Za-z0-9' ]+");
  var fname = document.getElementById("first_name").value;
  var lname = document.getElementById("last_name").value;
  if (!fname || regex.test(fname) || !lname || regex.test(lname)) {
    return "Please ensure names contain only alphabets."
  }

  // Validate password.
  var pw = document.getElementById("password").value;
  var pw2 = document.getElementById("password2").value;
  if (pw != pw2) {
    return "Please ensure you verify the right password."
  }
  // TODO if pw field is empty, send back old pw
  return "";
}

/* Enables and disables profile editing on clicks. */
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
  document.getElementById("change-settings").style.display = "none"
}

function enableProfileForm() {
  // Enable form editing of existing profile data.
  var form = document.forms["edit-form"].getElementsByTagName('input');
  for (var i = 0; i < form.length; ++i) {
    form[i].removeAttribute('readonly');
  }
  // Enable profile settings editds.
  document.getElementById("change-settings").style.display = "block"
}

/* Enables and disables profile editing on clicks. */
function editAvatar() {
  if (document.getElementById("upload-pic").style.display === "none") {
    document.getElementById("avatar-text").innerText = "Keep Avatar"
    document.getElementById("upload-pic").style.display = "block"
  } else {
    document.getElementById("avatar-text").innerText = "Change Avatar"
    document.getElementById("upload-pic").style.display = "none"
  }
}
