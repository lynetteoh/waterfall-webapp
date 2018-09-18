
/* Produces a popup confirmation for withdrawals and deposits. */
function popup(isWithdraw){
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
      swal({
        title: "Success!",
        text:  "The transaction has been processed.",
        icon:  "success",
      });
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

/* To remove if not going to allow edit card functions. */
// function editCard() {
//   if (document.getElementById("card-form").style.display == "none") {
//     document.getElementById("card-form").style.display = "block"
//   } else {
//     document.getElementById("card-form").style.display = "none"
//   }
// }
