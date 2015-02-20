/**
 * Created by thomaslynch on 10/16/14.
 * Last Edited: 11/6/14
 */

$(document).ready(function() {


    /*
     ****************************************************
     REST INTERFACE
     ****************************************************
     */

    var httpRequest;

    function makeRequest(url) {
        if (window.XMLHttpRequest) { // Mozilla, Safari, ...
            httpRequest = new XMLHttpRequest();
        } else if (window.ActiveXObject) { // IE
            try {
                httpRequest = new ActiveXObject("Msxml2.XMLHTTP");
            }
            catch (e) {
                try {
                    httpRequest = new ActiveXObject("Microsoft.XMLHTTP");
                }
                catch (e) {}
            }
        }

        if (!httpRequest) {
            alert('Giving up :( Cannot create an XMLHTTP instance');
            return false;
        }
        httpRequest.onreadystatechange = alertContents;
        httpRequest.open('GET', url);
        httpRequest.send();
    }

    function alertContents() {
        if (httpRequest.readyState === 4) {
            if (httpRequest.status === 200) {
                alert(httpRequest.responseText);
            } else {
                alert('There was a problem with the request. ' + httpRequest.status);
            }
        }
    }

    /*
     ****************************************************
     Variable Declaration and Ajax Call
        Used in: Table Configuration
                 MultiSelect
     ****************************************************
     */


    var allList = [
        "http_username",
        "local_username",
        "platform_name",
        "platform_hardware",
        "os_name",
        "mpi_name",
        "mpi_version",
        "compiler"
    ];

    var installlist = [
        "http_username",
        "local_username",
        "platform_name",
        "platform_hardware",
        "os_name",
        "mpi_name",
        "mpi_version",
        "bitness",
        "endian",
        "compiler"
    ];

    var buildrunlist = [
        "http_username",
        "local_username",
        "platform_name",
        "platform_hardware",
        "os_name",
        "mpi_name",
        "mpi_version",
        "bitness",
        "compiler",
        "compiler_version",
        "suite"
    ];

    var runlist = [
        "http_username",
        "local_username",
        "platform_name",
        "platform_hardware",
        "os_name",
        "mpi_name",
        "mpi_version",
        "bitness",
        "compiler",
        "compiler_version",
        "suite"
    ]


    var colList =  [];
    var showColList = [];
    var hideColList = [];

    var allphases;

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

    var url = "ajax/data/pretty.json";
    //var url = "http://flux.cs.uwlax.edu/~jjhursey/mtt-tmp/pretty.json";

    function ajaxprototype( ){
        $.ajax({
            dataType: "json",
            url: url
        })
            .done( function( data ){
                //fill variables
                fields = data.fields;
                values = data.values;

                for( var i = 0; i < data.fields.length; i++ ){
                    //setHeaders( data.fields[i] );
                    colList.push( data.fields[i] );
                    showColList.push( data.fields[i] );
                }

                for( var i = 0; i < colList.length; i++ ){
                    if( i < 6 ){
                        stringCols.push( colList[i] );
                    } else {
                        intCols.push( colList[i] );
                    }
                }

                fillColList( colList );
                buildSelect();
                addHeaders();
                buildTable( values );
            });
    }

    ajaxprototype( "all" );

    function ajaxRequest(){}


    function addHeaders(){
        //console.log( fields );
        //console.log( values );

        for(var i = 0; i < colList.length; i++){
            //console.log( colList[i] );
        }
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

    function phaseChange( phase ){
        removeTables();
        addTables( phase );

        changeHeaders( phase );
        pullValues( phase );

        buildTable( values );

        //addTables
        //update show/hide
        //reload table
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
                        "<th rowspan='2'>Local Username</th>" +
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
                        "<th>Perf</th>" +
                    "</tr>" +
                    "</thead>";
                break;

            case "install":
                header =
                    "<thead>" +
                    "<tr id='headers' >" +
                        "<th rowspan='2'>Org</th>" +
                        "<th rowspan='2'>Local Username</th>" +
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
                        "<th rowspan='2'>Local Username</th>" +
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
                        "<th rowspan='2'>Local Username</th>" +
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

    function pullValues( phase, start, end ){

        //var http = require('http');
        var columnlist;
        var searchlist = getSearchTerms();


        switch( phase ){
            case "all":
                columnlist = allList;
                break;
            case "install":
                columnlist = installlist;
                break;
            case "build":
            case "run":
                columnlist = buildrunlist;
                break;
            default:
                break;
        }

        //function buildsearch(){

            function checkSearchTerm(terms, name) {
                var val = $('input[name=' + name + ']').val();
                if (val) {
                    terms[name] = val;
                }
            }

            function getSearchTerms() {
                var SEARCH_FIELDS = [ 'org', 'local_username', 'platform_name', 'platform_hardware', 'os_name', 'mpi_name', 'mpi_version', 'bitness', 'endian', 'compiler', 'compiler_version', 'suite' ];
                var terms = {};

                for (var i = SEARCH_FIELDS.length; i--;) {
                    checkSearchTerm(terms, SEARCH_FIELDS[i]);
                }

                terms.start_timestamp = start;
                terms.end_timestamp = end;

                return terms;
            }

        var jsonRequest =
        {
            "columns": columnlist,
            "phases": phase,
            "search": searchlist
        };


    // Setup the request.  The options parameter is
    // the object we defined above.

        function makeTheRequest ( json ){
            $.ajax({
                type: 'POST',
                url: 'http://138.49.30.31:9090/summary',
                dataType: 'json',
                async: false,
                data: json,
                contentType: 'application/json',
                success: function(data){
                    alert( JSON.stringify( data ) );
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    alert(xhr.status);
                    alert(thrownError);
                }

            })
        }

        //makeTheRequest( JSON.stringify(jsonRequest) );
        makeTheRequest( jsonRequest );



        alert( JSON.stringify( jsonRequest ) );




    }
    /*
     ****************************************************
     Table Configuration
     ****************************************************
     */

    function  buildTable( input ){
        table = $('#example').DataTable({
            "dom": '<"top">Rrtp<"bottom"li><"clear">',
            data: input
            //"columnDefs": [{
            //    "visible": false,
            //    "targets": -1
            //}]
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
                if ( $(selected).html() === hideColList[k] ) {
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

    var start = $( "#startdate" );
    var end = $( "#enddate" );

    //Uncommment when implementing final
    //start.datepicker().datepicker('setDate', "-1d" );
    //end.datepicker().datepicker('setDate', new Date() );

    var absoluteMin = new Date(2011, 0, 1);
    var absoluteMax = new Date(2014, 9, 29);

    $(function() {
        start.datepicker({
            //defaultDate: "+1w",
            defaultDate: "-1d",
            minDate: absoluteMin,
            maxDate: absoluteMax,
            changeMonth: true,
            numberOfMonths: 2,
            onClose: function (selectedDate) {
                end.datepicker("option", "minDate", selectedDate);
            }
        });
        end.datepicker({
            //defaultDate: "+1w",
            defaultDate: new Date(),
            minDate: absoluteMin,
            maxDate: absoluteMax,
            changeMonth: true,
            numberOfMonths: 2,
            onClose: function (selectedDate) {
                start.datepicker("option", "maxDate", selectedDate);
            }
        });
    });

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


    /*
     ****************************************************
     Event Listeners
     ****************************************************
     */


    //------------------DRILL DOWNS------------------

    //CSS Row selection
    var tabletr = '#example tbody tr';
    var tabletd = '#example tbody td';

    $( document ).on( 'click', tabletr, function () {
        table.$('tr.selected').removeClass('selected');
        $(this).addClass('selected');
    } );
    $( document ).on( 'dblclick', tabletr, function () {
        if ( $(this).hasClass('selected') ) {
            $(this).removeClass('selected');
        }
    });

    //Drill Down - grab td cell data
    var sqlbox = $('#sqlbox');

    $( document ).on( 'click', tabletd, function () {
        table.$('td.selected').removeClass('selected');
        $(this).addClass('selected');

        var field = $('.column_filter').eq( $(this).index() );

        if( field.val() === table.cell(this).data() ){
            field.val("");
            field.focus();
        } else {
            field.val( table.cell(this).data() );
            field.focus();
        }
    } );
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



    //------------------SQL MODE------------------

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

    //Summary
    $( 'button[value=summary]' ).on( 'click', function(){
        var requestformat =  'YYYY-MM-DD hh:mm:ss a';

        var startdate = getDate( $('select[name=dates] option:selected').attr('value') ).hours(0).minutes(0).seconds(0);
        var enddate = $( '#enddate' ).val();

        var startMoment = startdate.format( requestformat );
        var endMoment = moment( new Date(enddate) ).endOf('day').format( requestformat );

        pullValues( "all", startMoment, endMoment );

        console.log( "Date Range: " + startMoment + " to " + endMoment );



    });

    //start over
    $( document ).on( 'click', 'button[value=startover]', function(){

        $( 'input[type=text]').val('');

        $( 'select[name^=dates] option[value="past24hrs"]').attr("selected","selected");

        start.datepicker( 'setDate', '-1d' );
        end.datepicker( 'setDate', new Date() );

        //$('select[name^="salesrep"] option[value="Bruce Jones"]').attr("selected","selected");
    });

    //filter
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

        //alert( $('#org').parents('tr').attr('data-column') );
        color = extend.css('background-color');
        state = ( color === lightcoral );
    });

    //performance
    //$('button[value=perf]').on( 'click', function() { makeRequest('http://flux.cs.uwlax.edu:9090/fields') });
    $('button[value=perf]').on( 'click', function() { pullValues( "all" ) });



    //------------------FILTER MODE------------------

    //filter fields
    $( document ).on( 'keyup click focus', 'input.column_filter', function() {
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

});
