$(function () {
  var EMAIL_UNAVAILABLE_ERROR = 'emailUnavailableError';
  var parsleyOptions = {
    excluded: "input[type=button], input[type=submit], input[type=reset], input[type=hidden], :hidden"
  };

  $addForm = $('#user-add');
  $viewForm = $('#user-view');
  $userId = $('#userId');
  $type = $('#type');
  $addSubmit = $('#addSubmit');
  $firstName = $('#firstName');
  $lastName = $('#lastName');
  $email = $('#email');
  $organization = $('#organization');
  $isNewOrganization = $('#isNewOrganization');
  $newOrganization= $('#newOrganization');
  $tier= $('#tier');
  $hardware = $('#hardware');
  $shirt_size = $('#shirt_size');
  $initiativeSelect = $('#initiativeSelect');
  $walkIn = $('#walkIn');
  $accepted = $('#accepted');

  $addForm.parsley(parsleyOptions);
  $viewForm.parsley(parsleyOptions);
  $userId.on('click', function(event) {
    $(this).val('');
  });
  $viewForm.on('submit', function (event) {
    event.preventDefault();

    var isValid = $viewForm.parsley().validate();
    if (!isValid) return;

    var id = $userId.val();
    $userId.blur();
    window.open('/admin/users/view/' + id, '_blank');
  });
  $addForm.on('submit', function (event) {
    event.preventDefault();

    var isValid = $addForm.parsley().validate();
    if (!isValid) return;

    var rawData = $(this).serializeArray();
    var data = { 'status':'ACCEPTED' };
    rawData.map(function(object){
      data[object.name] = object.value;
    });

    $.ajax({
      type: 'POST',
      url: '/admin/users/add',
      data: data,
    }).then(function(data, status, jqXHR){
      alert('User added successfully. An email has been sent with instructions on how to set a password.');
      window.location.reload();
    }, function(jqXHR, status, errorThrown){
      response = {};
      try {
        response = JSON.parse(jqXHR.responseText);
      } catch(SyntaxError){ }

      error = {};
      if (response.errors) error = response.errors[0];
      if (error.name === "UserAlreadyExistsError") {
        var emailField = $email.parsley();
        window.ParsleyUI.removeError(emailField, EMAIL_UNAVAILABLE_ERROR);
        window.ParsleyUI.addError(emailField, EMAIL_UNAVAILABLE_ERROR, error.message);
      }
      else {
        alert("An error occurred. Please try again and check your console for errors.");
      }
    });
  });

  $isNewOrganization.on('change', function(){
      if (this.checked) {
        $newOrganization.parent().removeClass('hidden');
        $tier.parent().removeClass('hidden');
        $hardware.parent().parent().removeClass('hidden');
        $organization.parent().addClass('hidden');
        return;
      }

      $newOrganization.parent().addClass('hidden');
      $tier.parent().addClass('hidden');
      $hardware.parent().parent().addClass('hidden');
      $organization.parent().removeClass('hidden');
  });

  $type.on('change', function (event) {
    var value = event.target.value;

    var $common = $firstName.parent().add($lastName.parent()).add($addSubmit)
    .add($email.parent()).add($shirt_size.parent());
    $common.removeClass('hidden');

    var $uncommon = $organization.parent().add($walkIn.parent().parent())
    .add($newOrganization.parent()).add($accepted.parent().parent()).add($tier.parent())
    .add($isNewOrganization.parent().parent()).add($initiativeSelect.parent())
    .add($hardware.parent().parent());
    $uncommon.addClass('hidden');

    if (value === 'HACKER') {
      $initiativeSelect.parent().removeClass('hidden');
      $walkIn.parent().parent().removeClass('hidden');
      $accepted.parent().parent().removeClass('hidden');
    }
    if (value === 'MENTOR' || value === 'SPONSOR') {
      $addForm.parsley().destroy();
      $shirt_size.attr('data-parsley-required', 'false');
      $addForm.parsley(parsleyOptions);
      $organization.parent().removeClass('hidden');
      $isNewOrganization.parent().parent().removeClass('hidden');
      if(value === 'SPONSOR'){
        $tier.children().first().prop( "disabled", true );
      }
      else {
        $tier.children().first().prop( "disabled", false );
      }
    }
    else {
      $addForm.parsley().destroy();
      $shirt_size.attr('data-parsley-required', 'true');
      $addForm.parsley(parsleyOptions);
    }
  });
});
