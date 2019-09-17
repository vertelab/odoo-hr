function check_in_out(){
    openerp.jsonRpc("/hr/attendance/presence", 'call', {
        'employee_id': $("#hr_employee").val(),
    }).done(function(data){
        $("#login").addClass("hidden");
        $("#logout").addClass("hidden");
        $("#attendance_div").load(document.URL +  " #attendance_div");
        clearContent();
        if(data == "done"){
            $('#hr_employee option[value=""]').attr('selected', true);
        }
        else{
            clearContent();
            $("#employee_message_error").html("<h2 style='color: #f00;'>" + _t("Cannot sense your presence") + "</h2>");
            $('#Log_div').delay(15000).fadeOut('slow');
        }
    });
}

var remote_original_attendance_state_update = attendance_state_update;

attendance_state_update = function(data){
    remote_original_attendance_state_update(data);
    if(data['state'] == "present") {
        $("#check_in_out").removeClass("hidden");
        //~ $("#check_in_label").removeClass("hidden");
        //~ $("#check_out_label").removeClass("hidden");

        openerp.jsonRpc("/hr/attendance/presence_status", 'call', {
            'employee_id': $("#hr_employee").val(),
        }).done(function(data){
            if (data == 'in') {
                $("#check_in_img").addClass("hidden");
                $("#check_out_img").removeClass("hidden");
                $("#check_in_label").addClass("hidden");
                $("#check_out_label").removeClass("hidden");
            } else {
                $("#check_in_img").removeClass("hidden");
                $("#check_out_img").addClass("hidden");
                $("#check_in_label").removeClass("hidden");
                $("#check_out_label").addClass("hidden");
            }
        });
    }
    if(data['state'] == "absent") {
        $("#check_in_out").addClass("hidden");
        if (data == 'in') {
            $("#check_in_img").addClass("hidden");
            $("#check_out_img").removeClass("hidden");
            $("#check_in_label").addClass("hidden");
            $("#check_out_label").removeClass("hidden");
        } else {
            $("#check_in_img").removeClass("hidden");
            $("#check_out_img").addClass("hidden");
            $("#check_in_label").removeClass("hidden");
            $("#check_out_label").addClass("hidden");
        }
    }
}

var remote_original_attendance_state_reset = attendance_state_reset;

attendance_state_reset = function(id){
    remote_original_attendance_state_reset(id);
    $("#check_in_out").addClass("hidden");
    if (data == 'in') {
        $("#check_in_img").addClass("hidden");
        $("#check_out_img").removeClass("hidden");
        $("#check_in_label").addClass("hidden");
        $("#check_out_label").removeClass("hidden");
    } else {
        $("#check_in_img").removeClass("hidden");
        $("#check_out_img").addClass("hidden");
        $("#check_in_label").removeClass("hidden");
        $("#check_out_label").addClass("hidden");
    }
}

