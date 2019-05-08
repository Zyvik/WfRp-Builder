 function roll(btn_id){
        input_id ="id"+btn_id;
        var bonus = document.getElementById(btn_id).value;
        var i,roll;
        roll = 0;
        for (i = 0; i < bonus; i++){
            roll += Math.floor(Math.random() * 10 +1);
            }
        document.getElementById(input_id).value=roll;
        }

    function profesja(){
        var xD = document.getElementsByClassName('xD');
        for (i=0; i < xD.length; i++){
            xD[i].style.display='none'
        }

        var roll = Math.floor(Math.random() * 100 +1);
        var prof = '';
        if (roll>1){
            prof = 'a';
        }
        if (roll>50) {
            prof = 'b';
        }
        document.getElementById(prof).style.display='block';

        }

    function validate(){
        // validate 2-20 rolls
        var inputs = ['WW','US','ZR','K','Int','Ogd','SW'];
        var is_valid = true;
        var stat,stat_value;
        for (i=0; i<inputs.length;i++){
            stat = document.getElementById('id_'+inputs[i]);
            stat_value = parseInt(stat.value);

            if (stat_value<2 || stat_value>20){
                stat.className += ' is-invalid';
                is_valid = false;
            }
            else{
                stat.className = stat.className.replace(" is-invalid","" );
            }
        }
        // validate 1-10 rolls
        inputs = ['Żyw','PP']
        for (i=0; i<inputs.length;i++){
        stat = document.getElementById('id_'+inputs[i]);
        stat_value = parseInt(stat.value);

            if (stat_value<1 || stat_value>10){
                stat.className += ' is-invalid';
                is_valid = false;
            }
            else{
                stat.className = stat.className.replace(" is-invalid","" );
            }
        }
        // validate 1-100
        V = document.getElementById('id_PROF');
        val = parseInt(V.value);
        if (val<1 || val>100){
            V.className += ' is-invalid';
            is_valid = false
        }


        if (is_valid == false){
        return false;
        }
        else{

        return true;}
    }

function validateRAND(){
    var inputs = ['0_random_ability','1_random_ability'];
    var is_valid = true;
    for (i=0; i<inputs.length;i++){
        roll = document.getElementById(inputs[i]);
        if (!roll){
            return true;
        }
        roll_value = parseInt(roll.value);

        if (roll_value < 1 || roll_value>100){
            roll.className += ' is-invalid';
            is_valid = false;
            return false;
        }

        }
        return true;
    }
function roll_ability(value){
    var input = document.getElementById(value+'_random_ability')
    input.value = Math.floor(Math.random() * 100) + 1;
}

function roll_profession(){
    document.getElementById('id_PROF').value = Math.floor(Math.random() * 100) + 1;
}

function roll_coins()
{   var x = Math.floor(Math.random()*10) + 1
    var y = Math.floor(Math.random()*10) +1
    document.getElementById('coins').value = x+y

}
function toggle_stats()
{
    var table_basic = document.getElementById('table_basic');
    var table_secondary = document.getElementById('table_secondary');
    var form_basic = document.getElementById('form_basic');
    var form_secondary = document.getElementById('form_secondary');
    var form_footer = document.getElementById('form_footer');
    var form_alert = document.getElementById('form_alert');
    var toggle_button = document.getElementById('stats_toggle_button')


    if (document.getElementById('form_basic').style.display == 'none')
    {
        table_basic.style.display = 'none';
        table_secondary.style.display = 'none';
        form_basic.style.display = 'block';
        form_secondary.style.display = 'block';
        form_footer.style.display = 'block';
        form_alert.style.display ='block';

        stats_toggle_button.className = 'btn btn-danger float-right';
        stats_toggle_button.innerHTML = 'Anuluj'


    }
    else
    {
        form_footer.style.display = 'none';
        form_alert.style.display ='none';
        form_basic.style.display = 'none';
        form_secondary.style.display = 'none';
        table_basic.style.display = 'block';
        table_secondary.style.display = 'block';

        stats_toggle_button.className = 'btn btn-secondary float-right';
        stats_toggle_button.innerHTML = 'Edytuj'
    }

}

function toggle_eq()
{
    var eq_toggle_button = document.getElementById("eq_toggle_button");
    var display_eq = document.getElementById('display_eq');
    var form_eq = document.getElementById('form_eq');
    var eq_footer = document.getElementById('eq_footer');

    if (form_eq.style.display=='none')
    {
        eq_toggle_button.className = 'btn btn-danger float-right';
        eq_toggle_button.innerHTML = 'Anuluj';

        display_eq.style.display = 'none';
        form_eq.style.display ='block';
        eq_footer.style.display = 'block';
    }
    else
    {
        eq_toggle_button.className = 'btn btn-secondary float-right';
        eq_toggle_button.innerHTML = 'Edytuj';

        display_eq.style.display = 'block';
        form_eq.style.display ='none';
        eq_footer.style.display = 'none';
    }
}

function toggle_skills()
{
    var skills_toggle_button = document.getElementById('skills_toggle_button');
    var display_skills = document.getElementById('display_skills');
    var form_skills = document.getElementById('form_skills');

    if (form_skills.style.display == 'none')
    {
        skills_toggle_button.className = 'btn btn-danger float-right';
        skills_toggle_button.innerHTML = 'Anuluj';

        display_skills.style.display = 'none';
        form_skills.style.display = 'block';
    }
    else
    {
        skills_toggle_button.className = 'btn btn-secondary float-right';
        skills_toggle_button.innerHTML = 'Edytuj';

        display_skills.style.display = 'block';
        form_skills.style.display = 'none';
    }
}

function toggle_abilities()
{
    var skills_toggle_button = document.getElementById('abilities_toggle_button');
    var display_skills = document.getElementById('display_abilities');
    var form_skills = document.getElementById('form_abilities');

    if (form_skills.style.display == 'none')
    {
        skills_toggle_button.className = 'btn btn-danger float-right';
        skills_toggle_button.innerHTML = 'Anuluj';

        display_skills.style.display = 'none';
        form_skills.style.display = 'block';
    }
    else
    {
        skills_toggle_button.className = 'btn btn-secondary float-right';
        skills_toggle_button.innerHTML = 'Edytuj';

        display_skills.style.display = 'block';
        form_skills.style.display = 'none';
    }
}