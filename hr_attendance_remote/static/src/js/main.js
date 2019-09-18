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
        number_employees();
    });
}

var remote_original_attendance_state_update = attendance_state_update;

attendance_state_update = function(data){
    remote_original_attendance_state_update(data);
    if(data['state'] == "present") {
        $("#check_in_out").removeClass("hidden");

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

function check_employees_presence(){
    openerp.jsonRpc("/hr/attendance/employees_presence", 'call', {
    }).done(function(data){
        clearContent();
        if(data == "") {
            number_employees();
            $("#employees_list").html("<h2 style='color: #f00;' class='text-center'>" + _t("No User is logged in") +"</h2>");
        }
        else {
            var employee_contect = "";
            $.each( data, function( name, image ) {
                var img = "<img src='/hr_attendance_terminal/static/src/img/icon-user.png' style='width: 64px; height: 64px; margin: auto; display: block;'/>";
                if (image !== null)
                    img = "<img src='data:image/png;base64," + image + "' style='margin: auto; display: block;'/>";
                employee_contect += "<div class='col-md-2 col-sm-2 col-xs-2'>" + img + "<p class='text-center'>" + name + "</p></div>"
            });
            number_employees();
            $("#employees_list").html(employee_contect);
        }
        logTimeOut = setTimeout("$('#Log_div').fadeOut('slow')", 15000);
    });
}

var remote_original_number_employees = number_employees;

number_employees = function(){
    remote_original_number_employees();
    openerp.jsonRpc("/hr/attendance/employees_number_presence", 'call', {
    }).done(function(data){
        $("#employees_qty_present").html("<span>" + data +"</span>");
    });
}
