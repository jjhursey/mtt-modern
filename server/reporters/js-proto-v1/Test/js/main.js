/**
 * Created by thomaslynch on 10/16/14.
 * Last Edited: 11/6/14
 */

$(document).ready(function() {

    var colList =  [];
    var hideColList = [];
    var showColList = [];


    //TODO: make checkCols dynamic
    //currently column names - needs to populate based on string/int check
    var stringCols = [];
    var intCols = [];

    var showStrColList = [];

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
      Search Initialization
     ****************************************************
     */
    function filterGlobal () {
        $('#example').DataTable().search(
            $('#global_filter').val(),
            $('#global_regex').prop('checked'),
            $('#global_smart').prop('checked')
        ).draw();
    }

    function filterColumn ( i ) {
        $('#example').DataTable().column( i ).search(
            $('#col'+i+'_filter').val(),
            $('#col'+i+'_regex').prop('checked'),
            $('#col'+i+'_smart').prop('checked')
        ).draw();
    }

    $('input.global_filter').on( 'keyup click', function () {
        filterGlobal();
    } );

    $('input.column_filter').on( 'keyup click', function () {
        filterColumn( $(this).parents('tr').attr('data-column') );
    } );

    //phase extra search

    function phaseChange( phase ){
        for(var i = 7; i < 11; i++){
            $( ('#filter_col' + i) ).remove();
        }

        //addColumn
        //update show/hide
        //reload table


        switch( phase ){
            case "all":;
                break;
            case "install":
                addCenter( "install" );
                break;
            case "build":
                addCenter( "build" );
                break;
            case "run":
                addCenter( "run" );
                break;
            default:
                break;
        }
    }

    function addCenter( phase ){
        var newColumn = "";
            //" <div id='center'> " +
                //"<table cellpadding='1' cellspacing='0' border='0'>" +
            //        "<thead>" +
            //            "<tr>" +
            //                "<th>Target</th>" +
            //                "<th>Search text</th>" +
            //                "<th>Regex</th>" +
            //                "<th>Smart</th>" +
            //            "</tr>" +
            //        "</thead>" +
            //        "<tbody>";

        switch( phase ){
            case "all":
                break;
            case "install":
                newColumn +=
                    "<tr id='filter_col7' data-column='6'>" +
                        "<td> Configure arguments </td>" +
                        "<td align='center'><input type='text' class='column_filter' id='col6_filter'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col6_regex'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col6_smart' checked='checked'></td>" +
                    "</tr>" +
                    "<tr id='filter_col8' data-column='7'>" +
                        "<td> Compiler </td>" +
                        "<td align='center'><input type='text' class='column_filter' id='col7_filter'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col7_regex'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col7_smart' checked='checked'></td>" +
                    "</tr>" +
                    "<tr id='filter_col9' data-column='8'>" +
                        "<td> Bitness </td>" +
                        "<td align='center'><input type='text' class='column_filter' id='col8_filter'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col8_regex'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col8_smart' checked='checked'></td>" +
                    "</tr>" +
                    "<tr id='filter_col10' data-column='9'>" +
                        "<td> Endian </td>" +
                        "<td align='center'><input type='text' class='column_filter' id='col9_filter'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col9_regex'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col9_smart' checked='checked'></td>" +
                    "</tr>"
                ;

                //newColumn += "</tbody></table></div>";
                //$( '#leftcolumn').after( newColumn );
                $( '#search table').append( newColumn );
                break;
            case "build":
                newColumn +=
                    "<tr id='filter_col7' data-column='6'>" +
                        "<td> Suite </td>" +
                        "<td align='center'><input type='text' class='column_filter' id='col6_filter'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col6_regex'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col6_smart' checked='checked'></td>" +
                    "</tr>" +
                    "<tr id='filter_col8' data-column='7'>" +
                        "<td> Compiler </td>" +
                        "<td align='center'><input type='text' class='column_filter' id='col7_filter'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col7_regex'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col7_smart' checked='checked'></td>" +
                    "</tr>" +
                    "<tr id='filter_col9' data-column='8'>" +
                        "<td> Compiler version </td>" +
                        "<td align='center'><input type='text' class='column_filter' id='col8_filter'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col8_regex'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col8_smart' checked='checked'></td>" +
                    "</tr>" +
                    "<tr id='filter_col10' data-column='9'>" +
                        "<td> Bitness </td>" +
                        "<td align='center'><input type='text' class='column_filter' id='col9_filter'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col9_regex'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col9_smart' checked='checked'></td>" +
                    "</tr>"
                ;

                //newColumn += "</tbody></table></div>";
                //$( '#leftcolumn').after( newColumn );
                $( '#search table').append( newColumn );
                break;
            case "run":
                newColumn +=
                    "<tr id='filter_col7' data-column='6'>" +
                        "<td> Suite </td>" +
                        "<td align='center'><input type='text' class='column_filter' id='col6_filter'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col6_regex'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col6_smart' checked='checked'></td>" +
                    "</tr>" +
                    "<tr id='filter_col8' data-column='7'>" +
                        "<td> Test </td>" +
                        "<td align='center'><input type='text' class='column_filter' id='col7_filter'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col7_regex'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col7_smart' checked='checked'></td>" +
                    "</tr>" +
                    "<tr id='filter_col9' data-column='8'>" +
                        "<td> np </td>" +
                        "<td align='center'><input type='text' class='column_filter' id='col8_filter'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col8_regex'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col8_smart' checked='checked'></td>" +
                    "</tr>" +
                    "<tr id='filter_col10' data-column='9'>" +
                        "<td> Command </td>" +
                        "<td align='center'><input type='text' class='column_filter' id='col9_filter'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col9_regex'></td>" +
                        "<td align='center'><input type='checkbox' class='column_filter' id='col9_smart' checked='checked'></td>" +
                    "</tr>"
                ;

                //newColumn += "</tbody></table></div>";
                //$( '#leftcolumn').after( newColumn );
                $( '#search table').append( newColumn );
                break;
            default:
                break;
        }
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

            //TODO: check string/int columns
            for( var i = 0; i < colList.length; i++ ){
                if( i < 6 ){
                    stringCols.push( colList[i] );
                } else {
                    intCols.push( colList[i] );
                }
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

    function buildSelect(){
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


    //fill with strings that are both in strCols and showCols
    function fillShowStrColList(){
        for( var i = 0; i < showColList.length; i++) {
            if( stringCols.indexOf( showColList[i] ) >= 0 ){
                showStrColList.push( showColList[i] );
            }
        }

        showStrColList.sort( function( a,b ){ return a-b; } )
    }

    //TODO: Aggregate data
    //TODO: fix extra test/fails
    //NOTE: extra test/fails with have additional text in showColList and hideColList than colList
    function toggleCols(){
        showStrColList = [];
        var aggregate = false;
        var wait = false;


        for( var i = 0; i < colList.length; i++ ){
            var selected = table.column(i).header();

            for( var j = 0; j < showColList.length; j++ ){
                if( $(selected).html() === showColList[j] ){
                    var column = table.column(i);
                    if( column.visible() === false ) {
                        table.ajax.reload( aggregateData );
                    }
                    column.visible(true);
                }
            }

            for( var k = 0; k < hideColList.length; k++ ){
                if( $(selected).html() === hideColList[k] ){
                    var column = table.column(i);
                    if( column.visible() === true ){
                        aggregate = true;
                    }
                    column.visible( false );
                }
            }

        }

        fillShowStrColList();
        if( aggregate ) {
            aggregateData();
        }
    }

    //TODO: reload with cache
    function aggregateData(){
        var skiprows = [];
        var deleterows = [];

        console.log("hit");

        table.rows().iterator('row', function( context, index ){
            console.log("hit");
            var rrow;
            var lrow;
            var lstring = "";
            var rstring = "";

            //grab left hand of comparison
            lrow = this.row( index );

            for(var i = 0; i < showStrColList.length; i++ ){
                lstring += this.row( index ).data()[ colList.indexOf( showStrColList[i] ) ] + ", ";
            }

            console.log(lstring);
            //grab right hand of comparison
            table.rows().iterator( 'row', function( content, index2 ){
                console.log( index2 + "  > " + index );
                if( index2 > index ) {
                    rrow = this.row(index2);
                    rstring = "";

                    for (var i = 0; i < showStrColList.length; i++) {
                        rstring += this.row(index2).data()[ colList.indexOf( showStrColList[i] ) ] + ", ";
                    }

                    //compare
                    console.log(lstring + " vs " + rstring );
                    if ( lstring === rstring && skiprows.indexOf( lstring ) < 0 ) {
                        //make new dataset
                        var newData = lrow.data();

                        //for all int columns add them up!
                        for (var i = 0; i < intCols.length; i++) {
                            var idx = colList.indexOf(intCols[i]);
                            newData[idx] = parseInt( newData[idx] ) + parseInt( rrow.data()[idx] );
                        }

                        lrow.data(newData);
                        //console.log("PUSH TO DELETE: " + rrow.data() );
                        deleterows.push( index2 );

                    }
                }

            });

            if( skiprows.indexOf( lstring ) < 0 ){
                //console.log("BANISHING: " + lstring);
                skiprows.push( lstring );
            }
        });

        //delete rows
        deleterows.sort( function( a,b ){ return a-b; } )

        for( var i = deleterows.length - 1; i >= 0; i-- ){
            console.log("DELETING:" + i + ": " + table.row( deleterows[i] ).data());
            table.row( deleterows[i] ).remove();
        }

        table.draw();
    }


    /*
     ****************************************************
     Event Listeners
     ****************************************************
     */

    //Row selection
    $('#example tbody').on( 'click', 'tr', function () {
        if ( $(this).hasClass('selected') ) {
            $(this).removeClass('selected');
        }
        else {
            table.$('tr.selected').removeClass('selected');
            $(this).addClass('selected');
        }
    } );

    //Column show/hide toggle
    $('#show-hide').click( function(){
        toggleCols();
    } );

    //radio buttons
    $( "input[type=radio][name=phase]" ).on( 'change', function (){
        if( $(this).is(':checked') ) {
            phaseChange( $(this).attr('value') );
        }
    });



});
