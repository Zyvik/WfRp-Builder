
//inicjatywa
var initiative_box = document.getElementById('initiative');

function add_initiative(){
    var li = document.createElement("li");
    li.className = "list-group-item";
    li.value = document.getElementById('i_value').value;
    li.innerHTML = li.value + " " + "<strong>" + document.getElementById('i_name').value+"</strong>" + "<input class='form-control' type='text'>";
    initiative_box.appendChild(li);
}

function sort_initiative(){
    var list = initiative_box.childNodes;
    function compare(a,b){
        if (a.value < b.value){
            return 1;
        }
        if (a.value > b.value){
            return -1;
        }
        return 0;
    }
    var array = Array.from(list);
    array.sort(compare);

    initiative_box.innerHTML = '';
    for(var i=0; i<array.length; i++ ){
        var li = document.createElement("li");
        initiative_box.appendChild(array[i]);
    }
}

function next_initiative(){
    var list = initiative_box.childNodes;
    var index = list.length-1;
    for(var i=0; i<list.length; i++){
        if (list[i].className == "list-group-item bg-primary"){
            index = i;
            break;
        }
    }

    list[index].className = "list-group-item";
    if (index >= list.length-1){
        index = -1;
    }
    list[index+1].className = "list-group-item bg-primary";
}

function reset_initiative(){
    initiative_box.innerHTML = "";
}