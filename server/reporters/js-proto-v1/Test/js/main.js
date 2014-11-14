/**
 * Created by thomaslynch on 10/16/14.
 * Last Edited: 11/6/14
 */

$(document).ready(function() {

    var table = $('#example').DataTable({
        "dom": 'C<"clear">Rlfrtip',
//        "ajax": "ajax/data/pretty.json",
        "ajax": "http://flux.cs.uwlax.edu/~jjhursey/mtt-tmp/pretty.json",
        "columnDefs": [ {
            "visible": false,
            "targets": -1
        } ],

        "colVis": {
            exclude: [],
            groups: [
                {
                    title: "MPI Install",
                    columns: [6, 7]
                },
                {
                    title: "Test Build",
                    columns: [8, 9]
                },
                {
                    title: "Test Run",
                    columns: [10, 11, 12, 13]
                }
            ],


            "label": function ( index, title, th ) {
                var count = 0;

//                if(title == "pass"){
//                    count++;
//                }
//
//                if(title == "pass" || title == "fail"){
//                    return title + " - " + count;
//                } else {
//                    return title;
//                }

                switch( index ){
                    case 0:
                    case 1:
                    case 2:
                    case 3:
                    case 4:
                    case 5:
                        return title;
                        break;
                    case 6:
                    case 7:
                        return "MPI Install: " + title;
                        break;
                    case 8:
                    case 9:
                        return "Test Build: " + title;
                        break;
                    case 10:
                    case 11:
                    case 12:
                    case 13:
                        return "Test Run: " + title;
                        break;
                    default:
                        return title;
                        break;
                }
            },

            stateChange: function (iColumn, bVisibile){
                console.log(iColumn + " : " + bVisibile);

                //if column is being hidden
                if( !bVisibile ){
                    console.log("This is the data in column to the left of the column that is now hidden");
                    var test = table
                        .column( --iColumn)
                        .data
                        .reduce( function( a, b ) {

                    });
                    console.log( test );
                }

            }
        }

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
