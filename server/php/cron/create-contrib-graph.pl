#!/usr/bin/env perl

use strict;
use Env qw(HOME PATH USER);

#
# Script requires the following software packages installed:
# - psql (with access to the mtt database)
# - gnuplot (with postscript terminal)
# - ps2pdf
#

# Directory containing scripts to execute
my $working_dir = "/mnt/data/mtt.open-mpi.org/mtt/server/php/cron/stats";
# Directory to place the contribution graph
my $output_dir  = "/mnt/data/mtt.open-mpi.org/mtt/server/php/stats/";
# Temporary directory to store data files
my $tmp_dir = "/tmp/";

my $cmd;

my $is_limited_to_one_year = "f";

my $data_file_year  = "mtt-raw-year.data";
my $data_file_month = "mtt-raw-month.data";
my $data_file_week  = "mtt-raw-week.data";
my $data_file_day   = "mtt-raw-day.data";

my $gnuplot_file = "graph-raw-data.plot";
my $ps_file  = "mtt-contrib.ps";
my $pdf_file = "mtt-contrib.pdf";

my $extra_cmd_line_arg = "";

#
# Parse any command line arguments
#
if( 0 != parse_cmd_line() ) {
  print_usage();
  exit -1;
}

if(!chdir($working_dir) ) {
  print "Error: Cannot chdir to <$working_dir>\n";
  exit(-1);
}

if( $is_limited_to_one_year eq "t" ) {
    $extra_cmd_line_arg = " -l ";

    $data_file_year  .= "-1year";
    $data_file_month .= "-1year";
    $data_file_week  .= "-1year";
    $data_file_day   .= "-1year";

    $gnuplot_file = "graph-raw-data-1year.plot";
    $ps_file  = "mtt-contrib-1year.ps";
    $pdf_file = "mtt-contrib-1year.pdf";
}

#
# Gather the raw data
#
$cmd = "./make-raw-data.pl -year ".$extra_cmd_line_arg." > ".$tmp_dir.$data_file_year;
if(0 != system($cmd) ) {
  print "Error: Cannot exec the command <$cmd>\n";
  exit(-1);
}

$cmd = "./make-raw-data.pl -month ".$extra_cmd_line_arg." > ".$tmp_dir.$data_file_month;
if(0 != system($cmd) ) {
  print "Error: Cannot exec the command <$cmd>\n";
  exit(-1);
}

$cmd = "./make-raw-data.pl -week ".$extra_cmd_line_arg." > ".$tmp_dir.$data_file_week;
if(0 != system($cmd) ) {
  print "Error: Cannot exec the command <$cmd>\n";
  exit(-1);
}

$cmd = "./make-raw-data.pl -day ".$extra_cmd_line_arg." > ".$tmp_dir.$data_file_day;
if(0 != system($cmd) ) {
  print "Error: Cannot exec the command <$cmd>\n";
  exit(-1);
}

#
# Graph the data
#
$cmd = "gnuplot ".$gnuplot_file." 2> /dev/null 1> /dev/null";
if(0 != system($cmd) ) {
  print "Error: Cannot exec the command <$cmd>\n";
  exit(-1);
}

#
# Convert the ps -> pdf
#
$cmd = "ps2pdf ".$tmp_dir."/".$ps_file." ".$tmp_dir."/".$pdf_file;
if(0 != system($cmd) ) {
  print "Error: Cannot exec the command <$cmd>\n";
  exit(-1);
}

#
# Cleanup
#
$cmd = ("rm ".$tmp_dir."/".$ps_file." ".
        $tmp_dir.$data_file_year." ".
        $tmp_dir.$data_file_month." ".
        $tmp_dir.$data_file_week." ".
        $tmp_dir.$data_file_day);
if(0 != system($cmd) ) {
  print "Error: Cannot exec the command <$cmd>\n";
  exit(-1);
}

#
# Post the graph
#
$cmd = "mv ".$tmp_dir."/".$pdf_file." ".$output_dir."/";
if(0 != system($cmd) ) {
  print "Error: Cannot exec the command <$cmd>\n";
  exit(-1);
}

exit(0);

sub parse_cmd_line() {
  my $i = -1;
  my $argc = scalar(@ARGV);
  my $exit_value = 0;

  for($i = 0; $i < $argc; ++$i) {
    if( $ARGV[$i] eq "-h" ) {
      $exit_value = -1;
    }
    elsif( $ARGV[$i] eq "-l" ) {
      $is_limited_to_one_year = "t";
    }
    #
    # Invalid options produce a usage message
    #
    else {
      print "ERROR: Unknown argument [".$ARGV[$i]."]\n";
      $exit_value = -1;
    }
  }

  return $exit_value;
}

sub print_usage() {
  print "="x50 . "\n";
  print "Usage: ./create-contrib-graph.pl [-h] [-l]\n";
  print "="x50 . "\n";

  return 0;
}
