#!/usr/bin/env perl
#
# Copyright (c) 2005-2006 The Trustees of Indiana University.
#                         All rights reserved.
# $COPYRIGHT$
# 
# Additional copyrights may follow
# 
# $HEADER$
#

use strict;
use Data::Dumper;
use Getopt::Long;
use File::Basename;
use Cwd;

# Try to find the MTT files.  Assume that mtt executable is in the
# base directory for the MTT files.  Try three methods:

# 1. With no effort; see if we can just "require" and find MTT files.
# 2. If $0 is a path, try adding that do @INC and try "require" again.
# 3. Otherwise, search $ENV[PATH] for mtt, and when you find it, add
#    that directory to @INC and try again.

use lib cwd() . "/lib";

my $ret;
eval "\$ret = require MTT::Version";
if (1 != $ret) {
    my $dir = dirname($0);
    my @INC_save = @INC;

    # Change to the dir of $0 (because it might be a relative
    # directory) and add the cwd() to @INC
    my $start_dir = cwd();
    chdir($dir);
    chdir("..");
    push(@INC, cwd() . "/lib");
    chdir($start_dir);
    eval "\$ret = require MTT::Version";

    # If it didn't work, restore @INC and try looking for mtt in the
    # path

    if (1 != $ret) {
        @INC = @INC_save;
        my @dirs = split(/:/, $ENV{PATH});
        my $mtt = basename($0);
        foreach my $dir (@dirs) {

            # If we found the mtt executable, add the dir to @INC and
            # see if we can "require".  If require fails, restore @INC
            # and keep trying.
            if (-x "$dir/$mtt") {
                chdir($dir);
                chdir("..");
                push(@INC, cwd() . "/lib");
                chdir($start_dir);
                eval "\$ret = require MTT::Version";
                if (1 == $ret) {
                    last;
                } else {
                    @INC = @INC_save;
                }
            }
        }
    }

    # If we didn't find them, die.
    die "Unable to find MTT support libraries"
        if (0 == $ret);
}

# Must use "require" (run-time) for all of these, not "use"
# (compile-time)

require Config::IniFiles;
require MTT::Version;
#require MTT::MPI;
#require MTT::Test;
#require MTT::Files;
require MTT::Messages;
#require MTT::INI;
#require MTT::Reporter;
#require MTT::Constants;
require MTT::FindProgram;
#require MTT::Trim;


my $PBCMD = "perfbase query -d query_mpi_install.xml";
my $SEP = "=====================================================================\n";
my $LINETOKEN = "XXXXX";


my $mpi_install_arg;
my $test_build_arg;
my $test_run_arg;
my $perfbase_arg;
my $email_arg;
my $debug_arg;
my $verbose_arg;
my $version_arg;
my $help_arg;

# TODO - take the stdout_stderr_combined field into account in output
#  make it clear that they are combined or not
# should probably hide stdout if none is given

&Getopt::Long::Configure("bundling", "require_order");
my $ok = Getopt::Long::GetOptions("mpi-install=s" => \$mpi_install_arg,
                                  "test-build=s" => \$test_build_arg,
                                  "test-run=s" => \$test_run_arg,
                                  "perfbase|p=s" => \$perfbase_arg,
                                  "email|e=s" => \$email_arg,
                                  "debug|d=s" => \$debug_arg,
                                  "verbose|v=s" => \$verbose_arg,
                                  "version=s" => \$version_arg,
                                  "help=s" -> \$help_arg);

if($version_arg) {
    print "MTT Version $MTT::Version::Major.$MTT::Version::Minor\n";
    exit(0);
}
if(!$mpi_install_arg && !$test_build_arg && !$test_run_arg) {
    print "Must specify at least one of --mpi-install, --test-build, or\n",
          "--test-run arguments.\n";
    $ok = 0;
}

if(!$ok || $help_arg) {
    print("Command line error\n") if(!$ok);

    print "Options:
--mpi-install <mpi install xml>     Specify the MPI install query XML
--test-build <test build xml>       Specify the test build query XML
--test-run <test run xml>           Specify the test run query XML
--perfbase <full path>              Location of perfbase binary
--email|e <send address>            Address to email reports to
--debug|d                           Debug mode enable
--verbose|v                         Verbose mode enable
--version                           MTT version information
--help}h                            This help message\n";

    exit($ok);
}

# Check debug
my $debug = $debug_arg ? 1 : 0;
my $verbose = $verbose_arg ? 1 : 0;
MTT::Messages::Messages($debug, $verbose);
MTT::Messages::Debug("Debug is $debug, Verbose is $verbose\n");


# Take a line of input, and if it is the column header line,
#  return an array containing the column headers.  Otherwise, return undef.
sub ParseHeaders {
    my ($line) = @_;
    my @columns;

    # We key on '# ' to determine if this is a column header line.
    return undef unless $line =~ /^# /;

    # Must be column header line.. break it up!
    $line =~ s/^# (.+\[\])+//;
    $line =~ s/\[\]//g;
    @columns = split(/\t/, $line);

    return @columns;
}


# Take a hash of results and generate text output
sub GenOutput {
    my (%results) = @_;

    #print Dumper(%results);

    # Split stderr/stdout/environment back into multiple lines
    $results{'environment'} =~ s/$LINETOKEN/\n/g;
    $results{'stdout'} =~ s/$LINETOKEN/\n/g;
    $results{'stderr'} =~ s/$LINETOKEN/\n/g;

    my $output = $SEP .
        "MPI Name: $results{'mpi_name'} $results{'mpi_version'}\n\n" .
        "Hostname: $results{'hostname'}\n" .
        "Operating System: $results{'os_version'}\n" .
        "Platform Type: $results{'platform_type'}\n" .
        "Platform ID: $results{'platform_id'}\n" .
        "Compiler: $results{'compiler_name'} $results{'compiler_version'}\n" .
        "Configure Arguments: $results{'configure_arguments'}\n" .
        "Start Date: $results{'start_timestamp'}\n" .
        "Finish Date: $results{'stop_timestamp'}\n\n" .
        "Result: $results{'result_message'}\n\n" .
        "Environment:\n$results{'environment'}\n\n" .
        "Stdout:\n$results{'stdout'}\n\n" .
        "Stderr:\n$results{'stderr'}\n";

    return $output;
}


# Run the perfbase query
if(!open(PBQUERY, "$PBCMD|")) {
    print "Unable to run query!\n";
    die;
}

my @output = <PBQUERY>;
chomp(@output);
close(PBQUERY);

# Find the column header line and parse it.
my @columns;
for(@output) {
    @columns = ParseHeaders($_);
    last if defined(@columns);
}


# Now we have the field names in an array.
# Loop over each line, putting all the results for that line into a hash.
# The keys in this hash are the field names, the values are results.

my $mailbody = "";
my $successes = 0;
my $failures = 0;

for(@output) {
    # Skip commented lines
    next if($_ =~ /^#/);

    print ("line: $_\n");
    my $i = 0;
    my %results;
    for(split(/\t/, $_)) {
        $_ =~ s/ *$//;
        $results{$columns[$i]} = $_;
        $i++;
    }

    if($results{'result_message'} eq "Success") {
        $successes++;
     } else {
         $failures++;
     }
#    print Dumper(%results);
    $mailbody .= GenOutput(%results);
}

# Put the header on the front of the mail body.
$mailbody = "MTT MPI Install Report\n\n" .
    "Summary:\n" .
    " $successes Successful installs\n" .
    " $failures Failed installs\n\n" .
    $mailbody;

print "$mailbody\n";
# TODO: Only show results in the past day
# Sum up success/failure counts
# Actually send off the email..

# Get the current date in seconds since epoch
# subtract 60*60*24 seconds from the current date

