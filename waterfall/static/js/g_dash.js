
function checkError(error) {
  if (error == "Success") {
    swal({
      title: "Success!",
      text:  "Your request has been processed.",
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

/* Produces a popup confirmation for withdrawals and deposits. */
function balancePopup(isWithdraw) {
  var id = isWithdraw ? "minus-amount" : "add-amount";
  var amount = document.getElementById(id).value;
  if (!validAmount(amount)) return;
  var text = isWithdraw ? "Withdrawing $" + amount + "?"
                        : "Depositing $" + amount + "?";
  swal({
    title: text,
    text:  "Once processed, this action cannot be undone.",
    icon:  "warning",
    buttons: true,
  }).then((confirmed) => {
    if (confirmed) {
      if (isWithdraw) {
        document.getElementById("withdraw").submit();
      } else {
        document.getElementById("deposit").submit();
      }
    }
  });
}

/* Ensures withdraw/deposit amounts are positive values. */
function validAmount(txt) {
  if (isNaN(txt) || parseFloat(txt) <= 0) {
    swal({
      title: "Invalid Amount",
      text:  "Please only input positive numeric amounts.",
      icon:  "warning",
    });
    return false;
  }
  return true;
}
