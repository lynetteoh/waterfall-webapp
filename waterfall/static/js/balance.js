
function checkError(error) {
  if (error == "Success") {
    swal({
      title: "Success!",
      text:  "The transaction has been sent.",
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

    var patt = /^\d+(\.\d{1,2})?$/;
    var result = patt.test(txt);
    
    if (isNaN(txt) || !result || txt <= 0) {
    swal({
      title: "Invalid Amount",
      text:  "Please only input positive numeric amounts.",
      icon:  "warning",
    });
    return false;
  }
  return true;
}
