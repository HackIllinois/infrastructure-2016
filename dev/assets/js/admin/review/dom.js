$(function() {
  var genderIndex = 2;
  var initiativesIndex = 6;
  var registeredIndex = 7;
  var statusIndex = 8;

  var _createdRowHandler = function(row, data, index) {
    var registrationDate = moment(data.registered).format("MMMM DD, YYYY");
    var gender = data.gender;
    var status = data.status;
    var initiatives = data.initiatives;
    var id = data.id;

    $(row).on('click', function () {
      window.open('/admin/review/' + id, '_blank');
    });

    row.children[registeredIndex].innerHTML = registrationDate;
    row.children[initiativesIndex].innerHTML = initiatives.map(function (el) {
      return el.toLowerCase().replace('_', ' ');
    }).join(', ');
    row.children[genderIndex].innerHTML = gender.toLowerCase().replace('_', ' ');
    row.children[statusIndex].innerHTML = status.toLowerCase();

    $(row.children[genderIndex]).addClass('text-capitalize');
    $(row.children[initiativesIndex]).addClass('text-capitalize');
    $(row.children[statusIndex]).addClass('text-capitalize');
    if (status === 'PENDING') {
      $(row.children[statusIndex]).addClass('pending');
    } else if (status === 'ACCEPTED') {
      $(row.children[statusIndex]).addClass('accepted');
    } else if (status === 'WAITLISTED') {
      $(row.children[statusIndex]).addClass('waitlisted');
    } else {
      $(row.children[statusIndex]).addClass('rejected');
    }
  };

  var datatableOptions = {
    dataUrl: '/admin/review/datatable',
    uniqueSearchIdentifier: 'email',
    uniqueSearchUrl: '/admin/search',
    uniqueSearchRedirectUrl: '/admin/review/',
    createdRowHandler: _createdRowHandler,
    order: [7, 'desc'],
    columns: [
      {"data": "firstName", "sortable": false},
      {"data": "lastName"},
      {"data": "gender", "sortable": false},
      {"data": "school", "sortable": false},
      {"data": "graduation"},
      {"data": "major", "sortable": false},
      {"data": "initiatives", "sortable": false},
      {"data": "registered"},
      {"data": "status", "sortable": false},
      {"data": "wave"}
    ]
  };

  initializeDatatable(datatableOptions);

});
