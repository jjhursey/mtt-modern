#!/usr/bin/env perl

#
# Convert the MTT v3 database to the MTT Flat database format
#

use strict;
use DBI;
use Data::Dumper;
use POSIX;

my $do_submit;
my $do_mpi_install;
my $do_test_build;
my $do_test_run = 0;
#my $do_test_run;

my $restrict_test_run;
##############
# 2015
##############
# (Down from here)
#$restrict_test_run = "start_timestamp >= '1-01-2015''";
#
##############
# 2014
##############
##$restrict_test_run = "start_timestamp >= '1-01-2014' AND start_timestamp < '6-01-2014'";
##$restrict_test_run = "start_timestamp >= '6-01-2014' AND start_timestamp < '1-01-2015'";
#
# (Down from here)
#$restrict_test_run = "start_timestamp >= '1-01-2014' AND start_timestamp < '4-01-2014'";
#$restrict_test_run = "start_timestamp >= '4-01-2014' AND start_timestamp < '7-01-2014'";
#$restrict_test_run = "start_timestamp >= '7-01-2014' AND start_timestamp < '11-01-2014'";
#$restrict_test_run = "start_timestamp >= '11-01-2014' AND start_timestamp < '1-01-2015'";
#
##############
# 2013
##############
##$restrict_test_run = "start_timestamp >= '1-01-2013' AND start_timestamp < '6-01-2013'";
##$restrict_test_run = "start_timestamp >= '6-01-2013' AND start_timestamp < '1-01-2014'";
#
# (Down from here)
#$restrict_test_run = "start_timestamp >= '1-01-2013' AND start_timestamp < '6-01-2013'";
#$restrict_test_run = "start_timestamp >= '6-01-2013' AND start_timestamp < '11-01-2013'";
#$restrict_test_run = "start_timestamp >= '11-01-2013' AND start_timestamp < '1-01-2014'";
#
##############
# 2012
##############
##$restrict_test_run = "start_timestamp >= '1-01-2012' AND start_timestamp < '6-01-2012'";
##$restrict_test_run = "start_timestamp >= '6-01-2012' AND start_timestamp < '1-01-2013'";
#
# (Down from here)
#$restrict_test_run = "start_timestamp >= '1-01-2012' AND start_timestamp < '2-01-2012'";
#$restrict_test_run = "start_timestamp >= '2-01-2012' AND start_timestamp < '4-04-2012'";
#$restrict_test_run = "start_timestamp >= '4-04-2012' AND start_timestamp < '5-09-2012'";
#$restrict_test_run = "start_timestamp >= '5-09-2012' AND start_timestamp < '7-01-2012'";
$restrict_test_run = "start_timestamp >= '7-01-2012' AND start_timestamp < '8-01-2012'";
#$restrict_test_run = "start_timestamp >= '8-01-2012' AND start_timestamp < '10-01-2012'";
#$restrict_test_run = "start_timestamp >= '10-01-2012' AND start_timestamp < '11-01-2012'";
#$restrict_test_run = "start_timestamp >= '11-01-2012' AND start_timestamp < '1-01-2013'";
#
##############
# < 2012
##############
# (Down from here)
#$restrict_test_run = "start_timestamp < '1-01-2012'";
#

#my $do_pushover_every = 20; # Percentage completed to pushover a message (leave blank if none)
my $do_pushover_every; # Percentage completed to pushover a message (leave blank if none)
my $pushover_message = "MTT Convert Update:";
my $pushover_script  = "pushover-notice.pl";

######################################################################
######################################################################

# Perform flush after each write to STDOUT
$| = 1;

my $rng = "";

if( scalar(@ARGV) == 2 ) {
    $restrict_test_run = "start_timestamp >= '".$ARGV[0]."' AND start_timestamp < '".$ARGV[1]."'";
    $rng = $ARGV[0]." to ".$ARGV[1];
}
elsif( scalar(@ARGV) == 1 ) {
    $restrict_test_run = "start_timestamp >= '".$ARGV[0]."'";
    $rng = $ARGV[0]." only";
}
elsif( scalar(@ARGV) == 0 ) {
    $restrict_test_run = "start_timestamp < '1-01-2012'";
    $rng = "1-01-2012 only (Default)";
}
else {
    print "Error: Invalid argument set\n";
    exit -1;
}

if( !defined($do_pushover_every) ) {
    system("$pushover_script $pushover_message Starting $rng");
}

#exit 0;

######################################################################
######################################################################

my $counter = 0;
my $progress_loop = 100;
my $progress_lw = 50;
my $cmd;


my $mtt_user = "mtt";
my $mtt_password;
my $mtt_db_v3 = "mttv3";
my $mtt_db_flat = "mttflat";

my $dbh_mttv3;
my $dbh_mttflat;

##########
# Grab password out of .pgpass, if available
$cmd = "grep \"".$mtt_user.":\" ~/.pgpass | cut -d : -f 5";
my @tmp = `$cmd`;
$mtt_password = $tmp[0];
chomp($mtt_password);
##########

if( defined($mtt_password) ) {
    $dbh_mttv3     = DBI->connect("dbi:Pg:dbname=".$mtt_db_v3,   $mtt_user);
    $dbh_mttflat   = DBI->connect("dbi:Pg:dbname=".$mtt_db_flat, $mtt_user);
}
else {
    $dbh_mttv3     = DBI->connect("dbi:Pg:dbname=".$mtt_db_v3,   $mtt_user, $mtt_password);
    $dbh_mttflat   = DBI->connect("dbi:Pg:dbname=".$mtt_db_flat, $mtt_user, $mtt_password);
}
$dbh_mttv3->{RaiseError} = 1;
$dbh_mttflat->{AutoCommit} = 0; # BEGIN a transaction
$dbh_mttflat->{RaiseError} = 1;

my $mttv3_stmt;
my $mttflat_stmt;
my $sub_stmt_submit_id;
my $sub_stmt_mpi_install_id;
my $sub_stmt_test_build_id;

my $rtn;
my $old_submit_id;
my $new_submit_id;
my $old_mpi_install_id;
my $new_mpi_install_id;
my $old_test_build_id;
my $new_test_build_id;

my $time_all_start;
my $time_all_end;
my $time_start;
my $time_end;

$time_all_start = time();
####################################################################################
####################################################################################
####################################################################################
my $opt_stmt;
my @sql_cmds = ();
push(@sql_cmds, "set sort_mem = '128MB'");

foreach my $sql_cmd (@sql_cmds) {
    my $opt_stmt = $dbh_mttv3->prepare( $sql_cmd );
    $opt_stmt->execute();
    my $opt_stmt = $dbh_mttflat->prepare( $sql_cmd );
    $opt_stmt->execute();
}

####################################################################################
####################################################################################
####################################################################################
if( defined($do_submit) ) {
    $time_start = time();
    system("date");

    convert_submit();
    $dbh_mttflat->commit;

    system("date");
    $time_end = time();
    print "Elapsed: " . get_time_diff_as_str($time_start, $time_end) . "\n";
}
else {
    print "Skipped... \t submit\n";
}


####################################################################################
####################################################################################
####################################################################################
if( defined($do_mpi_install) ) {
    $time_start = time();
    system("date");

    convert_mpi_install();
    $dbh_mttflat->commit;

    system("date");
    $time_end = time();
    print "Elapsed: " . get_time_diff_as_str($time_start, $time_end) . "\n";
}
else {
    print "Skipped... \t mpi_install\n";
}


####################################################################################
####################################################################################
####################################################################################
if( defined($do_test_build) ) {
    $time_start = time();
    system("date");

    convert_test_build();
    $dbh_mttflat->commit;

    system("date");
    $time_end = time();
    print "Elapsed: " . get_time_diff_as_str($time_start, $time_end) . "\n";
}
else {
    print "Skipped... \t test_build\n";
}


####################################################################################
####################################################################################
####################################################################################
if( defined($do_test_run) ) {
    $time_start = time();
    system("date");

    convert_test_run();
    $dbh_mttflat->commit;

    system("date");
    $time_end = time();
    print "Elapsed: " . get_time_diff_as_str($time_start, $time_end) . "\n";
}
else {
    print "Skipped... \t test_run\n";
}

####################################################################################
####################################################################################
####################################################################################
print "\n";
print "-"x50 . "\n";
print "--- DONE...\n";
print "-"x50 . "\n";

$time_all_end = time();
my $el = get_time_diff_as_str($time_all_start, $time_all_end);
print "Total Elapsed: " . $el . "\n";
system("$pushover_script $pushover_message All Done in \"$el\"");

exit 0;



sub convert_submit() {
    print "\n";
    print "-"x50 . "\n";
    print "--- Converting the table: submit\n";
    print "-"x50 . "\n";


    #----------------------------------------------------------
    printf("Setup...\n");
    $mttv3_stmt = $dbh_mttv3->prepare(
        "SELECT ".
        "submit_id, hostname, local_username, http_username, mtt_client_version ".
        "FROM ".
        "submit ".
        "ORDER BY submit_id ASC "
        );

    $mttflat_stmt = $dbh_mttflat->prepare(
        "INSERT into submit ".
        "(submit_id, old_submit_id, hostname, local_username, http_username, mtt_client_version) ".
        "VALUES (DEFAULT,?,?,?,?,?)"
        );


    #----------------------------------------------------------
    printf("Extracting original values...\n");
    $mttv3_stmt->execute();


    #----------------------------------------------------------
    $counter = 0;
    printf("Starting conversion...\n");
    while(my $mttv3_row_ref = $mttv3_stmt->fetchrow_arrayref ) {
        #print Dumper($mttv3_row_ref);
        #print "-"x50 . "\n";

        $rtn = $mttflat_stmt->execute($mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{submit_id} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{hostname} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{local_username} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{http_username} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{mtt_client_version} ]);
        if( $rtn != 1 ) {
            print "Error: Inserting) [$rtn] " . $mttflat_stmt->errstr . "\n";
        }

        $counter++;
        if( $counter % $progress_loop == 0 ) {
            print ".";
        }
        if( $counter % ($progress_loop*$progress_lw) == 0 ) {
            my $elapsed = get_time_diff_as_str($time_start, time());
            printf(" = %10d (%s)\n", $counter, $elapsed);
        }
    }
    print "\n";

}

sub convert_mpi_install() {
    my $total_rows = 0;

    print "\n";
    print "-"x50 . "\n";
    print "--- Converting the table: mpi_install\n";
    print "-"x50 . "\n";

    #----------------------------------------------------------
    printf("Setup...\n");
    $mttv3_stmt = $dbh_mttv3->prepare("SELECT count(mpi_install_id) as count from mpi_install");
    $mttv3_stmt->execute();
    while( my $tmp_ref = $mttv3_stmt->fetchrow_arrayref ) {
        $total_rows = $tmp_ref->[$mttv3_stmt->{NAME_lc_hash}{count}];
    }

    $mttv3_stmt = $dbh_mttv3->prepare(
        "SELECT ".
        "mpi_install_id, submit_id, platform_name, platform_hardware, platform_type, ".
        "os_name, os_version, mpi_name, mpi_version, compiler_name, compiler_version, ".
        "vpath_mode, bitness, endian, configure_arguments, ".
        "description, start_timestamp, submit_timestamp, duration, trial, ".
        "test_result, environment, result_stdout, result_stderr, result_message, merge_stdout_stderr, ".
        "exit_value, exit_signal ".
        "FROM ".
        "mpi_install JOIN submit using (submit_id) ".
        "JOIN compute_cluster using (compute_cluster_id) ".
        "JOIN compiler on (mpi_install.mpi_install_compiler_id = compiler.compiler_id) ".
        "JOIN mpi_get using (mpi_get_id) ".
        "JOIN mpi_install_configure_args using (mpi_install_configure_id) ".
        "JOIN description using (description_id) ".
        "JOIN environment using (environment_id) ".
        "JOIN result_message using (result_message_id) ".
        "ORDER BY mpi_install_id ASC "
        );

    $sub_stmt_submit_id = $dbh_mttflat->prepare(
        "SELECT submit_id from submit where old_submit_id = ?"
        );

    $mttflat_stmt = $dbh_mttflat->prepare(
        "INSERT into mpi_install ".
        "(".
        "mpi_install_id, old_mpi_install_id, submit_id, ".
        "platform_name, platform_hardware, platform_type, ".
        "os_name, os_version, mpi_name, mpi_version, compiler_name, compiler_version, ".
        "vpath_mode, bitness, endian, configure_arguments, ".
        "description, start_timestamp, submit_timestamp, duration, trial, ".
        "test_result, environment, result_stdout, result_stderr, result_message, merge_stdout_stderr, ".
        "exit_value, exit_signal ".
        ") ".
        "VALUES (DEFAULT,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        );


    #----------------------------------------------------------
    printf("Extracting original values...\n");
    $mttv3_stmt->execute();


    #----------------------------------------------------------
    $counter = 0;
    printf("Starting conversion...\n");
    while(my $mttv3_row_ref = $mttv3_stmt->fetchrow_arrayref ) {
        #
        # First convert the submit id
        #
        $old_submit_id = $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{submit_id} ];
        $sub_stmt_submit_id->execute( $old_submit_id );

        while( my $tmp_ref = $sub_stmt_submit_id->fetchrow_arrayref ) {
            $new_submit_id = $tmp_ref->[$sub_stmt_submit_id->{NAME_lc_hash}{submit_id}];
        }
        

        #
        # Now insert the values
        #
        $rtn = $mttflat_stmt->execute($mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{mpi_install_id} ],
                                      $new_submit_id,
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{platform_name} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{platform_hardware} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{platform_type} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{os_name} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{os_version} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{mpi_name} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{mpi_version} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{compiler_name} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{compiler_version} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{vpath_mode} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{bitness} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{endian} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{configure_arguments} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{description} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{start_timestamp} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{submit_timestamp} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{duration} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{trial} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{test_result} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{environment} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{result_stdout} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{result_stderr} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{result_message} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{merge_stdout_stderr} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{exit_value} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{exit_signal} ]
            );
        if( $rtn != 1 ) {
            print "Error: Inserting) [$rtn] " . $mttflat_stmt->errstr . "\n";
        }

        $counter++;
        if( $counter % $progress_loop == 0 ) {
            print ".";
        }
        if( $counter % ($progress_loop*$progress_lw) == 0 ) {
            my $elapsed = get_time_diff_as_str($time_start, time());
            printf(" = %10d of %10s (%s)\n", $counter, $total_rows, $elapsed);
        }
    }
    print "\n";
}

sub convert_test_build() {
    my $total_rows = 0;

    print "\n";
    print "-"x50 . "\n";
    print "--- Converting the table: test_build\n";
    print "-"x50 . "\n";

    #----------------------------------------------------------
    printf("Setup...\n");
    $mttv3_stmt = $dbh_mttv3->prepare("SELECT count(test_build_id) as count from test_build");
    $mttv3_stmt->execute();
    while( my $tmp_ref = $mttv3_stmt->fetchrow_arrayref ) {
        $total_rows = $tmp_ref->[$mttv3_stmt->{NAME_lc_hash}{count}];
    }

    $mttv3_stmt = $dbh_mttv3->prepare(
        "SELECT ".
        "test_build_id, mpi_install_id, submit_id, ".
        "compiler_name, compiler_version, ".
        "suite_name, test_suite_description, ".
        "description, start_timestamp, submit_timestamp, duration, trial, ".
        "test_result, environment, result_stdout, result_stderr, result_message, merge_stdout_stderr, ".
        "exit_value, exit_signal ".
        "FROM ".
        "test_build JOIN submit using (submit_id) ".
        "JOIN test_suites using (test_suite_id) ".
        "JOIN compiler on (test_build.test_build_compiler_id = compiler.compiler_id) ".
        "JOIN description using (description_id) ".
        "JOIN environment using (environment_id) ".
        "JOIN result_message using (result_message_id) ".
        "ORDER BY test_build_id ASC "
        );

    $sub_stmt_submit_id = $dbh_mttflat->prepare(
        "SELECT submit_id from submit where old_submit_id = ?"
        );

    $sub_stmt_mpi_install_id = $dbh_mttflat->prepare(
        "SELECT mpi_install_id from mpi_install where old_mpi_install_id = ?"
        );

    $mttflat_stmt = $dbh_mttflat->prepare(
        "INSERT into test_build ".
        "(".
        "test_build_id, old_test_build_id, mpi_install_id, submit_id, ".
        "compiler_name, compiler_version, ".
        "test_suite_name, test_suite_description, ".
        "description, start_timestamp, submit_timestamp, duration, trial, ".
        "test_result, environment, result_stdout, result_stderr, result_message, merge_stdout_stderr, ".
        "exit_value, exit_signal ".
        ") ".
        "VALUES (DEFAULT,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        );


    #----------------------------------------------------------
    printf("Extracting original values...\n");
    $mttv3_stmt->execute();


    #----------------------------------------------------------
    $counter = 0;
    printf("Starting conversion...\n");
    while(my $mttv3_row_ref = $mttv3_stmt->fetchrow_arrayref ) {
        #
        # First convert the submit id
        #
        $old_submit_id = $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{submit_id} ];
        $sub_stmt_submit_id->execute( $old_submit_id );

        while( my $tmp_ref = $sub_stmt_submit_id->fetchrow_arrayref ) {
            $new_submit_id = $tmp_ref->[$sub_stmt_submit_id->{NAME_lc_hash}{submit_id}];
        }


        #
        # Second, find the mpi_install_id
        #
        $old_mpi_install_id = $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{mpi_install_id} ];
        $sub_stmt_mpi_install_id->execute( $old_mpi_install_id );

        $new_mpi_install_id = 0; #  BOGUS
        while( my $tmp_ref = $sub_stmt_mpi_install_id->fetchrow_arrayref ) {
            $new_mpi_install_id = $tmp_ref->[$sub_stmt_mpi_install_id->{NAME_lc_hash}{mpi_install_id}];
        }
        

        #
        # Now insert the values
        #
        $rtn = $mttflat_stmt->execute($mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{test_build_id} ],
                                      $new_mpi_install_id,
                                      $new_submit_id,
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{compiler_name} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{compiler_version} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{suite_name} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{test_suite_description} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{description} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{start_timestamp} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{submit_timestamp} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{duration} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{trial} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{test_result} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{environment} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{result_stdout} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{result_stderr} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{result_message} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{merge_stdout_stderr} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{exit_value} ],
                                      $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{exit_signal} ]
            );
        if( $rtn != 1 ) {
            print "Error: Inserting) [$rtn] " . $mttflat_stmt->errstr . "\n";
        }

        $counter++;
        if( $counter % $progress_loop == 0 ) {
            print ".";
        }
        if( $counter % ($progress_loop*$progress_lw) == 0 ) {
            my $elapsed = get_time_diff_as_str($time_start, time());
            printf(" = %10d of %10s (%s)\n", $counter, $total_rows, $elapsed);
        }
    }
    print "\n";
}


sub convert_test_run() {
    my $current_percentage = 0;
    my $last_reported_percentage = 0;
    my $current_iteration = 0;
    my $total_rows = 0;
    my $current_num_rows = 0;

    #my $current_limit = 150000;
    #my $current_limit = 200000;
    #my $current_limit = 400000;
    my $current_limit = 1600000;
    my $current_offset = 0;

    my $last_mpi_install_id = -1;
    my $last_test_build_id = -1;

    print "\n";
    print "-"x50 . "\n";
    print "--- Converting the table: test_run\n";
    print "    Range: $restrict_test_run\n";
    print "-"x50 . "\n";

    $progress_loop = 1000;

    #----------------------------------------------------------
    printf("Setup...\n");

    if( !defined($restrict_test_run) ) {
        $restrict_test_run = " ";
    }
    else {
        $restrict_test_run = " WHERE $restrict_test_run ";
    }


    $mttv3_stmt = $dbh_mttv3->prepare("SELECT count(test_run_id) as count from test_run " . $restrict_test_run);
    $mttv3_stmt->execute();
    while( my $tmp_ref = $mttv3_stmt->fetchrow_arrayref ) {
        $total_rows = $tmp_ref->[$mttv3_stmt->{NAME_lc_hash}{count}];
    }

    printf("Processing %10d rows...\n", $total_rows);
    sleep(2);
    printf("-----------------------\n");


    $mttv3_stmt = $dbh_mttv3->prepare(
        "SELECT ".
        "test_run_id, test_build_id, mpi_install_id, submit_id, ".
        "np, full_command, ".
        "test_name, test_name_description, ".
        "launcher, resource_mgr, parameters, network, ".
        "description, start_timestamp, submit_timestamp, duration, trial, ".
        "test_result, environment, result_stdout, result_stderr, result_message, merge_stdout_stderr, ".
        "exit_value, exit_signal ".
        "FROM ".
        "test_run JOIN test_names using (test_name_id) ".
        "JOIN test_run_command using (test_run_command_id) ".
        "JOIN description using (description_id) ".
        "JOIN environment using (environment_id) ".
        "JOIN result_message using (result_message_id) ".
        $restrict_test_run .
        "ORDER BY test_run_id ASC ".
        "LIMIT ? ".
        "OFFSET ?"
        );

    $sub_stmt_submit_id = $dbh_mttflat->prepare(
        "SELECT submit_id from submit where old_submit_id = ?"
        );

    $sub_stmt_test_build_id = $dbh_mttflat->prepare(
        "SELECT test_build_id, mpi_install_id from test_build where old_test_build_id = ?"
        );

    $mttflat_stmt = $dbh_mttflat->prepare(
        "INSERT into test_run ".
        "(".
        "test_run_id, old_test_run_id, test_build_id, mpi_install_id, submit_id, ".
        "test_name, test_name_description, ".
        "launcher, resource_mgr, parameters, network, np, full_command, ".
        "description, start_timestamp, submit_timestamp, duration, trial, ".
        "test_result, environment, result_stdout, result_stderr, result_message, merge_stdout_stderr, ".
        "exit_value, exit_signal ".
        ") ".
        "VALUES (DEFAULT,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        );


    #----------------------------------------------------------
    $counter = 0;
    $current_num_rows = 1;
    while ( $current_num_rows > 0 ) {
        printf("Extracting original values... (iteration = %4d)\n", $current_iteration);

        $mttv3_stmt->execute($current_limit, $current_offset);
        if( 0 != $mttv3_stmt->err ) {
            print "Error: (".$mttv3_stmt->err.") Fatal! ".$mttv3_stmt->errstr."\n";
            $dbh_mttflat->rollback;
            exit(-1);
        }
        $current_num_rows = $mttv3_stmt->rows;

        if( $current_num_rows <= 0 ) {
            printf("Finished with test_run...\n");
            last;
        }

        #----------------------------------------------------------
        printf("Starting conversion...  (iter. = %3d, rows = %4d [%10d,    %10d])\n",
               $current_iteration, $current_num_rows, $current_limit, $current_offset);
        while(my $mttv3_row_ref = $mttv3_stmt->fetchrow_arrayref ) {
            #
            # First convert the submit id
            #
            $old_submit_id = $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{submit_id} ];
            $sub_stmt_submit_id->execute( $old_submit_id );

            while( my $tmp_ref = $sub_stmt_submit_id->fetchrow_arrayref ) {
                $new_submit_id = $tmp_ref->[$sub_stmt_submit_id->{NAME_lc_hash}{submit_id}];
            }


            #
            # Next, find the mpi_install_id, test_build_id
            #
            $old_test_build_id = $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{test_build_id} ];

            if( $old_test_build_id != $last_test_build_id ) {
                $last_test_build_id = $old_test_build_id;
                $sub_stmt_test_build_id->execute( $old_test_build_id );

                $new_test_build_id = 0; #  BOGUS
                while( my $tmp_ref = $sub_stmt_test_build_id->fetchrow_arrayref ) {
                    $new_mpi_install_id = $tmp_ref->[$sub_stmt_test_build_id->{NAME_lc_hash}{mpi_install_id}];
                    $new_test_build_id = $tmp_ref->[$sub_stmt_test_build_id->{NAME_lc_hash}{test_build_id}];
                }
            }

            #
            # Now insert the values
            #
            $rtn = $mttflat_stmt->execute($mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{test_run_id} ],
                                          $new_test_build_id,
                                          $new_mpi_install_id,
                                          $new_submit_id,
                                          $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{test_name} ],
                                          $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{test_name_description} ],
                                          $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{launcher} ],
                                          $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{resource_mgr} ],
                                          $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{parameters} ],
                                          $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{network} ],
                                          $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{np} ],
                                          $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{full_command} ],
                                          $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{description} ],
                                          $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{start_timestamp} ],
                                          $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{submit_timestamp} ],
                                          $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{duration} ],
                                          $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{trial} ],
                                          $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{test_result} ],
                                          $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{environment} ],
                                          $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{result_stdout} ],
                                          $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{result_stderr} ],
                                          $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{result_message} ],
                                          $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{merge_stdout_stderr} ],
                                          $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{exit_value} ],
                                          $mttv3_row_ref->[ $mttv3_stmt->{NAME_lc_hash}{exit_signal} ]
                );
            if( $rtn != 1 ) {
                print "Error: Inserting) [$rtn] " . $mttflat_stmt->errstr . "\n";
            }

            #
            # Status/Progress report
            #
            $counter++;
            $current_percentage = ((($counter*1.0)/$total_rows)*100.0);
            if( $counter % $progress_loop == 0 ) {
                print ".";
            }
            if( $counter % ($progress_loop*$progress_lw) == 0 ) {
                my $elapsed = get_time_diff_as_str($time_start, time());
                printf(" = %10d of %10s (%s) [%5.1f%%]\n",
                       $counter, $total_rows, $elapsed, $current_percentage);
            }
            if( defined($do_pushover_every) ) {
                if( $current_percentage >= $last_reported_percentage + $do_pushover_every ) {
                    my $elapsed = get_time_diff_as_str($time_start, time());
                    my $perc_str = sprintf("%4.1f", $current_percentage);
                    $last_reported_percentage += $do_pushover_every;
                    system("$pushover_script $pushover_message \"".$perc_str."%\" in \"$elapsed\"");
                }
            }
        }
        print "\n";

        # Progress
        $current_offset += $current_limit;
        $current_iteration += 1;
    }
}

sub get_time_diff_as_str() {
    my $t1 = shift(@_);
    my $t2 = shift(@_);
    my $str;
    my $time_str = strftime("\%H:\%M:\%S", gmtime( $t2 - $t1 ));
    my $day_str = int(strftime("\%d", gmtime( $t2 - $t1 ))) - 1;
    
    $str = sprintf("%d day(s) %s", $day_str, $time_str);

    return $str;
}
