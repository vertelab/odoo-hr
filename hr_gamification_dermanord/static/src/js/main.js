function go_training(){
    openerp.jsonRpc("/hr/attendance/training", 'call', {
        'employee_id': $("#hr_employee").val(),
    }).done(function(data){
        clearContent();
        if(data == "done"){
            $('#hr_employee option[value=""]').attr('selected', true);
            window.location.reload();
        }
        else
            $("#employee_message_error").html("<h2 style='color: #f00;'>" + _t("Cannot registrate your training pass") + "</h2>");
            $('#Log_div').delay(15000).fadeOut('slow');
    });
}

function go_workout(){
    openerp.jsonRpc("/hr/attendance/workout", 'call', {
        'employee_id': $("#hr_employee").val(),
    }).done(function(data){
        clearContent();
        if(data == "done"){
            $('#hr_employee option[value=""]').attr('selected', true);
            window.location.reload();
        }
        else
            $("#employee_message_error").html("<h2 style='color: #f00;'>" + _t("Cannot registrate your workout pass") + "</h2>");
            $('#Log_div').delay(15000).fadeOut('slow');
    });
}

/* overrider original */
function employee_state(id){
    clearContent();
    if (id != "") {
        openerp.jsonRpc("/hr/attendance/state", 'call', {
            'employee': id,
        }).done(function(data){
            if(data['state'] == "present") {
                $("#hr_employee").val(data['id']);
                $("#login").addClass("hidden");
                $("#logout").removeClass("hidden");
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
                $("#hr_employee").val(data['id']);
                employee_project(data['id']);
                $("#login").removeClass("hidden");
                $("#logout").addClass("hidden");
                $("#go_training").addClass("hidden");
                $("#go_workout").addClass("hidden");
            }
        });
    }
    else {
        $("#login").addClass("hidden");
        $("#logout").addClass("hidden");
        $("#go_training").addClass("hidden");
        $("#go_workout").addClass("hidden");
    }
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
                $("#employee_flex_time").html("<h4><strong>" + _t("Flex Time") + ": </strong>" + data.attendance.flextime + _t(" minutes") + "</h4><h4><strong>" + _t("Flex Time Bank") + ": </strong>" + data.attendance.flextime_total + _t(" minutes") + "</h4>");
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
