$(document).ready(function () {
    $('form.disable-submit').on('submit', function (e) {
        e.preventDefault();
    });

    $(document).on('click','.delete-row-btn', function(e){
        e.preventDefault();
        if($('#exposure-table tbody tr').length>1){
            $(this).closest('tr').remove();
        }        
    });

    $(document).on('keyup', '.amount-text', function(e){        
        let x = $(this).val();
        x = x.replace(/[^0-9]+/g, "");
        if(x[0]==0){
            x = x.substr(1);
        }
        x = x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        $(this).val(x);        
        x = x.replace(/,/g, "");
        $(this).siblings('input[type="number"]').val(parseInt(x));
    })

    $("#save_report").on('click', function(){
        if(checkLiabilityAndAsset()){
            if(!checkUSDAmount()){
                $("#table_error").html("USD equivalent amount can't be 0")
                setTimeout(function(){$("#table_error").html("")}, 1500);    
            }else{
                $("#user_action").val('save');
                $("#exposures_form").submit();
            }
        }else{
            $("#table_error").html("Liability Currency can't be same with Asset Currency")
            setTimeout(function(){$("#table_error").html("")}, 1500);
        }
    })

    $("#exposures_form").on('submit', function(){
        if(!checkLiabilityAndAsset()){
            $("#table_error").html("Liability Currency can't be same with Asset Currency")
            setTimeout(function(){$("#table_error").html("")}, 1500);
        }
        if(!checkUSDAmount()){
            $("#table_error").html("USD equivalent amount can't be 0")
            setTimeout(function(){$("#table_error").html("")}, 1500);    
        }
        return checkLiabilityAndAsset() && checkUSDAmount();
    })

    $("#edit_account").on('click', function(){
        $(".form-wrapper").removeClass('uneditable');
        $("#edit_account").addClass('hide');
        $("#update_account").removeClass("hide");
    })

    $("#update_account").on('click', function(){
        $("#account_form").submit();
    })

    $("#find_matches").on('click', function(e){ 
        e.preventDefault();       
        $(this).addClass('disabled-btn');
        $.ajax({
            type: "POST",
            url: '/find-matches',
            data: { name: "John", time: "2pm" },
            success: function(response){
                location.reload();
            }
          });
    })
});

function showStep(stepno){
    if(stepno=="step2"){
        if(isEmail($("#email").val())){
            var pass = $("#password").val();

            var strength = 1;
            var arr = [/.{5,}/, /[a-z]+/, /[0-9]+/, /[A-Z]+/];
            jQuery.map(arr, function(regexp) {
            if(pass.match(regexp))
                strength++;
            });

            if(strength>3){
                goStep(stepno);                
            }else{
                $("#password-wrapper p.error-msg").html("Password is not strong enough")
                setTimeout(function(){$("#password-wrapper p.error-msg").html("")},1500);
            }
        }else{
            $("#email-wrapper p.error-msg").html("Invalid Email Address")
            setTimeout(function(){$("#email-wrapper p.error-msg").html("")},1500);
        }
    }else if(stepno=="step1"){
        goStep(stepno);
    }
}

function goStep(stepno){
    $('.step').removeClass("active");
    var element = document.getElementById(stepno);
    element.classList.add("active");
}
function toggleCreditCardForm() {
    if($('#payment input[type=radio][name=payment_method]:checked').val() === 'credit-card') {
        $('#cc_form').removeClass('d-none')
    } else {
        $('#cc_form').addClass('d-none')
    }
}

function addExposureRow(){
    if(checkLiabilityAndAsset()){
        if(!checkUSDAmount()){
            $("#table_error").html("USD equivalent amount can't be 0")
            setTimeout(function(){$("#table_error").html("")}, 1500);    
        }else{
            if($("#user_plan").val()=="free"){
                if($('#exposure-table tbody tr').length<3){
                    $('#exposure-table tbody').append($('#exposure_row_hidden').val());        
                }else{
                    $("#table_error").html("You need to upgrade membership to add more pairs")
                    setTimeout(function(){$("#table_error").html("")}, 1500);    
                }
            }else if($("#user_plan").val()=="premium"){
                if($('#exposure-table tbody tr').length<10){
                    $('#exposure-table tbody').append($('#exposure_row_hidden').val());        
                }else{
                    $("#table_error").html("You need to upgrade membership to add more pairs")
                    setTimeout(function(){$("#table_error").html("")}, 1500);    
                }
            }else{
                if($('#exposure-table tbody tr').length<20){
                    $('#exposure-table tbody').append($('#exposure_row_hidden').val());
                }
            }                    
        }        
    }else{
        $("#table_error").html("Liability Currency can't be same with Asset Currency")
        setTimeout(function(){$("#table_error").html("")}, 1500);
    }    
}

function isEmail(email) {
    var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    return regex.test(email);
}

function checkLiabilityAndAsset(){
    let res = false;
    $('#exposure-table tr').each(function(){        
        if($(this).find('[name="long[]"]').val() == $(this).find('[name="short[]"]').val()){
            res = false;
        }else{
            res = true;
        }
    })
    return res;
}

function checkUSDAmount(){
    let res = false;
    $('#exposure-table tr').each(function(){        
        if($(this).find('[type="text"]').val() == 0 || $(this).find('[type="text"]').val() == "" ){
            res = false;
        }else{
            res = true;
        }
    })
    return res;
}