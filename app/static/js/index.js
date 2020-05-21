$(document).ready(function(){
    var socket = io.connect('http://127.0.0.1:5000');

    var myCards = [];
    const cardsNeeded = 5;

    function removeCard(cards, index){
        var newCards = []
        for(var i=0; i < cards.length; i++){
            if(i != index){
                newCards.push(cards[i]);
            }
        }
        return newCards;
    }

    $("#joinButton").click(function(){
        var data = {
            username : $("#username").val(),
            roomid : $("#roomid").val()
        };
        socket.emit('join_room', data);

        $("#username").prop('disabled',true);
        $("#roomid").prop('disabled',true);
        $("#joinButton").prop('disabled',true);
        $("#sendButton").prop('disabled',false);
        $("#drawButton").prop('disabled',false);
        $("#getAnswersButton").prop('disabled',false);
    });

    socket.on('join_room_message', function(data){
        $("#messages").append('<li>'+data["message"]+'</li>');
    });

    socket.on('room_closed', function(data){
        $("#messages").append('<li>The room is closed</li>');
        join_room_button_reset()
    });

    socket.on('payer_name_duplicate', function(data){
        $("#messages").append('<li>You are already in room: '+data["roomid"]+'</li>');
        join_room_button_reset()
    });

    socket.on('message', function(data){
        $("#messages").append('<li>'+data['username'] + ': ' + data["message"]+'</li>');
    });

    socket.on('get_question', function(data){
        $(".question-card .card-text").text(data["text"]);
    });

    socket.on('get_answers', function(data){
        for(var i=0; i < data.length; i++){
            myCards.push(data[i]["text"]);
        }
        for(var i=0; i < myCards.length; i++){
            $($(".answerbtn")[i]).text(myCards[i]);
        }
        $(".answerbtn").prop('disabled', false);
    });

    socket.on('show_answer', function(data){
        $("#gameAnnouncements").append('<li>'+data['username'] + ' chose: ' + data["answer"]+'</li>');
    });

    $("#sendButton").click(function(){
        var data = {
            username : $("#username").val(),
            roomid : $("#roomid").val(),
            message: $("#myMessage").val()
        };
        socket.emit('message', data);
    });

    $("#drawButton").click(function(){
        var data = {"roomid": $("#roomid").val(), "username": $("#username").val()};
        socket.emit('draw_question',data);
    });

    $("#getAnswersButton").click(function(){
        var data = {
            "needed": cardsNeeded - myCards.length,
            "username": $("#username").val()
    };
        socket.emit('draw_answers',data);
    });

    $(".answerbtn").click(function(){
        var data = {
            "username": $("#username").val(),
            "roomid": $("#roomid").val(),
            "answer": $(this).text()
        };
        socket.emit('submit_answer',data);

        for(var i=0; i < myCards.length; i++){
            if(myCards[i] == $(this).text()){
                myCards = removeCard(myCards, i);
            }
        }
        $(this).prop('disabled', true);
    });
});

function join_room_button_reset(){
        $("#username").prop('disabled',false);
        $("#roomid").prop('disabled',false);
        $("#joinButton").prop('disabled',false);
        $("#sendButton").prop('disabled',true);
        $("#drawButton").prop('disabled',true);
        $("#getAnswersButton").prop('disabled',true);
}