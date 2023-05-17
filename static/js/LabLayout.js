$(document).ready(function(){
    $("#userDetails").DataTable({
    "responsive":true,
    columnDefs:[
                {'targets':0,'searchable':true,'orderable':false,'visible':true},
                {'targets':1,'searchable':true,'orderable':true,'visible':true},
                {'targets':2,'searchable':true,'orderable':true,'visible':true},
                {'targets':3,'searchable':true,'orderable':true,'visible':true},
                {'targets':4,'searchable':true,'orderable':true,'visible':true},
                {'targets':5,'searchable':false,'orderable':false, 'visible':true}
                 ],
    dom: 'lBfrtip',
    buttons: [
                  {extend: 'excelHtml5'},
                  {
                  extend: 'pdfHtml5',
                  orientation: 'landscape',
                  pageSize: 'LEGAL'
                  }
             ],
    "order": [[ 2, "asc" ]],
    });
    var t= $("#tbl").DataTable({
        "sScrollX": "100%",
        "bScrollCollapse": true,
        columnDefs:[
                    {'targets':2,'searchable':false,'orderable':true,'visible':true},
                    {'targets':3,'searchable':false,'orderable':true,'visible':true},
                    {'targets':4,'searchable':false,'orderable':true}
                 ],

        dom: 'lBfrtip',
        buttons: [
                      {
                           extend: 'excel',
                           title:"",
                           exportOptions: {
                                    columns: [':visible']
                                    //columns: ':not(.not-export-col)'
                                    },
                            footer: false
                        },
                ],
        "order": [[ 2, "asc" ]],
    });

    var t= $("#tblod").DataTable({
        "sScrollX": "100%",
        "bScrollCollapse": true,
        columnDefs:[
                    {'targets':1,'searchable':false,'orderable':false,'visible':true, 'width':"Auto"},
                    {'targets':2,'searchable':false,'orderable':false,'visible':true, 'width':"Auto"},
                    {'targets':3,'searchable':false,'orderable':false,'visible':true, 'width':"Auto"},
                    {'targets':4,'searchable':false,'orderable':false,'visible':true, 'width':"Auto"},
                    {'targets':5,'searchable':false,'orderable':false, 'width':"Auto"}
                 ],

        dom: 'lBfrtip',
        buttons: [
                      {
                           extend: 'excel',
                           title:"",
                           exportOptions: {
                                    columns: [':visible']
                                    //columns: ':not(.not-export-col)'
                                    },
                            footer: false
                        },
                ],
        "order": [[ 2, "asc" ]],
    });
    <!--t.on( 'order.dt search.dt', function () {-->
        <!--t.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {-->
            <!--cell.innerHTML = i+1;-->
        <!--} );-->
    <!--} ).draw();-->
  });
