function roll(btn_id){
    const input_id ="id"+btn_id;
    const bonus = document.getElementById(btn_id).value;
    let roll = 0;
    for (let i = 0; i < bonus; i++){
        roll += Math.floor(Math.random() * 10 ) + 1;
        }
    document.getElementById((input_id.toLocaleLowerCase()).replace('ż', 'z')).value=roll;
}

function roll_profession() {
    const input = document.getElementById('id_prof');
    const roll = Math.floor(Math.random()*100) + 1;
    input.value = roll;
}