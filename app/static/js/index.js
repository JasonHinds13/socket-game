$(document).ready(function(){
    var socket = io.connect(window.location.origin);

    var myCards = [];
    const cardsNeeded = 5;

    $("#signInModal").modal("show");

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
        $("#leaveButton").prop('disabled', false);
        $("#sendButton").prop('disabled',false);
        $("#drawButton").prop('disabled',false);
        $("#getAnswersButton").prop('disabled',false);

        $("#signInModal").modal("hide");
    });

    $('#leaveButton').click(function(){
        var data = {
            username : $("#username").val(),
            roomid : $("#roomid").val()
        };
        socket.emit('leave_room', data);

        join_room_button_reset();

        $("#signInModal").modal("show");

    });

    socket.on('join_room_message', function(data){
        $("#messages").append('<li>'+data["message"]+'</li>');
        scroll_down();
    });

    socket.on('room_closed', function(data){
        $("#messages").append('<li>The room is closed</li>');
        join_room_button_reset();
        scroll_down();
    });

    socket.on('payer_name_duplicate', function(data){
        $("#messages").append('<li>You are already in room: '+data["roomid"]+'</li>');
        join_room_button_reset();
        scroll_down();
    });

    socket.on('drew_question_last', function(data){
        $("#messages").append('<li>Player '+data["username"]+' drew the last question card. Someone else draw</li>');
        scroll_down();
    });

    socket.on('submit_answer_success', function(data){
        $("#messages").append('<li>Round '+data["round"]+' - '+data["username"]+' played a card.</li>');
        scroll_down();
    });

    socket.on('message', function(data){
        $("#messages").append('<li>'+data['username'] + ': ' + data["message"]+'</li>');
        scroll_down();
    });

    socket.on('game_announcements', function(data) {
        $('#messages').append('<li>'+data['announcement']+'</li>');
        scroll_down();
    });

    socket.on('game_reset', function(data) {
        var reset_choice = confirm(data['message']);
        var data = {
            username : $("#username").val(),
            roomid : $("#roomid").val(),
            reset_choice: reset_choice
        };

        socket.emit('game_reset', data);
    });

    socket.on('reset_game', function() {
        $('#messages').children().remove();
        $('.question-card > .card-text').text('Draw Card');
        $('.answer-cards-list .answerbtn').text('X');
        $('.answer-cards-list .answerbtn').prop('disabled', false);
        $('#gameResetButton').prop('disabled', true);
    });

    socket.on('get_question', function(data){
        $('#gameResetButton').prop('disabled', false);
        $(".question-card .card-text").text(data["text"]);
    });

    socket.on('get_answers', function(data){
        for(var i=0; i < data.length; i++){
            myCards.push(data[i]["text"]);
        }
        for(var i=0; i < myCards.length; i++){
            $($(".answer-card .card-text")[i]).text(myCards[i]);
        }
        $(".answer-card").prop('disabled', false);
    });

    socket.on('show_answer', function(data){
        $("#messages").append('<div>------------ Round '+data[0]['round']+' Answers------------</div>');
        for(var i=0; i < data.length; i++){
            $("#messages").append('<li>Round '+data[i]['round']+' - '+data[i]['username'] + ' chose: ' + data[i]["answer"]+'</li>');
        }
        $("#messages").append('<div>----------------------------------</div>');
        scroll_down();
    });

    socket.on('submit_answer_failed', function(data){
        $("#messages").append('<li>You have already played for this round</li>');
        scroll_down();
    });

    socket.on('room_error', function(data){
        $("#messages").append('<li>'+data['error']+'</li>');
        scroll_down();
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
            "username": $("#username").val(),
            'roomid': $("#roomid").val()
    };
        socket.emit('draw_answers',data);
    });

    $(".answer-card").click(function(){
        var ans = $(this).first().text().trim();
        var data = {
            "username": $("#username").val(),
            "roomid": $("#roomid").val(),
            "answer": ans
        };
        socket.emit('submit_answer',data);

        for(var i=0; i < myCards.length; i++){
            if(myCards[i] == ans){
                myCards = removeCard(myCards, i);
            }
        }
        $(this).prop('disabled', true);
    });

    $('#gameResetButton').click(function() {
        var data = {
            "username": $("#username").val(),
            'roomid': $("#roomid").val()
        };
        socket.emit('initiate_game_reset', data);
    });
});

function scroll_down(){
    var mdiv = document.getElementById("messages-div");
    mdiv.scrollTop = mdiv.scrollHeight;
}

function join_room_button_reset(){
        $("#username").prop('disabled',false);
        $("#roomid").prop('disabled',false);
        $("#joinButton").prop('disabled',false);
        $("#leaveButton").prop('disabled', true);
        $("#sendButton").prop('disabled',true);
        $("#drawButton").prop('disabled',true);
        $("#getAnswersButton").prop('disabled',true);
        $('#gameResetButton').prop('disabled', true);
}