/**
* Created by thomaslynch on 10/16/14.
* Last Edited: 11/6/14
*/

//1424

/*
    Where you left off:
        - Confusing query not sending request. Might be due to load priorities or initialization timing.
        - Show/Hide not populating.
        - Not receiving values for Test run query
        - fix CSS
        - implement more Handlebars
*/

$(document).ready(function() {
    /*
     ****************************************************
     BEGIN VARIABLE DECLARATION
     ****************************************************
     */

    //TODO: bitness drilldown exception
    //TODO: change dropdown options to match POST settings (all switch statements here...)
    //TODO: Change state with start over button ( w/ automatic query )
    //TODO: save last json request to compare - possibly use cache ( e.g. when hiding datatable )

    var ns = {
        currentPhase: "all",
        /*sql*/state: "true",
        startMoment: 0,
        endMoment: 0
    };

    //Constants
    var ALLLIST = [
        "http_username",
        //"local_username",
        "platform_name",
        "platform_hardware",
        "os_name",
        "mpi_name",
        "mpi_version",
    ];
    var INSTALLLIST = [
        "http_username",
        //"local_username",
        "platform_name",
        "platform_hardware",
        "os_name",
        "mpi_name",
        "mpi_version",
        "bitness",
        "endian",
        "compiler_name"
    ];
    var BUILDRUNLIST = [
        "http_username",
        //"local_username",
        "platform_name",
        "platform_hardware",
        "os_name",
        "mpi_name",
        "mpi_version",
        "bitness",
        "compiler_name",
        "compiler_version",
        "test_suite_name"
    ];

    var AIDETAILLIST = [
        "http_username",
        "platform_name",
        "platform_hardware",
        "os_name",
        "mpi_name",
        "mpi_version",
        "bitness",
        "endian",
        "compiler_name",
        "vpath_mode",
        "compiler_version",
        "configure_arguments",
        "description",
        "exit_value",
        "exit_signal",
        "duration",
        "result_message",
        "result_stdout",
        "result_stderr",
        "environment"
    ];
    var TBDETAILLIST = [
        "http_username",
        "platform_name",
        "platform_hardware",
        "os_name",
        "mpi_name",
        "mpi_version",
        "bitness",
        "compiler_name",
        "compiler_version",
        "test_suite_name",
        "description",
        "exit_value",
        "exit_signal",
        "duration",
        "result_message",
        "result_stdout",
        "result_stderr",
        "environment"
    ];
    var TRDETAILLIST = [
        "http_username",
        "platform_name",
        "platform_hardware",
        "os_name",
        "mpi_name",
        "mpi_version",
        "test_suite_name",
        "test_name",
        "np",
        "full_command",
        "launcher",
        "resource_mgr",
        "parameters",
        "network",
        "description",
        "exit_value",
        "exit_signal",
        "duration",
        "result_message",
        "result_stdout",
        "result_stderr",
        "environment"
    ];

    var REQUESTFORMAT = 'YYYY-MM-DD hh:mm:ss a';

    //for datepicker
    var start = $( "#startdate" );
    var end = $( "#enddate" );

    //
    var colList =  [];
    var showColList = [];
    var hideColList = [];

    var stringCols = [
        //"http_username",
        //"platform_name",
        //"platform_hardware",
        //"os_name",
        //"mpi_name",
        //"mpi_version",
        //"mpi_install.compiler_name"
    ];
    var intCols = [
        //"mpi_install_pass",
        //"mpi_install_fail",
        //"test_build_pass",
        //"test_build_fail",
        //"test_run_pass",
        //"test_run_fail",
        //"test_run_skip",
        //"test_run_timed",
        //"bitness",
        //"endian"
    ];

    var showStrColList = [];

    var table;
    var fields;
    var values;

    var startMoment;
    var endMoment;

    var lastJSON = {};
    var reqLimit = 25;

    var currentPhase = "all";
    /*
     ****************************************************
     END VARIABLE DECLARATION
     ****************************************************
     */

    // Site Initilization

    (function init( ){
        dateInit();
        fillColList( colList );

        paginationInit();
        countInit();
        $('#details').hide();

        buildSelect();
        //buildTable();
        pullValues( "summary" );
    })();

    function dateInit(){
        var tempstart = new Date(2014, 10, 29, 0, 0, 0);

        //set dropdown menu
        $( 'select[name=dates]' ).val( 'past2weeks' );

        var absoluteMin = new Date(2011, 0, 1);
        var absoluteMax = new Date(2014, 9, 29);

        //datepicker configuration
        start.datepicker({
            minDate: absoluteMin,
            maxDate: absoluteMax,
            changeMonth: true,
            changeYear: true,
            numberOfMonths: 2,
            onClose: function (selectedDate) {
                end.datepicker("option", "minDate", selectedDate);
            }
        });
        end.datepicker({
            minDate: absoluteMin,
            maxDate: absoluteMax,
            changeMonth: true,
            changeYear: true,
            numberOfMonths: 2,
            onClose: function (selectedDate) {
                start.datepicker("option", "maxDate", selectedDate);
            }
        });



        //field init
        start.datepicker( 'setDate', tempstart );
        end.datepicker( 'setDate', tempstart );
    }

    //actual REST interaction
    /**
     * POST REQUEST FUNCTIONS
     */

    /**
     *
     * @param type - detail/summary
     * @param columnIdx -
     */
    function pullValues( type, columnIdx ){
        var resultStart;
        var columnlist ="";

        setMoments();
        var searchlist = getSearchTerms();
        var url = "http://138.49.30.31:9090/" + type;
        var isSum;

        type === "summary"? isSum = true : isSum = false ;

        grabColumns();

        var jsonRequest =
        {
            "columns": columnlist,
            "phases": currentPhase,
            "search": searchlist
        };

        if( isSum ){
            makeTheRequest( JSON.stringify(jsonRequest) );
        } else {
            jsonRequest.options = { "count_only": 1 };
            makeTheRequest( JSON.stringify(jsonRequest), true ); //grab count of results
        }


        // Setup the request.  The options parameter is
        // the object we defined above.
        function makeTheRequest ( json, check ){
            $.ajax({
                type: 'POST',
                url: url,
                dataType: 'json',
                async: false,
                data: json,
                contentType: 'application/json',
                success: function(data){
                    if( isSum ){
                        buildTable( data.values );
                        //fillColList( colList );
                        //buildSelect();
                    } else {
                        if( check ){
                            throttleReturn( data.values[0][0] );
                        } else {
                            detailsReport( data, resultStart );
                        }
                    }
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    alert(xhr.status);
                    alert(thrownError);
                }
            })
        }


        function grabColumns() {
            //TODO: switch here
            if ( isSum ) {
                switch (currentPhase) {
                    case "all":
                        columnlist = ALLLIST;
                        break;
                    case "install":
                        columnlist = INSTALLLIST;
                        break;
                    case "build":
                        currentPhase = "test_build";
                        columnlist = BUILDRUNLIST;
                        break;
                    case "run":
                        currentPhase = "test_run";
                        columnlist = BUILDRUNLIST;
                        break;
                    default:
                        break;
                }
            } else {
                switch (currentPhase) {
                    case "all":
                        columnlist = AIDETAILLIST;
                        resultStart = 19;
                        break;
                    case "install":
                        columnlist = AIDETAILLIST;
                        resultStart = 19;
                        break;
                    case "build":
                        currentPhase = "test_build";
                        columnlist = TBDETAILLIST;
                        resultStart = 17;
                        break;
                    case "run":
                        currentPhase = "test_run";
                        columnlist = TRDETAILLIST;
                        resultStart = 21;
                        break;
                    default:
                        break;
                }

            }
        }

        function checkSearchTerm(terms, name) {
            var val = $('input[name=' + name + ']').val();
            if (val) {
                terms[name] = val;
            }
        }

        function getSearchTerms() {
            var SEARCH_FIELDS = [ 'http_username', 'local_username', 'platform_name', 'platform_hardware', 'os_name', 'mpi_name', 'mpi_version', 'bitness', 'endian', 'compiler', 'compiler_version', 'suite' ];
            var terms = {};

            for (var i = SEARCH_FIELDS.length; i--;) {
                checkSearchTerm(terms, SEARCH_FIELDS[i]);
            }

            terms.start_timestamp = startMoment;
            terms.end_timestamp = endMoment;

            //grab nums if clicked on for drill-down
            if( columnIdx ){
                appendSearch( terms, columnIdx );
            }

            return terms;
        }

        //what if offset > count?
        function throttleReturn( data ){
            setMax( Math.ceil(data/reqLimit) );

            jsonRequest.options = {
                "limit": reqLimit,
                "offset": 0
            };
            makeTheRequest( JSON.stringify(jsonRequest), false ); //grab first batch of results
        }

    }

    function appendSearch( terms, columnIdx ){
        var addColumns = [];

        switch( currentPhase ){
            case "all":
                addColumns = [
                    "mpi_install_pass",
                    "mpi_install_fail",
                    "test_build_pass",
                    "test_build_fail",
                    "test_run_pass",
                    "test_run_fail",
                    "test_run_skip",
                    "test_run_timed"
                ];

                switch( columnIdx ){
                    case 6:
                        terms[ "mpi_install_pass" ] = 1;
                        currentPhase = "install";
                        phaseChange( currentPhase, true );
                        break;
                    case 7:
                        terms[ "mpi_install_fail" ] = 1;
                        currentPhase = "install";
                        phaseChange( currentPhase, true );
                        break;
                    case 8:
                        terms[ "test_build_pass" ] = 1;
                        currentPhase = "build";
                        phaseChange( currentPhase, true );
                        break;
                    case 9:
                        terms[ "test_build_fail" ] = 1;
                        currentPhase = "build";
                        phaseChange( currentPhase, true );
                        break;
                    case 10:
                        terms[ "test_run_pass" ] = 1;
                        currentPhase = "run";
                        phaseChange( currentPhase, true );
                        break;
                    case 11:
                        terms[ "test_run_fail" ] = 1;
                        currentPhase = "run";
                        phaseChange( currentPhase, true );
                        break;
                    case 12:
                        terms[ "test_run_skip" ] = 1;
                        currentPhase = "run";
                        phaseChange( currentPhase, true );
                        break;
                    case 13:
                        terms[ "test_run_timed" ] = 1;
                        currentPhase = "run";
                        phaseChange( currentPhase, true );
                        break;
                }

                break;
            case "install":
                addColumns = [
                    "mpi_install_pass",
                    "mpi_install_fail",
                ];

                switch( columnIdx ){
                    case 9:
                        terms[ "mpi_install_pass" ] = 1;
                        break;
                    case 10:
                        terms[ "mpi_install_fail" ] = 1;
                        break;
                }

                break;
            case "build":
                addColumns = [
                    "mpi_install_pass",
                    "mpi_install_fail",
                ];

                switch( columnIdx ){
                    case 11:
                        terms[ "mpi_install_pass" ] = 1;
                        break;
                    case 12:
                        terms[ "mpi_install_fail" ] = 1;
                        break;
                }

                break;
            case "run":
                addColumns =[
                    "test_run_pass",
                    "test_run_fail",
                    "test_run_skip",
                    "test_run_timed"
                ];

                switch( columnIdx ){
                    case 9:
                        terms[ "test_run_pass" ] = 1;
                        break;
                    case 10:
                        terms[ "test_run_fail" ] = 1;
                        break;
                    case 11:
                        terms[ "test_run_skip" ] = 1;
                        break;
                    case 12:
                        terms[ "test_run_timed" ] = 1;
                        break;
                }

                break;
            default:
                break;
        }

    }


    /*
     ****************************************************
      Search Initialization
     ****************************************************
     */

    function filterColumn ( i ) {
        //$('#example').DataTable().column( i ).search(
        //    $( '.column_filter' ).eq( i ).val(),
        //    true,
        //    false
        //).draw();
    }

    /*
     ****************************************************
     Phase Change
     ****************************************************
     */

    //special case if num col clicked
    function phaseChange( phase, specialCase ){
        currentPhase = phase;
        removeTables();
        addTables( phase );

        //enable details button
        if( phase === 'install' || phase === 'build' || phase === 'run' ){
            $('button[value=details]').removeAttr('disabled');
        } else {
            $('button[value=details]').prop('disabled', 'disabled');
        }

        changeHeaders( phase );
        if( !specialCase ){
            pullValues( "summary" );
        }

        $( "select[name=phases] ").val(currentPhase);
    }

    function removeTables(){
        $( '.col2' ).empty();
        $( '.col2 > table' ).remove();
    }

    function addTables( phase ){
        var sqlCol = $( 'div#sqlbox > div#columnwrapper > .col2' );

        var newColumns;
        var sqlTable = "<table class='sqltextfields' id='table2' cellpadding='1' cellspacing='0' border='0'>" +
                            "<tr class='blankrow' ></tr>";

        switch( phase ){
            case "all":
                sqlCol.append( '&nbsp;' );
                break;
            case "install":
                newColumns = [ "Configure args", "Compiler", "Bitness", "Endian" ];


                sqlTable = buildSqlTableString( newColumns, sqlTable );
                sqlCol.append( sqlTable );

                break;
            case "build":
                newColumns = [ "Suite", "Compiler", "Compiler ver.", "Bitness" ];


                sqlTable = buildSqlTableString( newColumns, sqlTable );
                sqlCol.append( sqlTable );

                break;
            case "run":
                newColumns = [ "Suite", "Test", "np", "Command" ];

                sqlTable = buildSqlTableString( newColumns, sqlTable );
                sqlCol.append( sqlTable );

                break;
            default:
                break;
        }
    }

    function buildSqlTableString( newColumns, table ){
        for( var i = 7; i < 11; i++ ){
            table +=
                "<tr data-column='" + i + "'>" +
                    "<td>" + newColumns[ i-7 ] + "</td>" +
                    "<td align='center'>" +
                    "<td> <input type='text'> </td>" +
                "</tr>"
            ;
        }
        return table;
    }

    function changeHeaders( phase ){

        var header;
        var tempTable = $( '#example' );
        tempTable.empty();

        switch( phase ){
            case "all":
                header =
                    "<thead>" +
                     "<tr id='headers' >" +
                        "<th rowspan='2'>Org</th>" +
                        //"<th rowspan='2'>Local Username</th>" +
                        "<th rowspan='2'>Platform name</th>" +
                        "<th rowspan='2'>Hardware</th>" +
                        "<th rowspan='2'>OS</th>" +
                        "<th rowspan='2'>MPI name</th>" +
                        "<th rowspan='2'>MPI version</th>" +
                        "<th colspan='2'>MPI Install</th>" +
                        "<th colspan='2'>Test Build</th>" +
                        "<th colspan='5'>Test Run</th>" +
                     "</tr>" +
                    "<tr>" +
                        //MPI Install
                        "<th>Pass</th>" +
                        "<th>Fail</th>" +
                        //Test Build
                        "<th>Pass</th>" +
                        "<th>Fail</th>" +
                        //Test Run
                        "<th>Pass</th>" +
                        "<th>Fail</th>" +
                        "<th>Skip</th>" +
                        "<th>Timed</th>" +
                        //"<th>Perf</th>" +
                    "</tr>" +
                    "</thead>";
                break;

            case "install":
                header =
                    "<thead>" +
                    "<tr id='headers' >" +
                        "<th rowspan='2'>Org</th>" +
                        //"<th rowspan='2'>Local Username</th>" +
                        "<th rowspan='2'>Platform name</th>" +
                        "<th rowspan='2'>Hardware</th>" +
                        "<th rowspan='2'>OS</th>" +
                        "<th rowspan='2'>MPI name</th>" +
                        "<th rowspan='2'>MPI version</th>" +
                        "<th rowspan='2'>Bitness</th>" +
                        "<th rowspan='2'>Endian</th>" +
                        "<th rowspan='2'>Compiler</th>" +
                        "<th colspan='2'>MPI Install</th>" +
                    "</tr>" +
                    "<tr>" +
                        //MPI Install
                        "<th>Pass</th>" +
                        "<th>Fail</th>" +
                    "</tr>" +
                    "</thead>";


                break;

            case "build":
                header =
                    "<thead>" +
                    "<tr id='headers' >" +
                        "<th rowspan='2'>Org</th>" +
                        //"<th rowspan='2'>Local Username</th>" +
                        "<th rowspan='2'>Platform name</th>" +
                        "<th rowspan='2'>Hardware</th>" +
                        "<th rowspan='2'>OS</th>" +
                        "<th rowspan='2'>MPI name</th>" +
                        "<th rowspan='2'>MPI version</th>" +
                        "<th rowspan='2'>Bitness</th>" +
                        "<th rowspan='2'>Compiler</th>" +
                        "<th rowspan='2'>Compiler Version</th>" +
                        "<th rowspan='2'>Suite</th>" +
                        "<th colspan='2'>Test Build</th>" +
                    "</tr>" +
                    "<tr>" +
                        //Test Build
                        "<th>Pass</th>" +
                        "<th>Fail</th>" +
                    "</tr>" +
                    "</thead>";
                break;

            case "run":
                header =
                    "<thead>" +
                    "<tr id='headers' >" +
                        "<th rowspan='2'>Org</th>" +
                        //"<th rowspan='2'>Local Username</th>" +
                        "<th rowspan='2'>Platform name</th>" +
                        "<th rowspan='2'>Hardware</th>" +
                        "<th rowspan='2'>OS</th>" +
                        "<th rowspan='2'>MPI name</th>" +
                        "<th rowspan='2'>MPI version</th>" +
                        "<th rowspan='2'>Suite</th>" +
                        "<th rowspan='2'>np</th>" +
                        "<th colspan='5'>Test Run</th>" +
                    "</tr>" +
                    "<tr>" +
                        //Test Run
                        "<th>Pass</th>" +
                        "<th>Fail</th>" +
                        "<th>Skip</th>" +
                        "<th>Timed</th>" +
                        "<th>Perf</th>" +
                    "</tr>" +
                    "</thead>";

                break;

            default:
                break;

        }


        table.destroy();
        tempTable.empty();
        tempTable.append( header );
    }

    /*
     ****************************************************
     Table Configuration
     ****************************************************
     */

    function buildTable( input ){
        table = $('#example').DataTable({
            "dom": '<"top">Rrtp<"bottom"li><"clear">',
            data: input
        });
    }


    /*
     ****************************************************
      MultiSelect Initialization
     ****************************************************
     */

    function fillColList( list ){
        for( var i = 0; i < colList.length; i++  ) {
            var name = list[i];var input = "<option value'" + name + "'>" + name + "</option>";
            $('#my-select').append( input );
        }
    }


    /*
     ****************************************************
      MultiSelect and Aggregation Configuration
     ****************************************************
     */

    //TODO: Fix reassignment of function paramater 'arr'
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

    //TODO: fix extra test/fails
    //NOTE: extra test/fails with have additional text in showColList and hideColList than colList
    function toggleCols() {
        console.time( " Total Completion Time" );

        showStrColList = [];
        var aggregate = false;
        var refresh = false;
        var column;


        for (var i = 0; i < colList.length; i++) {
            var selected = table.column(i).header();

            for (var j = 0; j < showColList.length; j++) {
                if ($(selected).html() === showColList[j]) {
                    column = table.column(i);
                    if (column.visible() === false) {
                        refresh = true;
                    }
                    column.visible(true);
                }
            }

            for (var k = 0; k < hideColList.length; k++) {
                if ( $(selected).html() === hideColList[k] ) {
                    column = table.column(i);
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
            //table.ajax.reload(aggregateData);
            table.destroy();
            buildTable( values );
            toggleCols();
        }
        console.timeEnd( " Total Completion Time" );
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
    }


    /*
     ****************************************************
     Date Range
     ****************************************************
     */

    //Uncommment when implementing final
    //start.datepicker().datepicker('setDate', "-1d" );
    //end.datepicker().datepicker('setDate', new Date() );

    function getDate( selection ){
        var date = $( '#startdate' ).val();

        switch( selection ){
            case "past12hrs":
                return moment().subtract( 12, 'hours' );
                break;
            case "past24hrs":
                return moment().subtract( 24, 'hours' );
                break;
            case "today":
            case "yesterday":
            case "past2days":
            case "past3days":
            case "pastweek":
            case "past2weeks":
                return moment( new Date(date) ).hours(0).minutes(0).seconds(0);
                break;
            case "custom":
                return moment( new Date(date) );
                break;
            default:
                break;
        }
    }

    function setFields( date ){
        //var now = new Date();
        var now = new Date(2014, 10, 29, 0, 0, 0);
        console.log( "NOW: " + now  );

        switch( date ){
            case "today":
                start.datepicker( 'setDate', now );
                end.datepicker( 'setDate', now );
                break;
            case "yesterday":
                start.datepicker( 'setDate', "-1d" );
                end.datepicker( 'setDate', now );
                break;
            case "past12hrs":
                if( now.getHours() <= 11 ){
                    start.datepicker( 'setDate', "-1d" );
                } else {
                    start.datepicker( 'setDate', now );
                }

                end.datepicker( 'setDate', now );
                break;
            case "past24hrs":
                start.datepicker( 'setDate', "-1d" );
                end.datepicker( 'setDate', now );
                break;
            case "past2days":
                start.datepicker( 'setDate', "-2d" );
                end.datepicker( 'setDate', now );
                break;
            case "past3days":
                start.datepicker( 'setDate', "-3d" );
                end.datepicker( 'setDate', now );
                break;
            case "pastweek":
                start.datepicker( 'setDate', "-1w" );
                end.datepicker( 'setDate', now );
                break;
            case "past2weeks":
                start.datepicker( 'setDate', "-2w" );
                end.datepicker( 'setDate', now );
                break;

            default:
                break;
        }
    }

    function setMoments(){
        var startdate = getDate( $('select[name=dates] option:selected').attr('value') ).hours(0).minutes(0).seconds(0);
        var enddate = $( '#enddate' ).val();

        startMoment = startdate.format( REQUESTFORMAT );
        endMoment = moment( new Date(enddate) ).endOf('day');
        endMoment = endMoment.format( REQUESTFORMAT );
    }




    /*
     ****************************************************
     Event Listeners
     ****************************************************
     */


    //------------------DRILL DOWNS------------------

    var sqlbox = $('#sqlbox');

    var tabletr = '#example tbody tr';
    var tabletd = '#example tbody td';

    //CSS Row selection
    $( document ).on( 'click', tabletr, function () {
        table.$('tr.selected').removeClass('selected');
        $(this).addClass('selected');
        //alert( table.row(this).data() );

    } );
    $( document ).on( 'dblclick', tabletr, function () {
        if ( $(this).hasClass('selected') ) {
            $(this).removeClass('selected');
        }
    });


   //Drill Down - grab td cell data
    $( document ).on( 'click', tabletd, function () {
        table.$('td.selected').removeClass('selected');
        $(this).addClass('selected');

        var field = $('.column_filter').eq( $(this).index() );
        var data = table.cell(this).data();
        var row;
        var colidx;

        if( isNaN( data ) ){
            if( field.val() === data ){
                field.val("");
                field.focus();
            } else {
                field.val(data);
                field.focus();
            }
        } else {
            colidx = table.cell(this).index().column; // grab col's index
            row = table.cell(this).index().row;       // grab cell's row index

            parseRow( table.row( row ).data() );          // gather string data
            if( data !== 0 ){
                pullValues( "summary", colidx );          // gather num data with appendSearch()
                $('button[value=details]').removeAttr('disabled');
            }
        }

    } );

    function parseRow( ar ){
        var columnlist;

        switch( currentPhase ){
            case "all" :
                columnlist = ALLLIST;
                break;
            case "install":
                columnlist = INSTALLLIST;
                break;
            case "build":
            case "run":
                columnlist = BUILDRUNLIST;
                break;
        }

        for( var i = 0; i < ar.length; i++ ){
            var name = "[name=" + columnlist[i] + "]";
            $( name ).val( ar[i] );
        }
    }


    $( document ).on( 'dblclick', tabletd, function () {
        if ( $(this).hasClass('selected') ) {
            $(this).removeClass('selected');
        }
    });


    //------------------UI SELECTION LISTENERS------------------

    //Phase Selection
    $( "select[name=phases]" ).on( 'change', function(){
            phaseChange( $( "select[name=phases] option:selected").attr('value') );
    });

    //Window Selection
    $('#sql').on( 'click', function(){
        if( sqlbox.is(":visible") ){
            sqlbox.hide("slow");
        } else {
            settingsbox.hide( "slow" );
            sqlbox.show("slow");
        }
    });

    $('input[name=settings]').on( 'click', function(){
        if( settingsbox.is(":visible") ){
            settingsbox.hide( "slow" );
            //sqlbox.show('slow');
        } else {
            //sqlbox.hide("slow");
            settingsbox.show( "slow" );
        }
    });

    $( document ).on( 'click', 'input[name=hidecaret]', function(){
        sqlbox.hide("slow");
        $(this)
            .prop( 'src', 'img/downcaret.png')
            .prop( 'name', 'showcaret' );
    } );

    $( document ).on( 'click', 'input[name=showcaret]', function(){
        sqlbox.show("slow");
        $(this)
            .prop( 'src', 'img/caret.png')
            .prop( 'name', 'hidecaret' );
    });


    /*
     ****************************************************
     Buttons
     ****************************************************
     */


    //dates dropdown
    $( 'select[name=dates]' ).on( 'change', function(){
        var selecteddate = $( 'select[name=dates] option:selected' ).attr('value');
        if( selecteddate != "custom" ){
            setFields( selecteddate );
        }
    });

    start.on( 'change', function(){
        $( 'option[value=custom]' ).prop('selected', true);
    });
    end.on( 'change', function(){
        $( 'option[value=custom]' ).prop('selected', true);
    });


    //SQL Buttons

    //-summary
    function summary(){
        $('#table').show();
        $('#details-report').hide();
        currentPhase = $( "select[name=phases] option:selected").attr('value');
        table.destroy();
        pullValues( "summary" );
        $('button[value=details]').prop('disabled', 'disabled');
    }

    $( 'button[value=summary]' ).on( 'click', function(){
        summary();
        $('button[value=filter]').removeAttr('disabled');
        $('#details').hide( "fast" );
    });

    //details
    $( document ).on( 'click', 'button[value=details]', function() {
        currentPhase = $( "select[name=phases] option:selected").attr('value');
        $('#table').hide();
        $('#details-report').show();
        //table.destroy();
        pullValues( "detail" );
        $('button[value=filter]').prop('disabled', 'disabled');
    });


    //-start over
    $( document ).on( 'click', 'button[value=startover]', function(){

        $( 'input[type=text]').val('');

        $( 'select[name^=dates] option[value="past24hrs"]').attr("selected","selected");

        start.datepicker( 'setDate', '-1d' );
        end.datepicker( 'setDate', new Date() );

        //$('select[name^="salesrep"] option[value="Bruce Jones"]').attr("selected","selected");
    });

    //-filter
    var state = true;

    $('button[value=filter]').on( 'click', function(){

        var extend = $( '.extend' ).first();
        var lightcoral = "rgb(240, 128, 128)";
        var lightgreen = "rgb(144, 238, 144)";
        var color = extend.css('background-color');
        var requestState = ( color === lightcoral );

        function changeColor() {
            if ( requestState ) {
                extend.css('background-color', lightgreen);
            } else {
                extend.css('background-color', lightcoral);
            }
        }


        //TODO: make performance and details disabled upon switching from filter mode
        function disableForms(){
            var select = $('.extend select');
            var phase = $( 'select[name=phases]' );
            var primary = $( '.primary' );
            var extra = $( '#show-hide' );
            var startdate = $( '#startdate' );
            var enddate = $( '#enddate' );

            if ( requestState ) {
                phase.prop('disabled', true);
                select.prop('disabled', true);
                primary.prop('disabled', true);
                startdate.prop('disabled', true);
                enddate.prop('disabled', true);
                extra.prop('disabled', false);
            } else {
                phase.prop('disabled', false);
                select.prop('disabled', false);
                primary.prop('disabled', false);
                startdate.prop('disabled', false);
                enddate.prop('disabled', false);
                extra.prop('disabled', true);
            }
        }

        function changeText(){
            var text = $( '#sqltoolbar3' );
            text.empty();

            if ( requestState ) {
                text.append('Filter current result');
            } else {
                text.append('Submit a new request');
            }
        }

        function toggleClear(){
            if ( requestState ) {
                $( 'button[value=startover]' )
                    .prop( 'value', 'clear' )
                    .empty()
                    .text( 'Clear Fields' );
            } else {
                $( 'button[value=clear]' )
                    .prop( 'value', 'startover' )
                    .empty()
                    .text( 'Start Over' );
            }
        }

        function addClass(){
            if( requestState ){
                $('.sqltextfields')
                    .find( 'input' )
                    .addClass( 'column_filter' )
                    .prop( 'data-column', 1 );

                for( var i = 0; i < 7; i++ ){
                    var selector = '.column_filter :eq(' + i + ')';
                    $( selector  )
                        //.eq( i )
                        .parents('tr')
                        .attr( 'data-column', i );
                }
            } else {
                $('.sqltextfields')
                    .find('input')
                    .removeClass('column_filter');
            }

        }

        changeColor();
        disableForms();
        changeText();
        toggleClear();
        addClass();

        color = extend.css('background-color');
        state = ( color === lightcoral );
    });

    //-performance
    //$('button[value=perf]').on( 'click', function() { makeRequest('http://flux.cs.uwlax.edu:9090/fields') });
    $('button[value=perf]').on( 'click', function() {
        alert("Not currently implemented.");
    });



    //------------------FILTER MODE------------------

    //filter fields
    $( document ).on( 'keyup click focus', 'input.column_filter', function() {
        //if( $( '.extend' ).first()
        //                  .
        //){
        //
        //}


        if( !state ) {
            filterColumn( $(this).parents('tr').attr('data-column') );
        }
    } );

    //clear
    $( document ).on( 'click', 'button[value=clear]', function(){
        $( 'input[type=text][class=column_filter]' ).val('').focus().blur();
    });

    //show/hide
    $('#show-hide').click( function(){
        toggleCols();
    } );


    //-------------------Detail HTML-------------------

    //$('#details').hide();

    /**
     * detailsReport: Populate detailsReports w/ pagination
     *
     * @param json - JSON loaded in from makeTheRequest
     * @param n - number of row to add pre tags (hard coded)
     */
    function detailsReport( json, n ){
        var detailsTableTemplate = Handlebars.compile( $('#details-table').html() );
        $('#details-report').html(detailsTableTemplate(json))
                            .addClass('detailsTable');

        var tmp = '.detailsTable table tr:nth-child(n+' + n + '):nth-child(-n+' + (n+1) + ') td';

        $( tmp ).addClass('highlight')
                .wrapInner( '<pre></pre>' );

        $('#details').show( "fast" );
    }

    function paginationInit(){
        var tmp =
        "<a href='#' class='first' data-action='first'>&laquo;</a>" +
            "<a href='#' class='previous' data-action='previous'>&lsaquo;</a>" +
            "<input type='text' readonly='readonly' />" +
            "<a href='#' class='next' data-action='next'>&rsaquo;</a>" +
            "<a href='#' class='last' data-action='last'>&raquo;</a>";
        $('.pagination').append( tmp );

        $('#top').jqPagination({
            max_page:  40,
            paged: function(page) {
                var bot = $('#bottom')

                if ( bot.jqPagination('option', 'current_page') !== page ) {
                    bot.jqPagination('option', 'current_page', page);
                }
            }
        });

        $('#bottom').jqPagination({
            max_page:  40,
            paged: function(page) {
                var top = $('#top');
                if ( top.jqPagination('option', 'current_page') !== page ) {
                    top.jqPagination('option', 'current_page', page);
                }
            }
        });
    }

    function countInit(){
        var tmp =
            "<div id='count'>" +
                "Show " +
                    "<select name='count'>" +
                        "<option value='10'> 10 </option>" +
                        "<option value='25' selected > 25 </option>" +
                        "<option value='50'> 50 </option>" +
                        "<option value='100'> 100 </option>" +
                    "</select>" +
                "entries" +
            "</div>";

        $('.pagination').after(tmp);
    }


    function setMax( num ){
        $('.pagination').jqPagination('option', 'max_page', num);
    }

    $('#next').on('click', function(){
        //console.log( "Setting to: " + $('.pagination').jqPagination( 'option', 'current_page' ) );
        //setCurrent(45);
    });

    //For number of table with offset of 1
    Handlebars.registerHelper("offset", function(value, options)
    {
        return parseInt(value) + 1;
    });
});
