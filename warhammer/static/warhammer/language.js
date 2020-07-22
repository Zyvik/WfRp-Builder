// change language of 'static' tags
let language_switch = document.getElementById("language_switch"); // right now its a button
language_switch.addEventListener('click', switch_language);

function switch_language(){
    let objects = document.querySelectorAll("[data-en]");
    for (let i=0; i<objects.length; i++){
        let temp = objects[i].innerText;
        objects[i].innerText = objects[i].dataset.en;
        objects[i].dataset.en = temp;
    }
}
