function popup(ul, form, amount) {
    var text = document.getElementById(amount).value;
    if (document.getElementById(ul).getElementsByTagName('li').length == 1) {
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
                  icon:  "warning",
                });
            }
        });
    } else if (document.getElementById(ul).getElementsByTagName('li').length >= 1) {
        swal("Error", "Please choose only a single payee.");
    } else {
        swal("Error", "Please choose at least one payee.");
    }
}

function add(search, user) {
    var text = document.getElementById(search).value;
    var list = document.createElement("li");
    var textnode = document.createTextNode(text);
    var input = document.createElement("input");
    input.setAttribute("type", "hidden");
    input.setAttribute("name", user);
    input.setAttribute("value", text);
    list.appendChild(input);
    list.appendChild(textnode);
    list.setAttribute('class', 'pr-5');
    document.getElementById(user).appendChild(list);
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
