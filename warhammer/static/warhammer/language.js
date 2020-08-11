// change language of 'static' tags
let language_switch = document.getElementById("language_switch");
let PL_flag = document.getElementById("PL_flag");
let ENG_flag = document.getElementById("ENG_flag");
let modal = document.getElementById("englishModal");
language_switch.addEventListener('click', click_switch_language);


function switch_display_language(){
    swap_flags();

    let objects = document.querySelectorAll("[data-en]");
    for (let i=0; i<objects.length; i++){
        let temp = objects[i].innerText;
        objects[i].innerText = objects[i].dataset.en;
        objects[i].dataset.en = temp;
    }

     let inputs = document.querySelectorAll("[data-placeholder]")
     for (let i=0; i<inputs.length; i++){
        let temp = inputs[i].placeholder;
        inputs[i].placeholder = inputs[i].dataset.placeholder;
        inputs[i].dataset.placeholder = temp;
    }
}

function click_switch_language(){
    // cant use booleans in local storage???
    if (localStorage.english == 'true'){
        localStorage.english = 'false';

    } else {
        localStorage.english = 'true';
        $('#englishModal').modal();
    }
    switch_display_language();
}

function swap_flags(){
    if (localStorage.english == 'true'){
        PL_flag.style.display = 'none';
        ENG_flag.style.display = 'block';
    } else {
        PL_flag.style.display = 'block';
        ENG_flag.style.display = 'none';
    }
}

if (localStorage.english=='true'){
    switch_display_language();
}
