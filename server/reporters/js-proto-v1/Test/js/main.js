/**
 * Created by thomaslynch on 10/16/14.
 * Last Edited: 11/6/14
 */

$(document).ready(function() {

    var colList =  [];
    var hideColList = [];
    var showColList = [];

    var checkCols =
        [
            "Org",
            "Platform name",
            "Hardware",
            "OS",
            "MPI Name",
            "MPI Version"
        ];

    //var url = "ajax/data/pretty.json";
    var url = "http://flux.cs.uwlax.edu/~jjhursey/mtt-tmp/pretty.json";


    /*
     ****************************************************
        Table Configuration
     ****************************************************
     */
    var table = $('#example').DataTable({
        "dom": 'C<"clear">Rlfrtip',
        "ajax": {
            url: url,
            dataSrc: "values"
        },
        "columnDefs": [ {
            "visible": false,
            "targets": -1
        } ],

        "colVis": {
            exclude: [],
            restore: "Restore",
            showAll: "Show All",
            showNone: "Show None",
            "buttonText": "Change columns",

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

                if( title == "Pass" ){
                    count++;
                }

                if( title == "Pass" || title == "Fail" ){
                    return title + " - " + count;
                } else {
                    return title;
                }
                //TODO: Make label dynamic
            },

            stateChange: function (iColumn, bVisibile){
                console.log(iColumn + " : " + bVisibile);

//                if column is being hidden
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

    //TODO: dynamic table headers
    function setHeaders( columnName ){
        //var input = "<th rowspan=\"2\">" + columnName + "</th>";
        //$( "#example" ).append( input );
    }


    /*
     ****************************************************
      MultiSelect Initialization
     ****************************************************
     */

    $.ajax({
        dataType: "json",
        url: url
    })
        .done( function( data ){
              for( var i = 0; i < data.fields.length; i++ ){
                  setHeaders( data.fields[i] );
                  colList.push( data.fields[i] );
                  showColList.push( data.fields[i] );
              }

            fillColList();
            buildSelect();
        });

    function fillColList(){
        for( var i = 0; i < colList.length; i++  ) {
            var name = colList[i];
            var input = "<option value\"" + name + "\">" + name + "</option>";
            $('#my-select').append( input );
        }
    }


    /*
     ****************************************************
      MultiSelect Configuration
     ****************************************************
     */
    function buildNewArray ( values, arr ){
        var tmpArray = arr;
        arr = [];

        tmpArray.forEach( function(entry) {
            if( values.toString() !== entry.toString() ){
                arr.push( entry );
            }
        });

        return arr;

    }

    function  buildSelect(){
      $('#my-select').multiSelect({
          selectableHeader: "<div class='custom-header'> Show Columns </div>",
          selectionHeader: "<div class='custom-header'> Hide Columns </div>",

          afterSelect: function( values ){
              //push and recreate
              showColList = buildNewArray( values, showColList );
              hideColList.push( values.toString() );
          },

          afterDeselect: function( values ){
              //push and recreate
              showColList.push( values.toString() );
              hideColList = buildNewArray( values, hideColList );
          }

      });
  }

    //TODO: Aggregate data
    //TODO: fix extra test/fails
    function toggleCols(){
        console.log( table.search( "OS" ) );

        for( var i = 0; i < colList.length; i++ ){
            var selected = table.column(i).header();

            for( var j = 0; j < showColList.length; j++ ){
                if( $(selected).html() === showColList[j] ){
                    table.columns(i).visible( true );
                }
            }

            for( var k = 0; k < hideColList.length; k++ ){
                if( $(selected).html() === hideColList[k] ){
                    table.columns(i).visible( false );
                    aggregateData();
                }
            }

        }
    }

    function aggregateData(){


    }



    $('#example tbody').on( 'click', 'tr', function () {
        if ( $(this).hasClass('selected') ) {
            $(this).removeClass('selected');
        }
        else {
            table.$('tr.selected').removeClass('selected');
            $(this).addClass('selected');
        }
    } );

    $( 'button[ name = "Change columns" ]' ).on( 'click', function(){
        alert( "Hey! I was hit!!!" );
    } );

    $('#show-hide').click( function(){
        toggleCols();
    } );


});
