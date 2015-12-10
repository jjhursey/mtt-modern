/**
* Created by thomaslynch on 10/16/14.
* Last Edited: 04/12/15
*/

$(document).ready(function() {
    /*
     ****************************************************
     BEGIN VARIABLE DECLARATION
     ****************************************************
     */

    // (N) Implement _more_ Handlebars (table creation)

    //TODO: Fix Show/Hide
    //TODO: Fix CSS
    //TODO: Fix Multiple Drill-Down on same selection bug (Destroys Table)
    //TODO: Fix Start Over button mess

    //determine when to destroy table (drilldowns)
    var oldphase;

    var ns = {
        currentPhase: "all",
        /*sql*/state: "true",
        startMoment: 0,
        endMoment: 0
    };

    //Constants
    var ALLLIST = [
        "http_username",
        "platform_name",
        "platform_hardware",
        "os_name",
        "mpi_name",
        "mpi_version",
    ];
    var INSTALLLIST = [
        "http_username",
        "platform_name",
        "platform_hardware",
        "os_name",
        "mpi_name",
        "mpi_version",
        "bitness",
        "endian",
        "compiler_name"
    ];
    var BUILDLIST = [
        "http_username",
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
    var RUNLIST = [
        "http_username",
        "platform_name",
        "platform_hardware",
        "os_name",
        "mpi_name",
        "mpi_version",
        "test_suite_name",
        "np"
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
        "environment",
        "test_result"
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
        "environment",
        "test_result"
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
        "environment",
        "test_result"
    ];

    var REQUESTFORMAT = 'YYYY-MM-DD hh:mm:ss a';

    //for datepicker
    var start = $( "#startdate" );
    var end = $( "#enddate" );

    //
    var colList =  [
        "Org",
        "Platform name",
        "Hardware",
        "OS",
        "MPI name",
        "MPI Install",
        "MPI Version",
        "Test Build",
        "Test Run"
    ];
    var showColList = [];
    var hideColList = [];

    var stringCols = [
        "http_username",
        "platform_name",
        "platform_hardware",
        "os_name",
        "mpi_name",
        "mpi_version"
        //"mpi_install.compiler_name"
        //"http_username",
        //"platform_name",
        //"platform_hardware",
        //"os_name",
        //"mpi_name",
        //"mpi_version",
        //"mpi_install.compiler_name"
    ];
    var intCols = [
        "mpi_install_pass",
        "mpi_install_fail",
        "test_build_pass",
        "test_build_fail",
        "test_run_pass",
        "test_run_fail",
        "test_run_skip",
        "test_run_timed",
        "bitness",
        "endian"
    ];

    var showStrColList = [];

    var table;
    var fields;
    var values;
    var cached;

    var startMoment;
    var endMoment;

    var lastSumJSON = {};
    var lastDetJSON = {};
    var lastJSON = {};
    var reqLimit = 25;

    var currentPhase = "all";
    var jsonRequest;
    var count;
    var resultStart = 0;
    var lastType;
    /*
     ****************************************************
     END VARIABLE DECLARATION
     ****************************************************
     */

    // Site Initilization

    (function init( ){
        addClass();
        dateInit();
        fillColList( colList );

        paginationInit();
        countInit();
        $('#details').hide();

        buildSelect();
        //buildTable();
        pullValues( "summary" );
    })();

    function addClass(){
        $('.sqltextfields')
            .find( 'input' )
            .addClass( 'column_filter' )
            .prop( 'data-column', 1 );

        for( var i = 0; i < 7; i++ ){
            var selector = '.column_filter :eq(' + i + ')';
            $( selector  )
                .parents('tr')
                .attr( 'data-column', i );
        }

    }

    function dateInit(){
        var tempstart = new Date(2014, 10, 29, 0, 0, 0);

        //set dropdown menu
        $( 'select[name=dates]' ).val( 'past24hrs' );

        //var absoluteMin = new Date(2011, 0, 1);
        //var absoluteMax = new Date(2014, 9, 29);

        //datepicker configuration
        start.datepicker({
            //minDate: absoluteMin,
            //maxDate: absoluteMax,
            changeMonth: true,
            changeYear: true,
            numberOfMonths: 2,
            onClose: function (selectedDate) {
                end.datepicker("option", "minDate", selectedDate);
            }
        });
        end.datepicker({
            //minDate: absoluteMin,
            //maxDate: absoluteMax,
            changeMonth: true,
            changeYear: true,
            numberOfMonths: 2,
            onClose: function (selectedDate) {
                start.datepicker("option", "maxDate", selectedDate);
            }
        });



        //field init
        //start.datepicker( 'setDate', tempstart );
        //end.datepicker( 'setDate', tempstart );
        start.datepicker( 'setDate', '-1d' );
        end.datepicker( 'setDate', new Date() );
    }

    /**
     * POST REQUEST FUNCTIONS
     */

    /**
     * pullValues: create JSON for request, then make request
     *
     * @param type - detail/summary
     * @param columnIdx - columnIdx clicked on (sent from drilldowns)
     * @param grabJSON - boolean: true = create JSON request/false = send POST request w/ JSON  (lazy alt to creating createJSON())
     */
    function pullValues( type, columnIdx, grabJSON, force ){
        var columnlist ="";
        lastType = type;

        setMoments();
        var searchlist = getSearchTerms( columnIdx );
        var isSum;

        type === "summary"? isSum = true : isSum = false ;

        grabColumns();

        jsonRequest =
        {
            "columns": columnlist,
            "phases": currentPhase,
            "search": searchlist
        };


        if( grabJSON ){ return; }

        if( isSum ) {
            makeTheRequest(type, jsonRequest, true, false, columnIdx, force);
        } else {
            jsonRequest.options = { "count_only": 1 };
            makeTheRequest(type, jsonRequest, false, true); //grab count of results
        }

        function grabColumns() {
            if ( isSum )  {
                switch (currentPhase) {
                    case "all":
                        columnlist = ALLLIST;
                        resultStart = 19;
                        break;
                    case "install":
                        columnlist = INSTALLLIST;
                        resultStart = 19;
                        break;
                    case "test_build":
                        columnlist = BUILDLIST;
                        resultStart = 17;
                        break;
                    case "test_run":
                        columnlist = RUNLIST;
                        resultStart = 21;
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
                    case "test_build":
                        columnlist = TBDETAILLIST;
                        resultStart = 17;
                        break;
                    case "test_run":
                        columnlist = TRDETAILLIST;
                        resultStart = 21;
                        break;
                    default:
                        break;
                }

            }
        }
    }

    function getSearchTerms( columnIdx ) {
        //grab search fields
        var SEARCH_FIELDS = [ 'http_username', 'local_username', 'platform_name', 'platform_hardware', 'os_name', 'mpi_name', 'mpi_version', 'bitness', 'endian', 'compiler', 'compiler_version', 'test_suite_name', 'np' ];
        var terms = {};

        for (var i = SEARCH_FIELDS.length; i--;) {
            checkSearchTerm(terms, SEARCH_FIELDS[i]);
        }

        terms.start_timestamp = startMoment;
        terms.end_timestamp = endMoment;

        //grab nums if clicked on for drill-down
        if( columnIdx ){
            oldphase = currentPhase;
            appendSearch( terms, columnIdx );
        }

        function checkSearchTerm(terms, name) {
            var val = $('input[name=' + name + ']').val();
            if (val) {
                terms[name] = val;
            }
        }

        /**
         * appendSearch:
         *
         * @param terms     -
         * @param columnIdx - column index of clicked on cell
         */
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
                            currentPhase = "test_build";
                            phaseChange( currentPhase, true );
                            break;
                        case 9:
                            terms[ "test_build_fail" ] = 1;
                            currentPhase = "test_build";
                            phaseChange( currentPhase, true );
                            break;
                        case 10:
                            terms[ "test_run_pass" ] = 1;
                            currentPhase = "test_run";
                            phaseChange( currentPhase, true );
                            break;
                        case 11:
                            terms[ "test_run_fail" ] = 1;
                            currentPhase = "test_run";
                            phaseChange( currentPhase, true );
                            break;
                        case 12:
                            terms[ "test_run_skip" ] = 1;
                            currentPhase = "test_run";
                            phaseChange( currentPhase, true );
                            break;
                        case 13:
                            terms[ "test_run_timed" ] = 1;
                            currentPhase = "test_run";
                            phaseChange( currentPhase, true );
                            break;
                        default: break;
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
                case "test_build":
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
                case "test_run":
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

        return terms;
    }


    /**
     * makeTheRequest: POST JSON request
     *
     * @param json - json object for request
     * @param check - boolean: true = grab page count/false = grab detail results
     * @param isSum - boolean: true = summary POST/false = details POST
     * @param type - 'summary'/'detail' - postfix to url for request type
     * @param columnIdx -
     * @param force - force request (used during showing columns)
     */
    function makeTheRequest ( type, json, isSum, check, columnIdx, force ){
        var url = "http://flux.cs.uwlax.edu/mtt/api" + type;

        //TODO: Figure out why is this is here...
        //if( columnIdx && oldphase == currentPhase && oldphase != "all" && lastJSON != json){
        //    table.destroy();
        //}


        lastJSON = json;

        //compare objects with Lo-Dash to prevent requesting same data twice in a row
        if( type === "summary") {
            if (_.isEqual(lastSumJSON.search, json.search) && _.isEqual(lastSumJSON.phases, json.phases) && !force) {
                console.log("ABORT THE SUMMARY QUERY!!!!");
                return;
            } else if ( columnIdx && oldphase == currentPhase && oldphase != "all"  ) {
                    table.destroy();
            }
            lastSumJSON = json;
            console.log( "lastSumJSON written to" );
        } else if ( type === "detail" && json.options['count_only'] === 1) {
            if( _.isEqual( lastDetJSON.search, json.search ) && _.isEqual( lastDetJSON.phases, json.phases ) && !force  ){
                setMax( Math.ceil(count/reqLimit) ); //details - start over - same details (w/o this pagination will work, but no text will be displayed until interaction)
                console.log("ABORT THE DETAILS QUERY!!!!");
                return;
            }
            lastDetJSON = json;
            console.log( "lastDetJSON written to!" );
        }

        $.ajax({
            type: 'POST',
            url: url,
            dataType: 'json',
            data: JSON.stringify(json),
            contentType: 'application/json',
            timeout: 10000,
            beforeSend: function() {
                if(isSum){
                    $('#table').hide();
                }
                $('#table').after("<div name='load' style='margin-left:35%'> <img src='img/loading.gif'/> </div>");
            },
            success: function(data){
                cached = data;
                if (isSum) {
                    buildTable( data.values );
                    addCSS();
                    fillColList( ALLLIST );
                    buildSelect();
                    $('#table').show();
                } else {
                    if (check) {
                        count = data.values[0][0];
                        setMax( Math.ceil(data.values[0][0] / reqLimit) );
                        throttleReturn(1);
                    } else {
                        detailsReport( data, resultStart );
                    }
                }
                $('div[name=load]').remove();
            },
            error: function (xhr, ajaxOptions, thrownError) {
                load = $('div[name=load]');
                //TODO: use statuscode - xhr.status?
                //switch( xhr.status ){
                //  case 503:
                //  load.empty();
                //  load.html("Uh-oh!! Service is down!!!!! Rebuilding in 3 seconds...");



                switch( thrownError ){
                    case "timeout":
                        load.empty();
                        load.html("Uh-oh!! It timed out!!!!! Rebuilding in 3 seconds...");
                        //setTimeout(location.reload, 500);
                        break;
                    case "Internal Server Error":
                        load.empty();
                        load.html("Uh-oh!! Looks like the server didn't like that...Rebuilding in 3 seconds...");
                        //setTimeout(location.reload, 500);
                        break;
                    default:
                        alert(xhr.status);
                        alert(thrownError);
                }
            }
        })
    }

    //what if offset > count?
    /**
     * throttleReturn: Create offset for return and make POST request
     *
     * @param page - Page number requested
     */
    function throttleReturn( page ){
        var offset = (page - 1) * reqLimit;

        jsonRequest.options = {
            "limit": reqLimit,
            "offset": offset
        };

        makeTheRequest( 'detail', jsonRequest, false, false ); //grab first batch of results
    }


    /*
     ****************************************************
      Search Initialization
     ****************************************************
     */

    function filterColumn ( i ) {
        $('#example').DataTable().column( i ).search(
            $( '.column_filter' ).eq( i ).val(),
            true,
            false
        ).draw();
    }

    /*
     ****************************************************
     Phase Change
     ****************************************************
     */

    function phaseChange( phase, isDrilldown ){
        currentPhase = phase;
        $( "select[name=phases]" ).val(currentPhase);

        removeTables();
        addTables( phase );
        changeHeaders( phase );
        updateSummary( isDrilldown );
        updateDetails( phase );
    }

    function removeTables(){
        $( '.col2' ).empty();
        $( '.col2 > table' ).remove();
    }

    function addTables( phase ){
        var sqlCol = $( 'div#sqlbox > div#columnwrapper > .col2' );

        var newColumns;
        var columnsRaw;
        var sqlTable = "<table class='sqltextfields' id='table2' cellpadding='1' cellspacing='0' border='0'>" +
                            "<tr class='blankrow' ></tr>";

        switch( phase ){
            case "all":
                sqlCol.append( '&nbsp;' );
                break;
            case "install":
                newColumns = [ "Bitness", "Endian", "Compiler", "Configure args" ];
                columnsRaw = [ "bitness", "endian", "compiler_name", "configure_arguments" ];

                sqlTable = buildSqlTableString( newColumns, columnsRaw, sqlTable );
                sqlCol.append( sqlTable );

                break;
            case "test_build":
                newColumns = [ "Bitness", "Compiler", "Compiler ver.", "Suite" ];
                columnsRaw = [ "bitness", "compiler_name", "compiler_version", "test_suite_name" ];

                sqlTable = buildSqlTableString( newColumns, columnsRaw, sqlTable );
                sqlCol.append( sqlTable );

                break;
            case "test_run":
                newColumns = [ "Suite", "np", "Test", "Command" ];
                columnsRaw = [ "test_suite_name", "np", "test_name", "full_command" ];

                sqlTable = buildSqlTableString( newColumns, columnsRaw, sqlTable );
                sqlCol.append( sqlTable );

                break;
            default:
                break;
        }
    }

    function buildSqlTableString( newColumns, columnsRaw, table ){
        for( var i = 7; i < 11; i++ ){
            table +=
                "<tr data-column='" + i + "'>" +
                    "<td>" + newColumns[ i-7 ] + "</td>" +
                    "<td align='center'>" +
                    "<td> <input type='text' name='" + columnsRaw[i-7] + "'> </td>" +
                "</tr>"
            ;
        }
        return table;
    }

    function changeHeaders( phase, specialCase ){
        var header;
        var tempTable = $( '#example' );
        tempTable.empty();

        switch( phase ){
            case "all":
                header =
                    "<thead>" +
                     "<tr id='headers' >" +
                        "<th rowspan='2'>Org</th>" +
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

            case "test_build":
                header =
                    "<thead>" +
                    "<tr id='headers' >" +
                        "<th rowspan='2'>Org</th>" +
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

            case "test_run":
                header =
                    "<thead>" +
                    "<tr id='headers' >" +
                        "<th rowspan='2'>Org</th>" +
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
                        //"<th>Perf</th>" +
                    "</tr>" +
                    "</thead>";

                break;

            default:
                break;

        }

        if( !specialCase ){
        }
        table.destroy();
        tempTable.empty();
        tempTable.append( header );
    }

    function updateSummary( isDrilldown ){
        if( !isDrilldown ){
            pullValues( 'summary', 0, false );
        }
    }

    function updateDetails( phase ){
        if( phase === 'install' || phase === 'test_build' || phase === 'test_run' ){
            // toggle button
            $( 'button[value=details]' ).removeAttr('disabled');

            //update details table if visible
            if ( $('#details').is(':visible') ) {
                $( '#details' ).hide()
                               .empty();

                $( '#table' ).show();
                //pullValues( 'detail', 0, false  );
            }

        } else {
            $( 'button[value=details]' ).prop('disabled', 'disabled');
        }


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
        //$('#my-select').multiSelect('refresh');

        for( var i = 0; i < list.length; i++ ) {
            var name = list[i];
            var input = "<option value'" + name + "'>" + name + "</option>";
            $('#my-select').append( input );
            //console.log( input );
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


    //fill with columns of current phase
    function fillShowColList(){
        switch( currentPhase ) {
            case "all":
                showColList = ALLLIST;
                break;
            case "install":
                showColList = INSTALLLIST
                break;
            case "test_build":
                showColList = BUILDLIST;
                break;
            case "test_run":
                showColList = RUNLIST;
                break;
            default:
                break;
        }
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

        fillShowColList();
        fillShowStrColList();
        if (aggregate) {
            aggregateData();
        }

        if( refresh ){
            ////////table.ajax.reload(aggregateData);

            table.destroy();
            //buildTable( cached );
            pullValues( lastType,null,null,true );
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
            console.log( "lrow:" + lrow );

            //TODO: Change hard coded 6 to be dependent on phase
            //for ( var i = 0; i < showStrColList.length; i++ ){
            for ( var i = 0; i < 6; i++ ){
                //console.log( this.row(index).data()[i] );
                lstring += this.row( index ).data()[ stringCols.indexOf( showStrColList[i] ) ] + ", ";
                //lstring += this.row( index ).data()[i] + ", ";
                //console.log( this.row( index ).data() );
            }

            console.log("lstring:" + lstring);

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
                console.log("BANISHING: " + lstring);
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
    start.datepicker().datepicker('setDate', "-1d" );
    end.datepicker().datepicker('setDate', new Date() );

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
        var now = new Date();
        //console.log( "NOW: " + now  );
        start.datepicker('option', 'maxDate', now );

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
                start.datepicker('option', 'maxDate', now );
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
        //var enddate = new Date();

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
    } );
    $( document ).on( 'dblclick', tabletr, function () {
        if ( $(this).hasClass('selected') ) {
            $(this).removeClass('selected');
        }
    });

    /**
     * checkCol: Check if the index is a suitable drill down option and not just a number.
     * @param data
     */
    function checkCol( colidx ){
        switch( currentPhase ){
            case "all":
                //6-13
                if( colidx > 5 && colidx < 14  ){
                    return 1;
                }
                break;
            case "install":
                //9-10
                if( colidx > 8 && colidx < 11  ){
                    return 1;
                }
                break;
            case "test_build":
                //10-11
                if( colidx > 9 && colidx < 12  ){
                    return 1;
                }
                break;
            case "test_run":
                //8-11
                if( colidx > 7 && colidx < 12  ){
                    return 1;
                }
                break;
            default:
                break;
        }

        return 0; //hit if colidx is not in range of suitable drilldown
    }


   //Drill Down - grab td cell data
    $( document ).on( 'click', tabletd, function () {
        table.$('td.selected').removeClass('selected');
        $(this).addClass('selected');

        //var field = $('.column_filter').eq( $(this).index() );
        var field = $('.sqltextfields').find("input").eq( $(this).index() );
        var data = table.cell(this).data();
        var row;
        var colidx = table.cell(this).index().column;

        if( isNaN(data) || data === "32" || data === "64" ) {
            if( field.val() === data ){
                field.val("");
                field.focus();
            } else {
                field.val(data);
                field.focus();
            }
        } else if( checkCol(colidx) && data != "0" ) {
            colidx = table.cell(this).index().column;           // grab col's index
            row = table.cell(this).index().row;                 // grab cell's row index

            parseRow( table.row( row ).data() );                // gather string data
            if( data !== 0 ){
                pullValues('summary', colidx, false);           // gather num data with appendSearch()
                $( 'button[value=details]' ).removeAttr('disabled');
            }
        } else {
            console.log("Not today, hotshot!"); // was originally for bitness
        }

    } );

    /**
     * parseRow: Copy row values to text fields
     *
     * 1. Grab correct column list
     * 2. Grab row values and put into text fields
     *
     * @param ar - row that was clicked on
     */
    function parseRow( ar ){
        var columnlist;

        //grab correct column list
        switch( currentPhase ){
            case "all" :
                columnlist = ALLLIST;
                break;
            case "install":
                columnlist = INSTALLLIST;
                break;
            case "test_build":
                columnlist = BUILDLIST;
                break;
            case "test_run":
                columnlist = RUNLIST;
                break;
        }

        //grab values from row and display in text fields
        for( var i = 0; i < ar.length; i++ ){
            var name = "[name=" + columnlist[i] + "]";
            $( name ).val( ar[i] );
        }
    }

    //remove selection class
    $( document ).on( 'dblclick', tabletd, function () {
        if ( $(this).hasClass('selected') ) { $(this).removeClass('selected'); }
    });

    //------------------UI SELECTION LISTENERS------------------

    //Phase Selection
    $( "select[name=phases]" ).on( 'change', function(){
            phaseChange( $( "select[name=phases] option:selected").attr('value') );
            //pullValues( lastType, 0, false );
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
        settingsbox.toggle( 'display' );
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
     * ******************   BUTTONS   *******************
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
        if( $('#details').is(":visible")  ){
            $( '#table' ).show();
            $( '#details' ).hide();
        }

        $( 'button[value=filter]' ).removeAttr('disabled');

        currentPhase = $( "select[name=phases] option:selected" ).attr('value');
        pullValues( "summary" );
    }

    $( 'button[value=summary]' ).on( 'click', function(){
        pullValues( 'summary', 0, true );
        if( !_.isEqual( lastSumJSON, jsonRequest ) ){
             table.destroy();
        }

        summary();
    });


    //details
    $( document ).on( 'click', 'button[value=details]', function() {
        $( '#table' ).hide();
        $( '#details' ).show();
        $( 'button[value=filter]' ).prop( 'disabled', 'disabled' );

        currentPhase = $( "select[name=phases] option:selected").attr('value');
        pullValues( "detail" );
    });


    //-start over
    $( document ).on( 'click', 'button[value=startover]', function(){
        //location.reload();

        $( 'input[type=text]' ).val('');
        $( 'select[name^=dates] option[value="past2weeks"]' ).attr("selected","selected");
        $( 'select[name^=phases] option[value="all"]' ).attr("selected","selected");

        start.datepicker( 'setDate', -1 );
        end.datepicker( 'setDate', new Date() );

        if( currentPhase !== "all" ){
            phaseChange( "all", true );
        }
        summary();
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
                $('button[value=details]').prop('disabled', true);
                $('button[value=perf]').prop('disabled', true);
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
    $('button[value=perf]').on( 'click', function() {
        alert("Not currently implemented.");
    });



    //------------------FILTER MODE------------------

    //filter fields
    $( document ).on( 'keyup click focus', 'input.column_filter', function() {
        //if ( !state ) {
            filterColumn( $(this).parents('tr').attr('data-column') );
        //}
    } );

    //clear
    $( document ).on( 'click', 'button[value=clear]', function(){
        $( 'input[type=text][class=column_filter]' ).val('').focus().blur();
    });

    //show/hide
    $('#show-hide').click( function(){
        toggleCols();
    });


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
        $('#details-report').empty()
                            .html(detailsTableTemplate(json))
                            .addClass('detailsTable');

        var tmp = '.detailsTable table tr:nth-child(n+' + n + '):nth-child(-n+' + (n+1) + ') td';
        var result = '.detailsTable table tr:nth-child(n+' + (n+3) + ') td';
        result = $(result).html().trim();

        var color;

        switch( result ){
            case "0":
                color = "red";
                break;
            case "1":
                color = "green";
                break;
            case "2":
                color = "yellow";
                break;
            case "3":
                color = "orange";
                break;
            default:
                break;
        }

        $( tmp ).addClass(color)
            .wrapInner( '<pre></pre>' );


        $('#details').show( "fast" );

        if( lastJSON.options.offset == 0 ){
            $('#textCount').empty();
            tmp =
                "<div id='textCount'>" +
                    "Showing " + 1 + " to " + $('#count option:selected').val() + " out of " + count + " entries." +
                "</div>";

            $('#count').after(tmp);
        }


        if( count == 0 ){
            tmp = "No results found...";
            $('#details').append( tmp );
        }
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
            paged: function(page) {
                syncPagination( $('#bottom'), page );
            }
        });

        $('#bottom').jqPagination({
            paged: function(page) {
                syncPagination( $('#top'), page );
            }
        });

        function syncPagination( id, page ){
            if( id.jqPagination( 'option', 'current_page' ) !== page ){
                id.jqPagination( 'option', 'current_page', page );
                throttleReturn( $('.pagination').jqPagination('option', 'current_page') );
                setTextRange();
            }
        }

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

    function setTextRange(){
        $('#textCount').empty();

        var tmp;
        var low  = lastJSON.options.offset + 1;
        var high = (low - 1) + parseInt($('#count option:selected').val());

        if ( high > count ) {
            tmp = "Showing " + low + " to " + count + " out of " + count + " entries.";
        } else {
            tmp = "Showing " + low + " to " + high + " out of " + count + " entries.";
        }

        $('#textCount').append( tmp );
    }

    $('select[name=count]').on('change', function(){
        var p = $('.pagination');
        reqLimit = $( "select[name=count] option:selected").attr('value');

        p.jqPagination( 'option', 'current_page', 1 );
        setMax( Math.ceil(count/reqLimit) );
        setTextRange();

        throttleReturn( p.jqPagination('option', 'current_page') );
    });

    //For number of table with offset of 1
    Handlebars.registerHelper("offset", function(value, options) {
        return (parseInt(value + 1) + (lastJSON.options.offset));
    });


    // Performance Buttons
    $( document ).on( 'change', '#table', function(){
       addCSS();
    });

    //color cordination
    function addCSS(){
        var cells = $('td.immediate');

        var cellData = table.cells( cells ).data();


        table.cells().every( function () {

            var colidx = this.index().column;
            var colh = table.column( colidx ).header();
            var colheader = $(colh).html();

            if (this.data() > 0) {
                if( colheader == "Pass" ){ $(this.node()).addClass( 'green' ); }
                if( colheader == "Fail" ){ $(this.node()).addClass( 'red' ); }
                if( colheader == "Skip" ){ $(this.node()).addClass( 'yellow' ); }
                if( colheader == "Timed" ){ $(this.node()).addClass( 'orange' ); }
            }
        });
    }


});
