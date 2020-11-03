var check = function() {

  var val1 = document.getElementById('input password').value;
  var val2 = document.getElementById('confirm password').value
  if (val1 == val2 && val1.length >= 6) {
    document.getElementById('message').style.color = 'green';
    document.getElementById('message').innerHTML = 'matching';
    return true;
  } else {
    document.getElementById('message').style.color = 'red';
    document.getElementById('message').innerHTML = "  Not valid";
    return false;
  }
}

function checkEmailExist(allEmails) { // if email exist it will be error

  // change border color to black after clicking on the red box(after failed)
    document.getElementById('input email').onclick = function(){
    document.getElementById("input email").style.borderColor = "black";
}

    var email = document.getElementById("input email").value;
     for(var i=0;i<allEmails.length;i++){
     if(email == allEmails[i]){
       // alert("email already exist");
       document.getElementById("input email").style.borderColor = "red";
       return false; // email already exist
     }
   }
     return true; // email not exsit
   }


var checkValidation = function(allEmails) {

// change border color to black after clicking on the red box(after failed)
  document.getElementById('confirm password').onclick = function(){
  document.getElementById("confirm password").style.borderColor = "black";
}

  var val1 = document.getElementById('input password').value;
  var val2 = document.getElementById('confirm password').value
  if (val1 == val2 && val1.length >= 6) {
    return checkEmailExist(allEmails);
  } else {
    // alert("passwords not matching")
    document.getElementById("confirm password").style.borderColor = "red";
    return false;
  }
}


function checkEmailNotExist(allEmails) { // if email not exist it will be error

  // change border color to black after clicking on the red box(after failed)
    document.getElementById('input email').onclick = function(){
    document.getElementById("input email").style.borderColor = "black";
}

  var email = document.getElementById("input email").value;
   for(var i=0;i<allEmails.length;i++){
   if(email == allEmails[i]){
     return true; // email already exist
   }
 }
 document.getElementById("input email").style.borderColor = "red";
 return false;
 }

function isNumber(evt) {
    evt = (evt) ? evt : window.event;
    var charCode = (evt.which) ? evt.which : evt.keyCode;
    if (charCode > 31 && (charCode < 48 || charCode > 57)) {
        return false;
    }
    return true;
}

$(".phoneRO").on('paste', function(e) {
  e.preventDefault();
});
$(".phoneRO").on('dragstart drop', function(e){
    e.preventDefault();
    return false;
});

$('.date-own').datepicker({
  format: "dd/mm/yyyy",
  startDate: "TODAY",
  maxViewMode: 1,
  forceParse: false,
  autoclose: true,
  todayHighlight: true
});
$(".readonly").on('keydown paste', function(e) {
  e.preventDefault();
});
$(".readonly").on('dragstart drop', function(e){
    e.preventDefault();
    return false;
});
