$(function() {
  var checkinDateIndex = 4;
  var datatableOptions = {
    dataUrl: '/admin/checkin/datatable',
    uniqueSearchIdentifier: 'email',
    uniqueSearchUrl: '/admin/search',
    uniqueSearchRedirectUrl: '/admin/checkin/',
    createdRowHandler: function(row, data, index) {
      var rowLength = row.children.length;
      if (data.checkIn) {
        var checkinDate = moment(data.checkIn).format("M/D/YY, h A");
        row.children[rowLength - 1].innerHTML = checkinDate;
      } else {
        row.children[rowLength - 1].innerHTML = 'Never';
      }

      $(row).on('click', function () {
        window.open('/admin/checkin/' + data.id, '_blank');
      });
    },
    order: [],
    columns: [
      {"data": "firstName", "sortable": false},
      {"data": "lastName"},
      {"data": "school", "sortable": false},
      {"data": "graduation"},
      {"data": "organization", "sortable": false, "visible": false },
      {"data": "checkIn", "sortable": false}
    ]
  };

  var $table = initializeDatatable(datatableOptions);

  $('#model').on('change', function (event) {
    var model = event.target.value;
    var isOrganizational = (model.indexOf('SPONSOR') >=0) || (model.indexOf('MENTOR') >= 0);

    var $$table = $('#table');
    $$table.attr('data-model', model);
    $('#select-query')[0].selectedIndex = 0;
    $('#select-query').trigger('change');

    $table.cursor = undefined;
    $table.columns([2, 3]).visible(!isOrganizational);
    $table.column(4).visible(isOrganizational);

    $('#select-query option.organizational').prop('disabled', !isOrganizational);
    $('#select-query option.registered').prop('disabled', isOrganizational);

    $$table.on('draw.dt', function (event, settings) {
      $table.columns.adjust();
      $$table.off('draw.dt');
    });

    $table.columns.adjust().draw();
  });

});
