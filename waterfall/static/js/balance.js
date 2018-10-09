
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

/* Confirms card details and gives relevant message. */
function checkCard() {
  var error = validateCard();
  if (!error) {
    swal({
      title: "Success!",
      text:  "Your card details have been updated.",
      icon:  "success",
    })
    return;
  }
  swal({
    title: "Card Validation Failed",
    text:  error,
    icon:  "warning",
  });
}

/* Validates card details and returns error message. */
function validateCard() {
  console.log("validating card");
  // Validate CCV
  var ccv = document.getElementById("ccv").value;
  ccv = ccv.replace(/\D/g,'');
  if (isNaN(ccv) || ccv.length != 3) {
    return "Please ensure you have a valid CCV number.";
  }

  // Validate expiry
  var expiry = document.getElementById("expiry").value;
  var expiryData = expiry.split("/");
  if (expiryData.length != 2) {
    return "Please ensure you use the correct MM/YYYY format for card expiry."
  }

  var month = expiryData[0];
  var year = expiryData[1];
  month = month.replace(/\D/g,'');
  year = year.replace(/\D/g, '');
  if (parseInt(month, 10) > 12 || parseInt(month, 10) <= 0) {
    return "Please ensure you have a valid expiry month."
  }
  if (year.length != 4 || parseInt(year, 10) < new Date().getFullYear()) {
    return "Your credit card has expired."
  }

  // Validate card number.
  var cardnum = document.getElementById("cardnum").value;
  if (isNaN(cardnum) || cardnum.length != 16) {
    return "Please ensure you have the correct card number."
  }
  return "";
}
