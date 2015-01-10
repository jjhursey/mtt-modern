/**
 * Created by thomaslynch on 10/16/14.
 * Last Edited: 11/6/14
 */

$(document).ready(function() {

    var colList =  [];
    var hideColList = [];
    var showColList = [];


    //TODO: make checkCols dynamic
    var stringCols = [];
    var intCols = [];

    var showStrColList = [];

    var url = "ajax/data/pretty.json";
    //var url = "http://flux.cs.uwlax.edu/~jjhursey/mtt-tmp/pretty.json";


    /*
     ****************************************************
        Table Configuration
     ****************************************************
     */
    var table = $('#example').DataTable({
        //"dom": 'C<"clear">Rlrtip',   l = amount per page
        "dom": '<"top">Rrtp<"bottom"li><"clear">',
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

    //phase extra search
    function phaseChange( phase ){
        removeTables();

        switch( phase ){
            case "all":;
                break;
            case "install":
                addTables( "install" );
                break;
            case "build":
                addTables( "build" );
                break;
            case "run":
                addTables( "run" );
                break;
            default:
                break;
        }

        //addTables
        //update show/hide
        //reload table
    }

    function removeTables(){
        $( '.col2 > table' ).remove();
    }

    function addTables( phase ){
        var newColumns;
        var sqlTable = "<table cellpadding='1' cellspacing='0' border='0'>" +
                            "<tr class='blankrow' ></tr>";
        var advTable;

        var filterTable =
                "<table cellpadding='1' cellspacing='0' border='0'>" +
                    "<thead> <tr> <th>Target</th> <th>Search Text</th> <th>Regex</th> <th>Smart</th> </tr> </thead>" +
                    "<tbody>";

        switch( phase ){
            case "all":
                break;
            case "install":
                newColumns = [ "Configure args", "Compiler", "Bitness", "Endian" ];


                sqlTable = buildSqlTableString( newColumns, sqlTable );
                filterTable = buildFilterTableString( newColumns, filterTable  );

                $( 'div#sqlbox > div#columnwrapper > .col2' ).append( sqlTable );
                $( 'div#filterbox > .col2' ).append( filterTable );
                $( 'div #filtertoolbar2').append( '&nbsp;' );

                break;
            case "build":
                newColumns = [ "Suite", "Compiler", "Compiler ver.", "Bitness" ];


                sqlTable = buildSqlTableString( newColumns, sqlTable )
                filterTable = buildFilterTableString( newColumns, filterTable );

                $( 'div#sqlbox > div#columnwrapper > .col2' ).append( sqlTable );
                $( 'div#filterbox > .col2' ).append( filterTable );
                $( 'div #filtertoolbar2').append( '&nbsp;' );

                break;
            case "run":
                newColumns = [ "Suite", "Test", "np", "Command" ];

                sqlTable = buildSqlTableString( newColumns, sqlTable );
                filterTable = buildFilterTableString( newColumns, filterTable );

                $( 'div#sqlbox > div#columnwrapper > .col2' ).append( sqlTable );
                $( 'div#filterbox > .col2' ).append( filterTable );
                $( 'div #filtertoolbar2').append( '&nbsp;' );

                break;
            default:
                break;
        }
    }

    function buildSqlTableString( newColumns, table ){
        for( var i = 7; i < 11; i++ ){
            table +=
                "<tr>" +
                    "<td>" + newColumns[ i-7 ] + "</td>" +
                    "<td align='center'>" +
                    "<td> <input type='text' name='sqltext' value='all' > </td>" +
                    "<td>" +
                        "<select name = 'display'>" +
                            "<option value='show'> Show </option>" +
                            "<option value='hide'> Hide </option>" +
                        "</select>" +
                    "</td>" +
                "</tr>"
            ;
        }
        return table;
    }

    function buildFilterTableString( newColumns, table ){
        for( var i = 7; i < 11; i++ ){
            var dc = "" + (i - 1);
            var id1 = "filter_col" + i;
            var id2 = "col" + i + "_filter";
            var id3 = "col" + i + "_regex";
            var id4 = "col" + i + "_smart";


            table +=
                "<tr id='" + id1 + "' data-column='" + dc + "'>" +
                "<td> " + newColumns[ i-7 ] + " </td>" +
                "<td align='center'><input type='text' class='column_filter' id='" + id2 + "'></td>" +
                "<td align='center'><input type='checkbox' class='column_filter' id='" + id3 + "'></td>" +
                "<td align='center'><input type='checkbox' class='column_filter' id='" + id4 + "' checked='checked'></td>" +
                "</tr>";
        }
        return table;
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
      MultiSelect and Aggregation Configuration
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
    function toggleCols() {
        console.time( " Total Completion Time" );

        showStrColList = [];
        var aggregate = false;
        var refresh = false;


        for (var i = 0; i < colList.length; i++) {
            var selected = table.column(i).header();

            for (var j = 0; j < showColList.length; j++) {
                if ($(selected).html() === showColList[j]) {
                    var column = table.column(i);
                    if (column.visible() === false) {
                        refresh = true;
                    }
                    column.visible(true);
                }
            }

            for (var k = 0; k < hideColList.length; k++) {
                if ($(selected).html() === hideColList[k]) {
                    var column = table.column(i);
                    if (column.visible() === true) {
                        aggregate = true;
                    }
                    column.visible(false);
                }
            }

        }

        fillShowStrColList();
        if (aggregate) {
            aggregateData();
        }

        if( refresh ){
            table.ajax.reload(aggregateData);
        }

    }

    //TODO: reload with cache
    function aggregateData(){
        console.time( "Time spent aggregating" );

        var skiprows = [];
        var deleterows = [];

        table.rows().iterator('row', function( context, index ){
            var rrow;
            var lrow;
            var lstring = "";
            var rstring = "";

            //grab left hand of comparison
            lrow = this.row( index );

            for ( var i = 0; i < showStrColList.length; i++ ){
                lstring += this.row( index ).data()[ colList.indexOf( showStrColList[i] ) ] + ", ";
            }

            //console.log(lstring);
            //grab right hand of comparison
            table.rows().iterator( 'row', function( content, index2 ){
                //console.log( index2 + "  > " + index );
                if( index2 > index ) {
                    rrow = this.row(index2);
                    rstring = "";

                    for (var i = 0; i < showStrColList.length; i++) {
                        rstring += this.row(index2).data()[ colList.indexOf( showStrColList[i] ) ] + ", ";
                    }

                    //compare
                    //console.log(lstring + " vs " + rstring );
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
            //console.log("DELETING:" + i + ": " + table.row( deleterows[i] ).data());
            table.row( deleterows[i] ).remove();
        }

        table.draw();
        console.timeEnd( "Time spent aggregating" );
        console.timeEnd( " Total Completion Time" );
    }


    /*
     ****************************************************
     Extra button functions
     ****************************************************
     */

    function toggleCheckbox( selector ){
        if( $( selector ).is(':checked') ){
            $( selector ).prop('checked', false);
        } else {
            $( selector ).prop('checked', true);
        }
    }



    /*
     ****************************************************
     Date Range
     ****************************************************
     */

    //typeahead
    var substringMatcher = function(strs) {
        return function findMatches(q, cb) {
            var matches, substrRegex;

            // an array that will be populated with substring matches
            matches = [];

            // regex used to determine if a string contains the substring `q`
            substrRegex = new RegExp(q, 'i');

            // iterate through the pool of strings and for any string that
            // contains the substring `q`, add it to the `matches` array
            $.each(strs, function(i, str) {
                if (substrRegex.test(str)) {
                    // the typeahead jQuery plugin expects suggestions to a
                    // JavaScript object, refer to typeahead docs for more info
                    matches.push({ value: str });
                }
            });

            cb(matches);
        };
    };

    var dates = [
        'today', 'yesterday', 'past 12 hours', 'past 24 hours',
        'past 2 days', 'past 3 days', 'past week', 'past 2 weeks'
    ];

    $('.typeahead').typeahead({
            hint: true,
            highlight: true,
            minLength: 1
        },
        {
            name: 'dates',
            displayKey: 'value',
            source: substringMatcher(dates)
        });

    //moment
    moment.invalid( );

    function getDate( date ){
        var index = dates.indexOf( date );

        if( index >= 0 ){
            var dates2 = [
                moment().startOf('day'),
                moment().subtract( 1, 'days' ).hours(0).minutes(0).seconds(0),
                moment().subtract(12, 'hours'),
                moment().subtract(24, 'hours'),
                moment().subtract( 2, 'days' ),
                moment().subtract( 3, 'days' ),
                moment().subtract( 7, 'days' ),
                moment().subtract( 14, 'days' )
            ];

            return dates2[ index ].format('YYYY-MM-DD hh:mm:ss');
        } else {
            return Moment(date).format('YYYY-MM-DD hh:mm:ss');
        }

    }


    /*
     ****************************************************
     Event Listeners
     ****************************************************
     */

    //filters
    $('input.global_filter').on( 'keyup click', function () {
        filterGlobal();
    } );

    $('input.column_filter').on( 'keyup click focus', function () {
        filterColumn( $(this).parents('tr').attr('data-column') );
    } );


    //CSS Row selection
    var tableSelector = '#example tbody';
    $( tableSelector ).on( 'click', 'tr', function () {
        table.$('tr.selected').removeClass('selected');
        $(this).addClass('selected');
    } );

    $( tableSelector ).on( 'dblclick', 'tr', function () {
        if ( $(this).hasClass('selected') ) {
            $(this).removeClass('selected');
        }
    });

    //Drill Down - grab td cell data
    $( tableSelector ).on( 'click', 'td', function () {
        table.$('td.selected').removeClass('selected');
        $(this).addClass('selected');

        if( !$('#filterbox').is(":visible") ){
            $( '#settingsbox').hide( "slow" );
            $( '#sqlbox').hide("slow");
            $( '#filterbox').show( "slow" );
        }

        var id = "#col" + $(this).index() + "_filter";

        if( $(id).val() === table.cell(this).data() ){
            $(id).val("");
            $(id).focus();
        } else {
            $(id ).val( table.cell(this).data() );
            $(id).focus();
        }
    } );

    $( tableSelector ).on( 'dblclick', 'td', function () {
        if ( $(this).hasClass('selected') ) {
            $(this).removeClass('selected');
        }
    });



    //Column show/hide toggle
    $('#show-hide').click( function(){
        toggleCols();
        console.log(" ");
    } );

    //Phase Selection
    $( "select[name=phases]").on( 'change', function(){
            phaseChange( $( "select option:selected").attr('value') );
    });


    //Window Selection
    $('#sql').on( 'click', function(){
        if( $( '#sqlbox').is(":visible") ){
            $( '#sqlbox').hide("slow");
        } else {
            $( '#filterbox').hide( "slow" );
            $( '#settingsbox').hide( "slow" );
            $( '#sqlbox').show("slow");
        }
    });

    $('#filter').on( 'click', function(){
        if( $('#filterbox').is(":visible") ){
            $( '#filterbox').hide( "slow" );
        } else {
            $( '#settingsbox').hide( "slow" );
            $( '#sqlbox').hide("slow");
            $( '#filterbox').show( "slow" );
        }
    });

    $('#settings').on( 'click', function(){
        if( $('#settingsbox').is(":visible") ){
            $( '#settingsbox').hide( "slow" );
        } else {
            $( '#sqlbox').hide("slow");
            $( '#filterbox').hide( "slow" );
            $( '#settingsbox').show( "slow" );
        }
    });

    //SQL buttons

    $('#sqltoolbar1 > button[value=startover]').on( 'click', function(){
        $( 'select[name^=dates] option[value="24hrs"]').attr("selected","selected");

        $( 'input[name=sqltext]').val('all');

        $( 'select[name^=display] option[value=show]').attr("selected","selected");
        $( 'select[name^=display2] option[value=hide]').attr("selected","selected");
            //$('select[name^="salesrep"] option[value="Bruce Jones"]').attr("selected","selected");
    });

    $( 'button[value=summary]' ).on( 'click', function(){
        var date = $( 'input[id=dates]' ).val();
        var endTime = moment().format('YYYY-MM-DD hh:mm:ss');

        if( moment(date).isValid() ){
            var startTime = getDate( date );
            console.log("Date Range: " + startTime + " to " + endTime );
        } else {
            console.log( "Invalid Date" );
        }

        //console.log( "Org: " + $( 'input[id=org]' ).val() );
        //console.log( "Local Username: " + $( 'input[id=localusername]' ).val() );
        //console.log( "Platform Name: " + $( 'input[id=platform_name]' ).val() );
        //console.log( "Hardware: " + $( 'input[id=platform_hardware]' ).val() );
        //console.log( "OS: " + $( 'input[id=os_name]' ).val() );
        //console.log( "MPI Name: " + $( 'input[id=mpi_name]' ).val() );
        //console.log( "MPI Version: " + $( 'input[id=mpi_version]' ).val() );


    });


    //Filter buttons
    $( 'button[value=clearf]' ).on( 'click', function(){
        $( 'input[type=text][class=column_filter]' ).val('').focus().blur();
    });
    $( 'button[value=toggler]' ).on( 'click', function(){
        toggleCheckbox( 'input[type=checkbox][class=column_filter][id*=regex]' );
    });
    $( 'button[value=toggles]' ).on( 'click', function(){
        toggleCheckbox( 'input[type=checkbox][class=column_filter][id*=smart]' );
    });
    $( 'button[value=resetf]' ).on( 'click', function(){
        $( 'input[type=text][class=column_filter]' ).val('').focus().blur();
        $( 'input[type=checkbox][class=column_filter][id*=regex]').prop("checked", false);
        $( 'input[type=checkbox][class=column_filter][id*=smart]').prop("checked", true);
    });


    //Preference buttons




    /*
     ****************************************************
     Performance
     ****************************************************
     */

    SpeedTest.prototype = {
        startTest: function(){
            var beginTime, endTime;
            beginTime = +new Date();

            this.testImplement( this.testParams );
            endTime = +new Date();

            timeSpent = endTime - beginTime;

            return console.log( timeSpent + "(" + this.testedFunction + ")"  );
        }
    }

    function SpeedTest( testImplement, testParams, testedFunction ) {
        this.testImplement = testImplement;
        this.testParams = testParams;
        this.testedFunction = testedFunction;
    }

    //var aggregateTest = new SpeedTest(  )



});
