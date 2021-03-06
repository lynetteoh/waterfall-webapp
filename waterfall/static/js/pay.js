// pop up to show error message for form submission
function checkError(error) {
    console.log("Checking error : " + error)
    if (error == "Success") {
        swal({
            title: "Success!",
            text: "The transaction has been saved.",
            icon: "success",
        });
    } else if (error) {
        swal({
            title: error,
            text: "Please try again.",
            icon: "warning",
        });
    }
}

// pop up to ask for user confirmation for form submission
function popup(ul, form, amount, date) {
    var text = document.getElementById(amount).value;
    var error = validateForm(ul, amount, date, form);
    if (!error) {
        swal({
            title: '$ ' + text,
            text: "Once processed, this action cannot be undone.",
            icon: "warning",
            buttons: true,
            dangerMode: true,
        }).then((confirmed) => {
            if (confirmed) {
                document.getElementById(form).submit();
            } else {
                swal({
                    title: "Cancelled",
                    text: "Your transaction request has been cancelled.",
                    icon: "warning",
                });
            }
        });
    } else {
        swal({
            title: "Process Failed",
            text: error,
            icon: "warning",
        });
    }
}


// add payee to list
function add(search, user, amnt) {

    var text = document.getElementById(search).value;

    //check for valid user
    var valid_user = 0;
    valid_user = check_payee(text);
    if (valid_user == 0) {
        swal({
            title: "Invalid User",
            text: "Please try again.",
            icon: "warning",
        });
        return;
    }
    var list = document.createElement("li");
    var textnode = document.createTextNode(text);
    var ul_len = document.getElementById(user).childNodes.length;
    //create input element
    var input = document.createElement("input");
    input.setAttribute("type", "hidden");
    input.setAttribute("name", user + ul_len);
    input.setAttribute("id", user + ul_len);
    input.setAttribute("value", text);

    //add element to list
    list.appendChild(input);
    list.appendChild(textnode);
    list.setAttribute('class', 'pr-5');

    var result = 0;
    result = exist(user, text);
    if (result == 0) {
        document.getElementById(user).appendChild(list);
        if (user == 'req_users') {
            update_payee(user, text, amnt);
        }
    }else {
        swal("You have chosen the same payee !");
        return;
    }

    //add remove button
    var remove = removeBtn();
    list.appendChild(remove);
    remove.onclick = function () {
        document.getElementById(user).removeChild(list);
        if (user == 'req_users') {
            remove_payee(list);
            update_value(user, amnt);
        }
    }
}

//create remove button
function removeBtn() {
    var btn = document.createElement("a");
    btn.innerHTML = '<i class="fa fa-trash" aria-hidden="true"></i>';
    btn.setAttribute('class', 'ml-2');
    return btn;
}

// validate form before form submission to make sure fields are correct
function validateForm(ul, amnt, d, form) {

    // Ensure at least one payee is selected.
    if (document.getElementById(ul).getElementsByTagName('li').length < 1) {
        return "Please choose at least one payee.";
    }

    // Validate dates.
    var date = document.getElementById(d).value;
    console.log(date)
    date = date.split("-");
    if (date.length != 3) {
        return "Please ensure you use the correct YYYY-MM-DD format."
    }
    var day = date[2];
    var month = date[1];
    var year = date[0];
    day = day.replace(/\D/g, '');
    month = month.replace(/\D/g, '');
    year = year.replace(/\D/g, '');
    if (parseInt(day, 10) > 31 || parseInt(day, 10) <= 0) {
        return "Please ensure you have a valid day and follow the MM-DD-YYYY format."
    }
    if (parseInt(month, 10) > 12 || parseInt(month, 10) <= 0) {
        return "Please ensure you have a valid month and follow the MM-DD-YYYY format."
    }

    var dt = new Date();
    if (parseInt(year, 10) < dt.getFullYear()
        && parseInt(month, 10) < dt.getMonth()
        && parseInt(day, 10) < dt.getDate()) {
        return "The date has passed."
    }

    // Validate amount.
    var amount = document.getElementById(amnt).value;
    if (parseFloat(amount) <= 0) {
        return "Please only input positive numeric amounts."
    }

    // check from_acc != payee
    if (form == 'req-form') {
        var from_acc = document.getElementById('req_from').value;
        var result = exist('req_users',from_acc)
        if(result == 1) {
            return "You are requesting from yourself !"
        }
    } else {
        var from_acc = document.getElementById('pay_from').value;
        var result = exist('pay_users',from_acc)
        if(result == 1) {
            return "You are paying from yourself !"
        }
    }

    // Checks split amounts for a request form.
    if (form == 'req-form') {
        var result = check_split(amount, ul);
        if (result == 1) {
            return "Split amounts do not sum up to requested amount."
        }
    }

    return "";
}

//update value for each payee in summary table
function update_value(users_list, amnt) {
    var extra = 0
    var amount = document.getElementById(amnt).value;
    console.log(amount);
    var ul = document.getElementById(users_list);
    var ul_len = document.getElementById(users_list).childNodes.length;
    console.log(ul_len);
    if (ul_len != 1) {
        var payee_amount = amount / ul_len;
        console.log(payee_amount);
        var floor = Math.floor(payee_amount * 100) / 100
        var split_total = floor * ul_len
        split_total = Math.floor(split_total * 100) / 100
        console.log(split_total);

        // Cases where not everyone would pay equally.
        if (split_total != amount) {
            var remainder = Math.round((amount - split_total) * 100) / 100
            extra = remainder / 0.01
            console.log(extra)
        }

    }else {
        var payee_amount = amount/ul_len;
    }


    for (var i = 0; i < ul.childNodes.length; i++) {
        if (ul.childNodes[i].nodeName == "LI") {
            //get the input html element
            var input = ul.childNodes[i].getElementsByTagName("INPUT")[0]
            //get the html element value
            var text = input.attributes[3].value;
            var input = document.getElementById(text);
            if (i < extra) {
                payee_amount = Math.floor(payee_amount*100) / 100;
                var pay_amount = payee_amount + 0.01
                input.setAttribute('value', pay_amount.toFixed(2));
            } else {
                var pay_amount = Math.floor(payee_amount*100) / 100;
                input.setAttribute('value', payee_amount.toFixed(2));
            }
        }
    }
}

// update payee in summary table
function update_payee(users, text, amnt) {
    show_div();
    var table = document.getElementById("summary_table");
    var amount = document.getElementById(amnt).value;
    var ul_len = document.getElementById(users).childNodes.length;
    var payee_amount = amount / ul_len;
    var row = table.insertRow(1);
    var payee = document.createElement("td");
    var amount = document.createElement("td");
    var textnode = document.createTextNode(text);

    //create label
    var label = document.createElement("label");
    label.setAttribute('for', text);
    label.setAttribute('class', 'col-sm-2 col-form-label');
    label.appendChild(textnode);

    //create input
    var input = document.createElement("input");
    input.setAttribute("name", text);
    input.setAttribute("value", payee_amount);
    input.setAttribute('id', text);
    input.setAttribute('class', 'form-control col-sm-7');

    //add to row in table
    row.setAttribute('id', "row_" + text);
    payee.appendChild(label);
    amount.appendChild(input);
    row.appendChild(payee);
    row.appendChild(amount);
}

// check if the split is correct
function check_split(amount, users_list) {
    sum = 0
    var ul = document.getElementById(users_list);
    for (var i = 0; i < ul.childNodes.length; i++) {
        if (ul.childNodes[i].nodeName == "LI") {
            //get the input html element
            var input = ul.childNodes[i].getElementsByTagName("INPUT")[0]
            //get the html element value
            var text = input.attributes[3].value;
            var input = document.getElementById(text);
            var val = input.value;
            val = parseFloat(val, 10)
            sum += val;
        }
    }
    return (sum != amount) ? 1 : 0;
}

// check if the selected user is chosen already
function exist(user, text) {
    result = 0
    // make sure same payee is not chosen
    var ul = document.getElementById(user)
    for (var i = 0; i < ul.childNodes.length; i++) {
        if (ul.childNodes[i].nodeName == "LI") {
            var input = ul.childNodes[i].getElementsByTagName("INPUT")[0]
            console.log(input);
            var x = input.attributes[3].value;
            console.log(x);
            if (x == text) {
                result = 1
                break
            }
        }
    }
    return result
}

//remove payee from list
function remove_payee(list) {
    var input = list.getElementsByTagName("INPUT")[0]
    //get the html element value
    var text = input.attributes[3].value;
    text = "row_" + text;
    var row = document.getElementById(text);
    //remove the html element
    row.parentNode.removeChild(row);
}

// update total in summary table
function update_total(amnt, summary_total) {
    var amount = document.getElementById(amnt).value
    var total = document.getElementById(summary_total)
    total.setAttribute('value', amount);
}

// show hidden div
function show_div() {
    var x = document.getElementById("summary");
    if (x.style.display === "none") {
        x.style.display = "block";
    }
}

// check if valid user is selected
function check_payee(user) {
    users = f_users.split("&#39;");
    // Removes the [] parantheses.
    users.splice(0, 1);
    users.pop();

    // Removes all comma values.
    for (var i = users.length - 1; i--;) {
        if (users[i].match(",")) users.splice(i, 1);
    }

    for (i = 0; i < users.length; i++) {
        if (users[i] == user) {
            return 1;
        }
    }
    return 0;
}
