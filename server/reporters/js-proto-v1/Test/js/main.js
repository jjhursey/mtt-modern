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


    $('button[value=perf]').on( 'click', function() { makeRequest('http://flux.cs.uwlax.edu:9090/fields') });
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
      */



    /*
     ****************************************************
     Variable Declaration and Ajax Call
        Used in: Table Configuration
                 MultiSelect
     ****************************************************
     */


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
    var values2;

    var url = "ajax/data/pretty.json";
    //var url = "http://flux.cs.uwlax.edu/~jjhursey/mtt-tmp/pretty.json";

    $.ajax({
        dataType: "json",
        url: url
    })
        .done( function( data ){
            //fill variables
            fields = data.fields;
            values = data.values;

            for( var i = 0; i < data.fields.length; i++ ){
                setHeaders( data.fields[i] );
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

            fillColList();
            buildSelect();
            addHeaders();
            buildTable( values );
        });




    function addHeaders(){
        console.log( fields );
        console.log( values );

        for(var i = 0; i < colList.length; i++){
            console.log( colList[i] );
        }
    }




    /*
     ****************************************************
      Search Initialization
     ****************************************************
     */
    function filterGlobal () {
        $('#example').DataTable().search(
            $('#global_filter').val(),
            true,
            false
        ).draw();
    }

    function filterColumn ( i ) {
        $('#example').DataTable().column( i ).search(
            $( '.column_filter' ).eq( i ).val(),
            true,
            false
        ).draw();
    }

    /*
     ****************************************************
     Window Selection and Phase Change
     ****************************************************
     */

    function phaseChange( phase ){
        removeTables();
        addTables( phase );

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

    function buildFilterTableString( newColumns, table ){
        for( var i = 7; i < 11; i++ ){
            var dc = "" + (i - 1);
            var id1 = "filter_col" + i;
            var id2 = "col" + i + "_filter";


            table +=
                "<tr id='" + id1 + "' data-column='" + dc + "'>" +
                "<td> " + newColumns[ i-7 ] + " </td>" +
                "<td align='center'><input type='text' class='column_filter' id='" + id2 + "'></td>" +
                "</tr>";
        }
        return table;
    }

    /*
     ****************************************************
     Table Configuration
     ****************************************************
     */

    function  buildTable( input ){
        table = $('#example').DataTable({
            //"dom": 'C<"clear">Rlrtip',   l = amount per page
            "dom": '<"top">Rrtp<"bottom"li><"clear">',
            data: input,
            "columnDefs": [{
                "visible": false,
                "targets": -1
            }],

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

                "label": function (index, title, th) {
                    var count = 0;

                    if (title == "Pass") {
                        count++;
                    }

                    if (title == "Pass" || title == "Fail") {
                        return title + " - " + count;
                    } else {
                        return title;
                    }
                    //TODO: Make label dynamic
                }
            }

        });
    }

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
    var filterbox = $('#filterbox');
    var sqlbox = $('#sqlbox');
    var settingsbox = $('#settingsbox');

    $( tableSelector ).on( 'click', 'td', function () {
        table.$('td.selected').removeClass('selected');
        $(this).addClass('selected');

        //if( !filterbox.is(":visible") ){
        //    settingsbox.hide( "slow" );
        //    sqlbox.hide("slow");
        //    filterbox.show( "slow" );
        //}

        var field = $('.column_filter').eq( $(this).index() );

        if( field.val() === table.cell(this).data() ){
            field.val("");
            field.focus();
        } else {
            field.val( table.cell(this).data() );
            field.focus();
        }
    } );
    $( tableSelector ).on( 'dblclick', 'td', function () {
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


    //------------------SQL WINDOW------------------

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

        var startdate = getDate( $('select[name=dates] option:selected').attr('value') );
        var enddate = $( '#enddate' ).val();

        var startMoment = startdate.format( requestformat );
        var endMoment = moment( new Date(enddate) ).endOf('day').format( requestformat );

        console.log("Date Range: " + startMoment + " to " + endMoment );

        //console.log( "Org: " + $( 'input[id=org]' ).val() );
        //console.log( "Local Username: " + $( 'input[id=localusername]' ).val() );
        //console.log( "Platform Name: " + $( 'input[id=platform_name]' ).val() );
        //console.log( "Hardware: " + $( 'input[id=platform_hardware]' ).val() );
        //console.log( "OS: " + $( 'input[id=os_name]' ).val() );
        //console.log( "MPI Name: " + $( 'input[id=mpi_name]' ).val() );
        //console.log( "MPI Version: " + $( 'input[id=mpi_version]' ).val() );
        //console.log( moment.parsingFlags().invalidMonth );
    });

    //start over
    $( document ).on( 'click', 'button[value=startover]', function(){

        //start.datepicker( 'setDate', '-1d' );
        //end.datepicker( 'setDate', now );

        $( 'select[name^=dates] option[value="past24hrs"]').attr("selected","selected");

        $( 'input[type=text]').val('');

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



    //------------------FILTER WINDOW------------------

    //filter fields
    $('input.global_filter').on( 'keyup click', function() {
        filterGlobal();
    } );
    $( document ).on( 'keyup click focus', 'input.column_filter', function() {

        if( !state ) {
            filterColumn( $(this).parents('tr').attr('data-column') );
        }
    } );

    //Column show/hide toggle
    $('#show-hide').click( function(){
        toggleCols();
        console.log(" ");
    } );

    //Filter buttons
    $( document ).on( 'click', 'button[value=clear]', function(){
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
