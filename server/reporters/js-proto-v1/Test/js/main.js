/**
 * Created by thomaslynch on 10/16/14.
 * Last Edited: 11/6/14
 */

$(document).ready(function() {

    var table = $('#example').DataTable({
        "dom": 'C<"clear">Rlfrtip',
        "ajax": "ajax/data/pretty.json",
        "columnDefs": [ {
            "visible": false,
            "targets": -1
        } ]
    });

    $('#example tbody').on( 'click', 'tr', function () {
        if ( $(this).hasClass('selected') ) {
            $(this).removeClass('selected');
        }
        else {
            table.$('tr.selected').removeClass('selected');
            $(this).addClass('selected');
        }
    } );

    $('#remove').click( function () {
        table.row('.selected').remove().draw( false );
    } );

//    $( "#remove" ).click( function() {
//       alert("I do a thing!");
//    });






});
