function initializeDatatable(options) {

  // the table setup itself
  var $table = $('#table').DataTable({
    processing: true,
    serverSide: true,
    deferRender: true,
    orderMulti: false, // we have to manually keep track of all indicies
    searching: true,
    lengthMenu: [10, 25, 50],
    pagingType: 'simple',
    dom: '<"row top"' +
      '<"#search-col.col-sm-12">>rt' +
      '<"row bottom"<"col-sm-6"l><"col-sm-6" <"pull-right"p>>>',
    ajax: {
      url: options.dataUrl,
      type: "POST"
    },
    columns: options.columns,
    order: options.order,
    createdRow: options.createdRowHandler
  });

  $table.cursor = undefined;

  // set up our own search solution
  $(document).on('init.dt', function(event, settings) {
    var $searchElement = $('#search').detach();
    $searchElement.appendTo($('#search-col'));
  });

  // keep track of previous table values so that
  // we can discard the cursor when needed
  var prevPage = 0;
  var prevSort = JSON.stringify($table.order());
  var prevLength = $table.page.info().length;
  var direction = 1; // a positive number indicates forward direction

  // set up handlers for various events
  // events are documented on datatables.net
  $('#table').on('preXhr.dt', function(event, settings, data) {
    var pageInfo = $table.page.info();
    var length = pageInfo.length;
    var sort = JSON.stringify(settings.aaSorting);

    var sendCursor = true;
    if (prevSort !== sort || prevLength != length) {
      // sort changed or length changed
      sendCursor = false;
    } else if (pageInfo.page < prevPage) {
      // direction changed from forward to backward
      // (reset may not be needed)
      if (direction > 0) sendCursor = false;
      direction = -1;
    } else {
      // direction changed from backward to forward
      // (reset may not be needed)
      if (direction < 0) sendCursor = false;
      direction = 1;
    }

    // update previous values
    prevPage = pageInfo.page;
    prevLength = length;
    prevSort = sort;

    data.page = prevPage;
    data.model = $('#table').attr('data-model');
    if (sendCursor) {
      data.cursor = $table.cursor;
    } else {
      $table.cursor = undefined;
      direction = 1;
    }
  }).on('xhr.dt', function(event, settings, json, xhr) {
    if (json) $table.cursor = json.cursor;
  });

  // handle selection of the different query filters
  $('#select-query').on('change', function(event) {
    var value = event.target.value;
    var $query = $('#search-query');
    var $submit = $('#query-action');

    // reset everything to start
    $query.parent().removeClass('has-error');
    $table.search('').columns().search('');
    if (!value) {
      $query.addClass('hidden');
      $query.val('');
      $submit.html("Refresh");
    } else {
      $query.removeClass('hidden');
      $submit.html("Search");
    }
  });

  // handle the submission of the query input
  $('#search').on('submit', function(event) {
    event.preventDefault();

    var $submit = $('#query-action');
    var $querySelect = $('#select-query');
    var $query = $('#search-query');
    var queryColumn = $querySelect.val();
    var query = $query.val();

    $query.parent().removeClass('has-error');
    if (!queryColumn) $table.search('').columns().search('').draw();
    if (!query || !query.trim().length) return;
    if (queryColumn === options.uniqueSearchIdentifier) {
      // we want to provide the ability to search by a unique value,
      // but listing this value as a column is often not viable
      $submit.prop('disabled', true);
      $.ajax({
        url: options.uniqueSearchUrl,
        data: {
          query: query
        },
        complete: function() {
          $submit.prop('disabled', false);
        }
      }).then(function(result, textStatus, jqXHR) {
        if (!result.error) {
          window.open(options.uniqueSearchRedirectUrl + result.data.id, '_blank');
          return;
        }

        $query.parent().addClass('has-error');
      }, function(jqXHR, textStatus, errorThrown) {
        alert("A back-end error occurred. Please try again.");
      });
    } else {
      queryColumn = parseInt(queryColumn);
      $table.cursor = undefined;
      $table.column(queryColumn).search(query).draw();
    }
  });

  return $table;
}
