function checkError(error) {
  if (error == "Success") {
    swal({
      title: "Success!",
      text:  "The changes have been saved.",
      icon:  "success",
    });
  } else if (error) {
    swal({
      title: error,
      text:  "Please try again.",
      icon:  "warning",
    });
  }
}

/* Produces a popup confirmation for request approvals and rejections. */
function confirmPopup(form_id) {
  swal({
    title: "Are you sure?",
    text:  "Once processed, this action cannot be undone.",
    icon:  "warning",
    buttons: true,
  }).then((confirmed) => {
    if (confirmed) {
      document.getElementById(form_id).submit();
    }
  });
}
