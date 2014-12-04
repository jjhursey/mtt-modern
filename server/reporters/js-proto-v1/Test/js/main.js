/**
 * Created by thomaslynch on 10/16/14.
 * Last Edited: 11/6/14
 */

$(document).ready(function() {

    var hideColList = [];
    var showColList = [];
    var colList =  [];
    var url = "ajax/data/pretty.json";
    //            url: "http://flux.cs.uwlax.edu/~jjhursey/mtt-tmp/pretty.json",


    /*
        Table Configuration
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
        MultiSelect Initialization
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

        console.log( table.data()[0][0]  );
    }



    /*
        MultiSelect Configuration
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
              //Recreate show array
              console.log("Show:");
              showColList = buildNewArray( values, showColList );

              showColList.forEach( function(entry) {
                  console.log(entry);
              });

              //Push to hidden array
              console.log("Hide:");
              hideColList.push( values.toString() );

              hideColList.forEach( function(entry) {
                  console.log(entry);
              });
          },

          afterDeselect: function( values ){
              //Push to show array
              console.log("Now Show:");
              showColList.push( values.toString() );

              showColList.forEach( function(entry) {
                  console.log(entry);
              });

              //Recreate hidden array
              console.log("Now Hide:");
              hideColList = buildNewArray( values, hideColList );

              hideColList.forEach( function(entry) {
                  console.log(entry);
              });
          }

      });
  }

    //TODO: convert strings to indexes
    function getIndexes(){
        //for( var i = 0; i < colList.length){
        //
        //}
    }

    //TODO: Aggregate data
    //TODO: implement button to toggle visibility
    function toggleCols(){

        //for( var i = 0; i < showColList() ){
        //
        //}

            //for all columns in show
                //find column - make visible true
            //for all columns in hide
                //find column - make visible false

        for( var i = 0; i < table.columns; i++ ){

        }


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

    $('#show-hide').click( function () {
        //hideColList.forEach( function(entry){
        //   console.log( entry );
        //});
        fillColList();
    } );




    //dropdown checkbox select
    //populate with current columns
    //






});
