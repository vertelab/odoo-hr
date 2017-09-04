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

function go_training(){
    openerp.jsonRpc("/hr/attendance/training", 'call', {
        'employee_id': $("#hr_employee").val(),
    }).done(function(data){
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
        if(data == "done"){
            $('#hr_employee option[value=""]').attr('selected', true);
            window.location.reload();
        }
        else
            $("#employee_message_error").html("<h2 style='color: #f00;'>" + _t("Cannot registrate your workout pass") + "</h2>");
            $('#Log_div').delay(15000).fadeOut('slow');
    });
}
