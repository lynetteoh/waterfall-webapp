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
                swal({
                    title: "Success!",
                    text: "The transaction has been sent.",
                    icon: "success",
                }).then((post) => {
                    document.getElementById(form).submit();
                });
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

function add(search, user) {

    var text = document.getElementById(search).value;
    var list = document.createElement("li");
    var textnode = document.createTextNode(text);
    var input = document.createElement("input");
    var ul_len = document.getElementById(user).childNodes.length
    input.setAttribute("type", "hidden");
    input.setAttribute("name", user + ul_len);
    input.setAttribute("id", user + ul_len);
    input.setAttribute("value", text);
    list.appendChild(input);
    list.appendChild(textnode);
    list.setAttribute('class', 'pr-5');
    var result = 0
    
    // make sure same payee is not chosen
    if(search == 'req_search'){
        var ul = document.getElementById(user)
        for (var i = 0; i < ul.childNodes.length; i++) {
            if (ul.childNodes[i].nodeName == "LI") {
                //get the input html element
                var input = ul.childNodes[i].getElementsByTagName("INPUT")[0]
                console.log(input)
                //get the html element value
                var x = input.attributes[3].value;
                console.log(x)
                if(x == text) {
                    swal("You have chosen the same payee !");
                    result = 1
                    break
                }
            }
        }

    }else {
        var ul = document.getElementById(user)
        for (var i = 0; i < ul.childNodes.length; i++) {
            if (ul.childNodes[i].nodeName == "LI") {
                var input = ul.childNodes[i].getElementsByTagName("INPUT")[0]
                console.log(input)
                var x = input.attributes[3].value;
                console.log(x)
                if(x == text) {
                    swal("You have chosen the same payee !");
                    result = 1
                    break
                }
            }
        }
    } 
    if (result == 0) {
        document.getElementById(user).appendChild(list);
    }
    remove = removeBtn();
    list.appendChild(remove);
    remove.onclick = function () {
        document.getElementById(user).removeChild(list);
    }
}

function removeBtn() {
    var btn = document.createElement("a");
    btn.innerHTML = '<i class="fa fa-trash" aria-hidden="true"></i>';
    btn.setAttribute('class', 'ml-2');
    return btn;
}

function validateForm(ul, amnt, d, form) {

    //validate date
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
    console.log(day)
    console.log(month)
    console.log(year)
    if (parseInt(day, 10) > 31 || parseInt(day, 10) <= 0) {
        return "Please ensure you have a valid day and follow the YYYY-MM-DD format."
    }

    if (parseInt(month, 10) > 12 || parseInt(month, 10) <= 0) {
        return "Please ensure you have a valid month and follow the YYYY-MM-DD format."
    }

    var dt = new Date();
    if (parseInt(year, 10) < dt.getFullYear() || parseInt(month, 10) < dt.getMonth() || parseInt(day, 10) < dt.getDate()) {
        return "The date has passed."
    }


    //validate amount
    var amount = document.getElementById(amnt).value;
    if (parseFloat(amount) <= 0) {
        return "Please only input positive numeric amounts."
    }

    if (form != 'req-form') {
        //validate payee
        if (document.getElementById(ul).getElementsByTagName('li').length == 1) {
            return "";
        } else if (document.getElementById(ul).getElementsByTagName('li').length >= 1) {
            return "Please choose only a single payee !";
        } else {
            return "Please choose a payee !";
        }
    }else {
        if (document.getElementById(ul).getElementsByTagName('li').length >= 1) {
            return "";
        } else {
            return "Please choose a payee !";
        }
    }
}

function update_value(){
    
}
