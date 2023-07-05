"use strict"

export function sayHi(user) {
    var msg = "Hello~ ${user}";
    console.log(msg)
    alert(msg);
}

export function sayBye(user) {
    alert("Bye~ ${user}");
}
