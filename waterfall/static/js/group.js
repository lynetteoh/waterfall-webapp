//add member to group
function add_member(search, users) {
    //get text from search bar
    var text = document.getElementById(search).value;
    var valid_user = 0;
    //check if member is a valid user
    valid_user = check_member(text);
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
    var ul_len = document.getElementById(users).childNodes.length;

    // create input element
    var input = document.createElement("input");
    input.setAttribute("type", "hidden");
    input.setAttribute("name", users + ul_len);
    input.setAttribute("id", users + ul_len);
    input.setAttribute("value", text);
    list.appendChild(input);
    list.appendChild(textnode);
    list.setAttribute('class', 'pr-5');

    var result = 0;
    result = exist(search, users, text);
    if (result == 0) {
        document.getElementById(users).appendChild(list);
    }

    // add remove button
    remove = removeBtn();
    list.appendChild(remove);
    remove.onclick = function () {
        document.getElementById(users).removeChild(list);
    }
}

function exist(search, user, text) {
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
                swal("You have chosen the same payee !");
                result = 1
                break
            }
        }
    }
    return result
}

//create remove button
function removeBtn() {
    var btn = document.createElement("a");
    btn.innerHTML = '<i class="fa fa-trash" aria-hidden="true"></i>';
    btn.setAttribute('class', 'ml-2');
    return btn;
}

function check_member(user) {
    users = f_members.split("&#39;");
    // Removes the [] parantheses.
    users.splice(0, 1);
    users.pop();

    // Removes all comma values.
    for (var i = users.length - 1; i--;) {
        if (users[i].match(",")) users.splice(i, 1);
    }

    console.log(users);
    for (i = 0; i < users.length; i++) {
        if (users[i] == user) {
            return 1;
        }
    }
    return 0;
}

//alert
function popup(members, form) {
    var error = validateForm(members);
    if (!error) {
        swal({
            text: "Create Group ?",
            icon: "warning",
            buttons: true,
            dangerMode: true,
        }).then((confirmed) => {
            if (confirmed) {
                document.getElementById(form).submit();
            } else {
                swal({
                    title: "Cancelled",
                    text: "Group creation has been cancelled",
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

function validateForm(members) {
    // Ensure at least one payee is selected.
    if (document.getElementById(members).getElementsByTagName('li').length >= 1) {
        return "";
    } else {
        return "Please choose at least one member.";
    }
}

//add group creator
function add_creator(members, user) {
    var list = document.createElement("li");
    var textnode = document.createTextNode(user);
    var length = document.getElementById(members).childNodes.length;

    //create input element
    var input = document.createElement("input");
    input.setAttribute("type", "hidden");
    input.setAttribute("name", members + length);
    input.setAttribute("id", members + length);
    input.setAttribute("value", '{{user}}');

    //add input to list
    list.appendChild(input);
    list.appendChild(textnode);
    list.setAttribute('class', 'pr-5');
    document.getElementById(members).appendChild(list);
}

function add_all_members(members) {
    users = g_members.split("&#39;");
    // Removes the [] parantheses.
    users.splice(0, 1);
    users.pop();

    // Removes all comma values.
    for (var i = users.length - 1; i--;) {
        if (users[i].match(",")) users.splice(i, 1);
    }

    for (i = 0; i < users.length; i++) {
        var list = document.createElement("li");
        var textnode = document.createTextNode(users[i]);
        var ul_len = document.getElementById(members).childNodes.length;

        // create input element
        var input = document.createElement("input");
        input.setAttribute("type", "hidden");
        input.setAttribute("name", members + ul_len);
        input.setAttribute("id", members + ul_len);
        input.setAttribute("value", users[i]);
        list.appendChild(input);
        list.appendChild(textnode);
        list.setAttribute('class', 'pr-5');
        document.getElementById(members).appendChild(list);

        // add remove button
        remove = removeBtn();
        list.appendChild(remove);
        remove.onclick = function () {
            document.getElementById(members).removeChild(list);
        }

    }

}

function leave_group() {

}