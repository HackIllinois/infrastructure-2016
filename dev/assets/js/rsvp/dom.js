$(function () {
  var parsleyOptions = {
    errorClass: 'error',
    focus: 'none',
    errorsWrapper: '<span></span>',
    errorTemplate: '<span class="error active"></span>',
    excluded: "input[type=button], input[type=submit], input[type=reset], input[type=hidden], :hidden:not('.selectized')"
  };

  var prohibited = ['BUS_KU_MIZZOU', 'BUS_PURDUE', 'BUS_FLORIDA_GEORGIA_TECH', 'BUS_WISCONSIN_MADISON'];

  var attendingOptions = [{
    name: "Yes, I'll be there!",
    value: true
  }, {
    name: "No, I can't make it.",
    value: false
  }];
  var transportationOptions = [{
      name: "Driving",
      value: "DRIVING",
      sort: 1
    }, {
      name: "Bus (UIC/DePaul)",
      value: "BUS_UIC_DEPAUL",
      sort: 2
    }, {
      name: "Bus (IIT/UChicago)",
      value: "BUS_IIT_UCHICAGO",
      sort: 3
    }, {
      name: "Bus (Northwestern)",
      value: "BUS_NORTHWESTERN",
      sort: 4
    },
    // , {
    //   name: "Bus (KU/Mizzou)",
    //   value: "BUS_KU_MIZZOU",
    //   sort: 5
    // }
    {
      name: "Bus (KU/Mizzou) - Closed",
      value: "BUS_KU_MIZZOU",
      sort: 5
    },
    // {
    //   name: "Bus (Purdue)",
    //   value: "BUS_PURDUE",
    //   sort: 6
    // },
    {
      name: "Bus (Purdue) - Closed",
      value: "BUS_PURDUE",
      sort: 6
    },
    // {
    //   name: "Bus (Florida/Georgia Tech)",
    //   value: "BUS_FLORIDA_GEORGIA_TECH",
    //   sort: 7
    // },
    {
      name: "Bus (Florida/Georgia Tech) - Closed",
      value: "BUS_FLORIDA_GEORGIA_TECH",
      sort: 7
    },
     {
      name: "Bus (Rose-Hulman)",
      value: "BUS_ROSE_HULMAN",
      sort: 8
    },
    // {
    //   name: "Bus (Wisconsin-Madison)",
    //   value: "BUS_WISCONSIN_MADISON",
    //   sort: 9
    // },
    {
      name: "Bus (Wisconsin-Madison) - Closed",
      value: "BUS_WISCONSIN_MADISON",
      sort: 9
    },
    {
        name: "Not applicable",
        value: "NOT_NEEDED",
        sort: 10
    }];

  var $form = $('#rsvp-form');
  var isUpdate = $('#submit').hasClass('update');
  var isOpenSource = $form.attr('data-os') === 'true';
  $form.parsley(parsleyOptions);

  var $attendingSelectize = $('#attending').selectize({
    options: attendingOptions,
    labelField: 'name',
    valueField: 'value',
    sortField:[{field: 'name', direction: 'desc'}, {field: '$score'}],
    searchField: ['name'],
    maxItems: 1,
    create: false
  });
  var $transporatationSelectize = $('#transportation').selectize({
    options: transportationOptions,
    labelField: 'name',
    valueField: 'value',
    sortField: 'sort',
    searchField: ['name'],
    maxItems: 1,
    create: false
  });

  if (isUpdate) {
    $('[data-selectize-value]').each(function () {
      var $this = $(this);
      var name = $this.attr('name');
      var value = $this.attr('data-selectize-value');

      if (name === 'attending') {
        value = (value === 'true') ? '1' : '0';
        $attendingSelectize[0].selectize.setValue(value);
      } else {
        $transporatationSelectize[0].selectize.setValue(value);
      }
    });
  }

  $('#reimbursement-question').on('click', function (event) {
    event.preventDefault();
    var answer = $(event.target).attr('data-answer');
    if (answer === "false") {
      alert("Sorry, but you do not qualify for the reimbursement of expenses for a flight from your area. Questions? Please send us an email at contact@hackillinois.org.");
    } else {
      alert("You're in luck! It looks like we can reimburse you for the cost of a flight from your area (up to $150). Questions? Please send us an email at contact@hackillinois.org.");
    }
  });

  $('#transportation').on('change', function (event) {
    var value = event.target.value;
    var $transportationDetailsGroup = $('#transportation-details-caption, #transportation-details-row, #transportation-details-2-row');
    var $reimbursement = $('#reimbursement-question-row');
    if (value === 'DRIVING') {
      $transportationDetailsGroup.removeClass('hidden');
    } else if ($.inArray(value, prohibited)>=0){
      alert("Sorry, but this transportation route is now closed.");
      $transporatationSelectize[0].selectize.setValue('none');
    } else {
      $transportationDetailsGroup.addClass('hidden');
    }

    if (value !== 'NOT_NEEDED') {
      $reimbursement.addClass('hidden');
    } else {
      $reimbursement.removeClass('hidden');
    }
  });

  $('#attending').on('change', function (event) {
    var value = event.target.value;
    var $transportationGroup = $('#transportation-caption, #transportation-row');
    var $transportationDetailsGroup = $('#transportation-details-caption, #transportation-details-row, #transportation-details-2-row');
    var $transportation = $('#transportation');
    if (value === "0") {
      $transportationGroup.addClass('hidden');
      $transportationDetailsGroup.addClass('hidden');
      $transportation.removeAttr('data-parsley-required');
    } else {
      $transportationGroup.removeClass('hidden');
      $transportation.attr('data-parsley-required', 'true');

      if ($('#transportation').val() === 'DRIVING') $transportationDetailsGroup.removeClass('hidden');
    }
    // we don't want the second selectize to be required
    // if the hacker is not coming to the event, so we re-bind
    $form.parsley().destroy();
    $form.parsley(parsleyOptions);
  });

  $form.on('submit', function (event) {
    event.preventDefault();

    var isValid = $form.parsley().validate();
    if (!isValid) return;

    var response = {};
    $form.serializeArray().map(function (element) {
      if (element.name == "attending") {
        response[element.name] = (element.value == "1") ? true : false;
      } else {
        response[element.name] = element.value;
      }
    });

    var $submit = $('#submit');
    $submit.prop('disabled', true);
    $submit.html('Responding...');

    var method = (isUpdate) ? 'PUT' : 'POST';
    $.ajax({
      type: method,
      url: '/rsvp',
      data: response
    }).then(function (data, status, jqXHR) {
      $('#submit-row').addClass('hidden');
      if (response.attending) {
        $('#positive-response').removeClass('hidden');
        if (!isUpdate && isOpenSource) {
          $('#regular-container').fadeOut("slow", function () {
            $('#os-response').hide().removeClass('hidden').fadeIn("slow", function () {
              $('#sub-title').text('Okay, one last thing.');
            });
          });
        }
      } else {
        $('#negative-response').removeClass('hidden');
      }
    }, function (jqXHR, status, errorThrown) {
      if (jqXHR.status == 400) {
        alert("There was a problem with your response. Please try again. " +
                "If this issue persists, let us know via contact@hackillinois.org");
      } else if (jqXHR.status == 401) {
        if (!isUpdate) {

        }
      } else {
        alert("An error occurred while submitting your response. Please try again. " +
                "If this issue persists, let us know via contact@hackillinois.org.");
      }
      // we only remove the disabled property if
      // there is an error so that the user can re-submit
      $submit.removeProp('disabled');
      if (isUpdate) {
        $submit.html('Update Response');
      } else {
        $submit.html('Respond');
      }
    });
  });

});
