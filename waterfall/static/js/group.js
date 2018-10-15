//add member to group
function add_member(search, users) {
    // Get text from search bar
    var text = document.getElementById(search).value;
    var valid_user = 0;
    // Check if member is a valid user
    valid_user = check_member(text);
    if (valid_user == 0) {
        swal({
            title: "Invalid User",
            text: "Please try again.",
            icon: "warning",
        });
        return;
    }

    var result = 0;
    result = exist(search, users, text);

    if (result == 0) {
        add(text, users);
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
                swal({
                    title: "Invalid Selection",
                    text: "You have selected the same user twice.",
                    icon: "warning",
                });
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
        if(form == 'group-creation-form') {
            swal({
                title: "Creating New Group",
                text: "Are you sure?",
                icon: "warning",
                buttons: true,
                dangerMode: true,
            }).then((confirmed) => {
                if (confirmed) {
                    document.getElementById(form).submit();
                    window.location.replace(group_list);
                } else {
                    swal({
                        title: "Cancelled",
                        text: "Group creation cancelled",
                        icon: "warning",
                    });
                }
            });
        } else {
            swal({
                title: "Are you sure?",
                text: "Once changes have been saved, they cannot be undone.",
                icon: "warning",
                buttons: true,
                dangerMode: true,
            }).then((confirmed) => {
                if (confirmed) {
                    document.getElementById(form).submit();
                } else {
                    swal({
                        title: "Cancelled",
                        text: "Your changes have not been saved.",
                        icon: "warning",
                    });
                }
            });
        }

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
    input.setAttribute("value", user);

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

    for (var i = 0; i < users.length; i++) {
        add(users[i], members)
    }

}

function add(user, members) {
    var list = document.createElement("li");
    var textnode = document.createTextNode(user);
    var ul_len = document.getElementById(members).childNodes.length;

    // create input element
    var input = document.createElement("input");
    input.setAttribute("type", "hidden");
    input.setAttribute("name", members + ul_len);
    input.setAttribute("id", members + ul_len);
    input.setAttribute("value", user);
    list.appendChild(input);
    list.appendChild(textnode);
    list.setAttribute('class', 'pr-5');

    // add remove button
    var remove = removeBtn();
    list.appendChild(remove);
    document.getElementById(members).appendChild(list);
    remove.onclick = function () {
        console.log(list);
        document.getElementById(members).removeChild(list);
    }
}

function leave_group(form) {
    swal({
        title: "Leaving Group",
        text: "Are you sure?",
        icon: "warning",
        buttons: true,
        dangerMode: true,
    }).then((confirmed) => {
        if (confirmed) {
            document.getElementById(form).submit();
            window.location.replace(group_list);
        } else {
            swal({
                title: "Cancelled",
                text: "You have not left the group.",
                icon: "warning",
            });
        }
    });
}

function cancel_changes(link) {
    swal({
        title: "Cancel Changes?",
        text: "Your changes have not been saved.",
        icon: "warning",
        buttons: true,
        dangerMode: true,
    }).then((confirmed) => {
        if (confirmed) {
            window.location.replace(link);
        }
    });
}
