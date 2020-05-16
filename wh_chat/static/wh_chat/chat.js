//RIGHT SIDEBAR
$(document).ready(function () {
    $("#sidebar").mCustomScrollbar({
        theme: "minimal"
    });

    $('#dismiss-right').on('click', function () {
        chat_bool=toggleAPI(chat_bool,map_bool);
        $('#sidebar').removeClass('active');
    });

    $('#sidebarCollapse').on('click', function () {
        chat_bool=toggleAPI(chat_bool,map_bool);
        $('#sidebar').toggleClass('active');
        $('.collapse.in').toggleClass('in');
        $('a[aria-expanded=true]').attr('aria-expanded', 'false');
    });
});

//LEFT SIDEBAR
$(document).ready(function () {
    $("#sidebar-left").mCustomScrollbar({
        theme: "minimal"
    });

    $('#dismiss-left').on('click', function () {
        map_bool=toggleAPI(map_bool,chat_bool);
        $('#sidebar-left').removeClass('active');
    });

    $('#sidebarCollapse-left').on('click', function () {
        map_bool=toggleAPI(map_bool,chat_bool);
        $('#sidebar-left').toggleClass('active');
        $('.collapse.in').toggleClass('in');
        $('a[aria-expanded=true]').attr('aria-expanded', 'false');
    });
});

// On load
const host = window.location.host;
const game_id = 1;
const game_url = 'http://' + host + '/warhammer/chat/' + game_id;
const chat_box = document.getElementById('chat_box');
let message_counter = 0;
let map_state = "foobar";
let map_bool = false;
let chat_bool = false;
let reload_messages;


//checks if sidebars are open and sets interval accordingly
function toggleAPI(clicked_bool, other_bool){
    clicked_bool = !clicked_bool;
    if (clicked_bool && other_bool){
        // do nothing because interval has been already set
    } else if (clicked_bool || other_bool){
        if (clicked_bool){
            get_message();
            reload_messages = setInterval(get_message, 4000);
        }
    } else {
        clearInterval(reload_messages);
    }
    return clicked_bool;
}

//contrary to name - it also gets map
function get_message(){
        let Httpreq = new XMLHttpRequest();
        Httpreq.open("GET", game_url, true);
        Httpreq.onload = function(){
            let json = JSON.parse(Httpreq.responseText);
            let json_map = json.map;
            json = json.chat;
            let i;

            // if there are new messages - refresh chat
            if(json[0].pk != message_counter){
                chat_box.innerHTML = ' ';
                for (i = 0; i < json.length; i++){
                    if (json[i].message.includes("Sukces!")){
                        chat_box.innerHTML += "<li class='list-group-item text-body' style='background-color:#caeebe;'>" + json[i].author + "<br>" + json[i].message + '</li>';
                    }else if(json[i].message.includes("Porażka!")){
                        chat_box.innerHTML += "<li class='list-group-item text-body' style='background-color:#ed5050 ;'>" + json[i].author + "<br>" + json[i].message + '</li>';
                    }else {
                        chat_box.innerHTML += "<li class='list-group-item text-body'>" + json[i].author + "<br>" + json[i].message + '</li>';
                    }
                }
            message_counter = json[0].pk;
            }

            // if there is change in map - refresh
            if (json_map.map != map_state){
                refresh_map(json_map.map);
                map_state = json_map.map;
            }

        };
  Httpreq.send();
}

//sends provided message and refreshes chat
function send_message(message, type){
    let post_data = {};
    let author = document.getElementById("Name").innerHTML.replace("Nazwa: ", "");
    let Httpreq = new XMLHttpRequest();
    if (type=='roll') {
        Httpreq.open("POST", game_url, true);
        post_data = {"author":author,"message":message, "game":game_id};
    } else {
        Httpreq.open("PUT", game_url, true);
        post_data = {"map":message, "game":game_id};
    }

    Httpreq.setRequestHeader("Content-Type", "application/json");

    Httpreq.onload = function (){
      clearInterval(reload_messages);
      get_message();
      reload_messages = setInterval(get_message, 4000);
    };

    Httpreq.send(JSON.stringify(post_data));
}

//rolls 1 die
function roll(d){
   var x = Math.floor(Math.random()*d)+1;
   var string = "1k" + d.toString() + ": <strong>" + x.toString()+"</strong>";
   send_message(string, "roll");
}

//roll - n:number of dice, d: number of die sides
function roll_custom(){
    var n = parseInt(document.getElementById('n').value);
    var d = parseInt(document.getElementById('d').value);
    var bonus = parseInt(document.getElementById('roll_bonus').value)

    if (n > 0 && d > 0 && n <= 1000 && d<=1000 ){
      let i;
      var sum = 0;
      // prepare bonus string
      var bonus_string ='';
      if (bonus && !isNaN(bonus)){
        if (bonus>0){
            bonus_string = ' + ';
        }
        else{
            bonus_string = ' - '
        }
        bonus_string +=  Math.abs(bonus);
        sum = bonus;
      }
    //create string to send
      var string = n.toString() + "k"+ d.toString() + bonus_string + ": " + "<strong>" + "suma" + "</strong><br>(";
      // roll and calculate sum
      let x;
      for (i=0; i<n; i++){
        x = Math.floor(Math.random()*d)+1;
        sum += x;
        string += x.toString() + " + ";
      }
      string = string.substring(0, string.length-3)+")"+bonus_string;
      string = string.replace("suma",sum.toString());


      send_message(string, "roll");
  }
}
//rolls, checks for success, for WW and US check location of hit
function roll_stat(short){
    var stat = document.getElementById(short).innerHTML;
    var stat_val = parseInt(stat);
    var short = short.replace("R_","");

    // rolls
    var roll = Math.floor(Math.random()*100)+1;
    var string = "<strong>" + short+": "+ roll.toString()+"</strong> "; //ex. WW: 75

    //checks for success
    if (stat_val >= roll){
       string += "<br><strong>" + "Sukces! (+" + (stat_val-roll).toString() +")"; //ex. WW: 30 Sukces (14)
    }
    else {
        string += "<br><strong>" + "Porażka! (" + (stat_val-roll).toString() +")";
    }

    //checks location of hit
    if (short=="WW" || short=="US"){
        roll = "0" + roll; //in case of 1 digit roll
        var flipped_roll = roll.charAt(roll.length-1) + roll.charAt(roll.length-2);
        flipped_roll = parseInt(flipped_roll);
        console.log(flipped_roll);

        //tabelka :)
        if (flipped_roll < 16){
            string += " (" + "Głowa" + ")</strong>";
        } else if (flipped_roll < 36){
            string += " (Prawe ramię)</strong>";
        } else if (flipped_roll < 56){
            string += " (Lewe ramię)</strong>";
        } else if (flipped_roll < 81){
            string += " (Korpus)</strong>";
        } else if (flipped_roll < 91){
            string += " (Prawa noga)</strong>";
        } else{
            string += " (Lewa noga)</strong>";
        }
    }
    send_message(string, "roll");
}

function roll_initiative(){
    var dexterity = parseInt(document.getElementById('R_ZR').innerHTML);
    var roll = Math.floor(Math.random()*10)+1;
    var string = 'Inicjatywa: <strong>'+ (dexterity+ roll).toString() + '</strong><br>('+ dexterity.toString()+ '+' + roll.toString() + ')';
    send_message(string, "roll");

}

//#######################MAP###########################
    var token_nr = 14;
const empties = document.querySelectorAll('.empty');
    var picked;
    // Adds eventListeners for map
    for(const empty of empties){
        empty.addEventListener('dragover',dragOver);
        empty.addEventListener('dragenter',dragEnter);
        empty.addEventListener('dragleave',dragLeave);
        empty.addEventListener('drop',dragDrop);
    }

    //Gets images for tokens (last one is empty - trash);
    var tokens = [];
    for (var i=0; i< token_nr;i++){
        tokens.push(empties[i].innerHTML);
    }

    //"map" is string representing every field on map
    function refresh_map(map){

        //Prepares array
        map = map.split(",");
        // places tokens on map
        for (let i=0; i<map.length; i++){
            empties[i].innerHTML = tokens[parseInt(map[i])];
        }

        // finds tokens
        var filled = document.querySelectorAll('.filled');

        // Adds eventListeners for Tokens
        for (const fill of filled){
            fill.addEventListener('dragstart',dragStart);
            fill.addEventListener('dragend',dragEnd);
        }
    }

    // returns string representation of map
    function prepare_map(token_nr){
        var string_map = "";
        for (let i=0 ; i<empties.length; i++){
            if(i<token_nr){
                string_map += i.toString() + ',';
            } else if (empties[i].firstChild) {
                string_map += empties[i].firstChild.dataset.token + ",";
            } else {
                string_map += (token_nr-1).toString() +',';
            }
        }
        string_map = string_map.slice(0, string_map.length-1);
        return string_map;
    }


    // Map functionality functions
    function dragStart(){
        picked = this;
        this.className +=' hold';
        setTimeout(() => (this.className = 'invisible'), 0);
    }

    function dragEnd() {
        this.className = 'filled';
    }

    function dragOver(e){
        e.preventDefault();
    }

    function dragEnter(e){
        e.preventDefault();
        this.className += ' hovered';

    }

    function dragLeave(){
        this.className = 'empty';
    }

    function dragDrop(e){
        e.preventDefault();
        if (picked.className == "invisible" && this.innerHTML.indexOf("<") == -1 || picked.className == "invisible" && this.id=="trash"){
        this.className = 'empty';
        this.append(picked);
        send_message(prepare_map(token_nr), "map");
        }

    }
