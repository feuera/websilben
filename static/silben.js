

function setCurStufe(name, stufe) {
    //alert(name+stufe)
    $.get("{{url_for('setStufe')}}", {user: name, st:stufe}, function(data){
        alert("done");
    });
}

function shuffle(array) {
    var m = array.length, t, i;
    // While there remain elements to shuffle…
    while (m) {
        // Pick a remaining element…
        i = Math.floor(Math.random() * m--);
        // And swap it with the current element.
        t = array[m];
        array[m] = array[i];
        array[i] = t;
    }
    console.log(array);
    return array;
} 

function showSilben(silbCnt) {
    pre = ''+
        '<div class="col-xs-6 col-md-4 silbe">'+
        '<div id="jumbo" class="btn btn-info jumbotron"> <h1 class="text-center">';
    post = '</h1></div></div>';
    var s = ''
        for (var i = 0, item; item = Silb[i++];) {
            s+= pre;
            s+= item;
            s+= post;
        }
    $("#diesilben").html(s);
}

function start() {
    silbCnt = 0;
    Silb = silben.slice(silbCnt,silbCnt+nr);
    showSilben(Silb);
}
