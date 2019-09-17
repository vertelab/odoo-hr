function go_training(){
    openerp.jsonRpc("/hr/attendance/training", 'call', {
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
            $("#employee_message_error").html("<h2 style='color: #f00;'>" + _t("Cannot registrate your training pass") + "</h2>");
            $('#Log_div').delay(15000).fadeOut('slow');
        }
    });
}

function go_workout(){
    openerp.jsonRpc("/hr/attendance/workout", 'call', {
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
            $("#employee_message_error").html("<h2 style='color: #f00;'>" + _t("Cannot registrate your workout pass") + "</h2>");
            $('#Log_div').delay(15000).fadeOut('slow');
        }
    });
}

var gamification_original_attendance_state_update = attendance_state_update;

attendance_state_update = function(data){
    gamification_original_attendance_state_update(data);
    if(data['state'] == "present") {
        openerp.jsonRpc("/hr/attendance/training_validate", 'call', {
            'employee_id': $("#hr_employee").val(),
        }).done(function(data){
            return (data == 'confirm') ? $("#go_training").removeClass("hidden") : $("#go_training").addClass("hidden");
        });
        openerp.jsonRpc("/hr/attendance/workout_validate", 'call', {
            'employee_id': $("#hr_employee").val(),
        }).done(function(data){
            return (data == 'confirm') ? $("#go_workout").removeClass("hidden") : $("#go_workout").addClass("hidden");
        });        
    }
    if(data['state'] == "absent") {
        $("#go_training").addClass("hidden");
        $("#go_workout").addClass("hidden");
    }
}

var gamification_original_attendance_state_reset = attendance_state_reset;

attendance_state_reset = function(id){
    gamification_original_attendance_state_reset(id);
    $("#go_training").addClass("hidden");
    $("#go_workout").addClass("hidden");
}

function get_attendance(id){
    openerp.jsonRpc("/hr/attendance/" + id, 'call', {
        }).done(function(data){
            $("#login").addClass("hidden");
            $("#logout").addClass("hidden");
            $("#attendance_div").load(document.URL +  " #attendance_div");
            clearContent();
            if (data.employee.img !== null)
                $("#employee_image").html("<img src='data:image/png;base64," + data.employee.img + "'/>");
            if (data.employee.img === null)
                $("#employee_image").html("<img src='/hr_attendance_terminal/static/src/img/icon-user.png'/>");
            if (data.attendance.action === 'sign_in') {
                $("#employee_message").html("<h2>" + _t("Welcome!") + "</h2><h2>" + data.employee.name +"</h2>");
                number_employees();
            }
            if (data.attendance.action === 'sign_out'){
                var workedHour = 0;
                var workedMinute = 0;

                if (data.attendance.worked_hours != false) {
                    workedHour = hour2HourMinute(data.attendance.worked_hours)[0];
                    workedMinute = hour2HourMinute(data.attendance.worked_hours)[1];
                }
                $("#employee_message").html("<h2>" + _t("Goodbye!") + "</h2><h2>" + data.employee.name +"</h2>");
                $("#employee_worked_hour").html("<h4><strong>" + _t("Worked Hours") + ": </strong>" + workedHour + _t(" hours and ") + workedMinute + _t(" minutes") + "</h4>");
                if(data.attendance.work_time === 'flex'){
                    $("#employee_flex_time").html("<h4><strong>" + _t("Flex Time") + ": </strong>" + Math.round(data.attendance.flextime) + _t(" minutes") + "</h4><h4 id=\"flextime_total_" + id + "\"><strong>" + _t("Flex Time Bank") + ": </strong></h4>");
                    openerp.jsonRpc("/hr/attendance/flextotal/" + id, 'call', {
                        }).done(function(data){
                            $("#flextime_total_" + id).html("<strong>" + _t("Flex Time Bank") + ": </strong>" + Math.round(data.flextime_total) + _t(" minutes"));
                        });
                }
                openerp.jsonRpc("/hr/attendance/workout_status", 'call', {
                    'employee_id': $("#hr_employee").val(),
                }).done(function(data){
                    $("#training_status").html("<h4><strong>" + _t("This week(month) 7MW") + ": </strong>" + data['works_in_week'] + "(" + data['works_in_month'] + ")</h4>");
                });
                openerp.jsonRpc("/hr/attendance/training_status", 'call', {
                    'employee_id': $("#hr_employee").val(),
                }).done(function(data){
                    $("#workout_status").html("<h4><strong>" + _t("This week(month) Training") + ": </strong>" + data['works_in_week'] + "(" + data['works_in_month'] + ")</h4>");
                });
                number_employees();
            }
            logTimeOut = setTimeout("$('#Log_div').fadeOut('slow')", 15000);
        });
}

function clearContent(){
    $("#employees_list").empty();
    $("#employee_image").empty();
    $("#employee_message").empty();
    $("#employee_message_error").empty();
    $("#employee_worked_hour").empty();
    $("#employee_flex_time").empty();
    $("#employee_time_bank").empty();
    $("#training_status").empty();
    $("#workout_status").empty();
    $('#Log_div').css("display", "unset");
    $('#Log_div').stop();
    clearTimeout(logTimeOut);
}
