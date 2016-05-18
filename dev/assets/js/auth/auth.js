var parsleyOptions = {
  errorClass: 'error',
  focus: 'none',
  errorsWrapper: '<span></span>',
  errorTemplate: '<span class="error active"></span>',
  excluded: 'input[type=button], input[type=submit], input[type=reset], input[disabled]'
};

function getUrlVars()
{
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}

function populateWithResponse(data){
  if(data.errors){
    errors = data.errors;
    $('form input').each(function(){
      var self = $(this);
      var name = self.attr('id');
      if(errors.hasOwnProperty(name)){
        var parsleyElement = self.parsley();
        var currentErrors = window.ParsleyUI.getErrorsMessages(parsleyElement);
        if(currentErrors.length === 0){
          window.ParsleyUI.removeError(parsleyElement, 'backendValidation');
          window.ParsleyUI.addError(parsleyElement, 'backendValidation', errors[name]);
        }
      }
    });
  }
  if(data.messages){
    $('#messageContainer').html(data.messages.success);
  }
}

function handleReponse(data){
  if (data.redirect) {
         // data.redirect contains the string URL to redirect to
         window.location.href = data.redirect;
  }
  else {
    populateWithResponse(data);
  }
}

function createFormData() {
  var formData = {};
  $('form input').each(function() {
    formData[this.name] = this.value;
  });
  return formData;
}

function signupSubmit(event){
  event.preventDefault();
  var form = $('#auth').parsley();
  form.validate();
  if(form.isValid()){
    var submission = createFormData();
    $.ajax({
      type: 'POST',
      url: '/signup',
      data: submission,
    }).then(function (data, status, jqXHR){
      handleReponse(data);
    },function(jqXHR, status, errorThrown){
      alert("An error occurred while attempting to process your request. Please try again. If this issue persists, let us know via contact@hackillinois.org.");
    }
    );
  }
}

function signupOnClickHandler(event){
  var self = $(this);
  event.preventDefault();
  var confirmPasswordContainer = $('#confirm-password-container');
  $('#input-container').append(confirmPasswordContainer.children(':first').clone());
  $('#input-container').children(':last').children(':first').removeAttr('disabled');
  $('#auth-login').remove();
  confirmPasswordContainer.remove();
  self.unbind();
  self.bind('click', signupSubmit);
}

function loginSubmit(event){
  event.preventDefault();
  var form = $('#auth').parsley();
  form.validate();
  if(form.isValid()){
    var submission = createFormData();
    $.ajax({
      type: 'POST',
      url: '/login',
      data: submission,
    }).then(function (data, status, jqXHR){
      handleReponse(data);
    },function(jqXHR, status, errorThrown){
      alert("An error occurred while attempting to process your request. Please try again. If this issue persists, let us know via contact@hackillinois.org.");
    }
    );
  }
}


function forgotPasswordSubmit(event){
  event.preventDefault();
  var form = $('#auth').parsley();
  form.validate();
  if(form.isValid()){
    var submission = createFormData();
    $.ajax({
      type: 'POST',
      url: '/forgot',
      data: submission,
    }).then(function (data, status, jqXHR){
      handleReponse(data);
    },function(jqXHR, status, errorThrown){
      alert("An error occurred while attempting to process your request. Please try again. If this issue persists, let us know via contact@hackillinois.org.");
    }
    );
  }
}

function resetPasswordSubmit(event){
  event.preventDefault();
  var form = $('#auth').parsley();
  form.validate();
  if(form.isValid()){
    var submission = createFormData();
    var urlVars = getUrlVars();
    submission["token"] = urlVars["token"];
    submission["user"] = urlVars["user"];
    $.ajax({
      type: 'POST',
      url: '/reset',
      data: submission,
    }).then(function (data, status, jqXHR){
      handleReponse(data);
    },function(jqXHR, status, errorThrown){
      alert("An error occurred while attempting to process your request. If this issue persists, let us know via contact@hackillinois.org.");
    }
    );
  }
}

function forgotPasswordOnClickHandler(event){
  var self = $(this);
  $('#auth-signup').remove();
  $('#auth-login').remove();
  $('#auth-password').remove();
  $('#auth-confirm-password').remove();
  $('#confirm-password-container').remove();
  $('#password-error').remove();
  $('#confirm-password-error').remove();
  var forgotPasswordContainer = $('#forgot-password-container');
  $('#buttonContainer').append(forgotPasswordContainer.children(':first'));
  $('#auth-forgot').removeAttr('disabled');
  forgotPasswordContainer.remove();
  self.parent().remove();
}

function parsleyValidationHandler() {
  //remove any non-parsley errors
  $('#form-block input').each(function(){
    var parsleyElement = $(this).parsley();
    window.ParsleyUI.removeError(parsleyElement, 'backendValidation');
  });
}


$(document).ready(function() {
  $('#auth').parsley(parsleyOptions);
  // Remove initial errors on validation
  $('#auth').parsley().on('form:validate', parsleyValidationHandler);
  $('form input').each(function(){
    //when parsley validation fails, remove any backend errors so parsley errors can be shown
    $(this).parsley().on('field:error', parsleyValidationHandler);
  });
  // On first click of Sign-up button, remove Login button and add
  // confirm password field.
  $('#auth-signup').on("click", signupOnClickHandler);
  $('#auth-login').on("click", loginSubmit);
  $('#auth-forgot').on("click", forgotPasswordSubmit);
  $('#forgot-password').on('click', forgotPasswordOnClickHandler);
  $('#reset-submit').on('click', resetPasswordSubmit);
});
