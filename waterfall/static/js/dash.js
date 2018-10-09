function checkError(error) {
  console.log("Checking error : " + error)
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
function reqPopup(is_approve) {
  swal({
    title: "Are you sure?",
    text:  "Once processed, this action cannot be undone.",
    icon:  "warning",
    buttons: true,
  }).then((confirmed) => {
    if (confirmed) {
      if (is_approve) {
        document.getElementById("approve-req-form").submit();
      } else {
        document.getElementById("delete-req-form").submit();
      }
    }
  });
}
