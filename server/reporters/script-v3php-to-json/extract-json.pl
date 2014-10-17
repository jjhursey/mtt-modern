#!/bin/env perl

#
# Copyright (c) 2014      University of Wisconsin - La Crosse
#                         All rights reserved.
# $COPYRIGHT$
#
# Additional copyrights may follow
#
# $HEADER$
#

use strict;

my $debug;



my $MAKE_PRETTY = 1;
my $MAKE_FLAT   = 0;

my $cmd;
my @table_data = ();
my $table_data_pos = 0;
my $table_data_len = 0;

my @table_header = ();

my @all_data = ();

main();

exit 0;

sub main() {
  #
  # Grab the latest data from the existing reporter
  #
  my $raw_file = get_raw_data();
  my $line;
  my $line_num = 0;
  my $table_num = 0;

  #
  # Open the file
  #
  open(RAW_WWW, "$raw_file") or die $!;

  #
  # Search for the results table and save it into memory
  #
  while($line = <RAW_WWW> ) {
    $line_num += 1;
    chomp($line);
    if( $line =~ /^<table width/ ) {
      $table_num += 1;
    }

    if( $table_num == 5 ) {
      if( $line =~ /^<\/table/ ) {
        $table_num = 0;
      }
      else {
        #print $line_num . ") Table Start: $line\n";
        push(@table_data, $line);
      }
    }

  }

  #
  # Close the file
  #
  close(RAW_WWW);
  $table_data_len = scalar(@table_data);

  #
  # Extract the header from the table
  #
  extract_header();
  #print "Line number: $table_data_pos vs $table_data_pos\n";
  # Shift of the "#" field
  shift(@table_header);


  #
  # Extract all of the row data
  #
  extract_rows();

  #
  # Display the data
  #
  #display_data();

  #
  # Display the data in JSON format
  #
  my $pretty_json = "pretty.json";
  my $flat_json = "flat.json";
  open( PRETTY, ">$pretty_json") or die $!;
  display_data_json( $MAKE_PRETTY, \*PRETTY );
  close( PRETTY );

  open( PRETTY, ">$flat_json") or die $!;
  display_data_json( $MAKE_FLAT, \*PRETTY);
  close( PRETTY );

  #
  # Cleanup
  #
  if( !defined($debug) ) {
    $cmd = "rm $raw_file";
    system($cmd);
  }

  return 0;
}

sub display_data_json() {
  my $pretty = shift(@_);
  my $fh = shift(@_);

  print $fh "{";
  print $fh "\n" if( $pretty );

  print $fh "    " if( $pretty );
  print $fh "\"fields\": [";
  print $fh "\n" if( $pretty );

  for my $i (0 .. $#table_header) {
    if( $i != 0 ) {
      print $fh ",";
      print $fh "\n" if( $pretty );
    }
    print $fh "      " if( $pretty );
    print $fh "\"". $table_header[$i] ."\"";
  }
  print $fh "\n    " if( $pretty );
  print $fh "],";
  print $fh "\n" if( $pretty );

  print $fh "    " if( $pretty );
  print $fh "\"values\": [";
  print $fh "\n" if( $pretty );
  for my $i (0 .. $#all_data) {
    if( $i != 0 ) {
      print $fh ",";
      print $fh "\n" if( $pretty );
    }
    print $fh "        " if( $pretty );
    print $fh "[";
    print $fh "\n" if( $pretty );

    for my $j (0 .. $#{ $all_data[$i] }) {
      if( $j != 0 ) {
        print $fh ",";
        print $fh "\n" if( $pretty );
      }
      print $fh "            " if( $pretty );
      print $fh "\"".$all_data[$i][$j]."\"";
    }
    print $fh "\n" if( $pretty );
    print $fh "        " if( $pretty );
    print $fh "]";
  }

  print $fh "\n" if( $pretty );
  print $fh "}";
  print $fh "\n" if( $pretty );

  print $fh "\n";
  return 0;
}

sub display_data() {
  for my $i (0 .. $#table_header) {
    printf("%-20s\t", $table_header[$i]);
  }
  printf("\n");

  for my $i (0 .. $#all_data) {

    for my $j (0 .. $#{ $all_data[$i] }) {
      printf("%-20s\t", $all_data[$i][$j]);
    }
    printf("\n");
  }

  return 0;
}

sub extract_rows() {
  my $line;
  my $num_rows = 0;
  my @tmp_values = ();

  while( $table_data_pos < $table_data_len ) {
    $line = $table_data[ $table_data_pos ];

    #print "Search: " . substr($line, 0, 50) . "\n";
    if( $line =~ /<tr/ ) {
      if( scalar(@tmp_values) > 0 ) {
        # Shift of the "#" field
        shift(@tmp_values);
        push(@all_data, [ @tmp_values ] );
      }
      @tmp_values = ();

      $num_rows += 1;
    }
    elsif( $line =~ /<td/ ) {
      $line =~ s/<.*?>//g;

      #printf("--%2d--> ", $num_rows);
      #print "" . $line . "\n";

      push(@tmp_values, $line);
    }

    $table_data_pos += 1;
  }

  # Skipping the last row with totals...
  #if( scalar(@tmp_values) > 0 ) {
  #  push(@all_data, [ @tmp_values ] );
  #}

  return 0;
}

sub extract_header() {
  my $line;

  while( $table_data_pos < $table_data_len ) {
    $line = $table_data[ $table_data_pos ];
    if( $line =~ /<th bgcolor/ ) {
      #print "Header: " . substr($line, 0, 20) . "\n";
      #print "Header: " . $line . "\n\n";
      $line =~ s/<.*?>//g;
      #print "Header: " . $line . "\n\n";
      if( $line =~ /MPI install/i ) {
        push(@table_header, ($line . " Pass") );
        push(@table_header, ($line . " Fail") );
      }
      elsif( $line =~ /Test build/i ) {
        push(@table_header, ($line . " Pass") );
        push(@table_header, ($line . " Fail") );
      }
      elsif( $line =~ /Test run/i ) {
        push(@table_header, ($line . " Pass") );
        push(@table_header, ($line . " Fail") );
        push(@table_header, ($line . " Skip") );
        push(@table_header, ($line . " Timed") );
        push(@table_header, ($line . " Perf") );
      }
      else {
        push(@table_header, $line);
      }

    }
    elsif( $line =~ /<th id='result'/ ) {
      #print "Result: " . substr($line, 0, 20) . "\n";
      #print "Result: " . $line . "\n";
      $line =~ s/<.*?>//g;
      #print "----->: " . $line . "\n";
    }
    elsif( scalar(@table_header) > 1 && $line =~ /<td bgcolor/ ) {
      $table_data_pos -= 1;
      return 0;
    }
    $table_data_pos += 1;
  }

  return 0;
}

sub get_raw_data() {
  my $url = "http://mtt.open-mpi.org/index.php?limit=&wrap=&trial=&enable_drilldowns=&yaxis_scale=&xaxis_scale=&hide_subtitle=&split_graphs=&remote_go=&do_cookies=&phase=all_phases&text_start_timestamp=past+24+hours&text_platform_hardware=all&show_platform_hardware=show&text_os_name=all&show_os_name=show&text_mpi_name=all&show_mpi_name=show&text_mpi_version=all&show_mpi_version=show&text_http_username=all&show_http_username=show&text_local_username=all&show_local_username=hide&text_platform_name=all&show_platform_name=show&click=Summary&text_compute_cluster_id=&text_os_version=&show_os_version=&text_platform_type=&show_platform_type=&text_submit_id=&text_hostname=&show_hostname=&text_mpi_get_id=&text_mpi_install_compiler_id=&text_mpi_install_configure_id=&text_mpi_install_id=&text_compiler_name=&show_compiler_name=&text_compiler_version=&show_compiler_version=&text_vpath_mode=&show_vpath_mode=&text_endian=&show_endian=&text_bitness=&show_bitness=&text_configure_arguments=&text_exit_value=&show_exit_value=&text_exit_signal=&show_exit_signal=&text_duration=&show_duration=&text_client_serial=&show_client_serial=&text_result_message=&text_result_stdout=&text_result_stderr=&text_environment=&text_description=&lastgo=";
  my $raw_file = "/tmp/raw.txt";

  #
  # Grab the latest data from the existing reporter
  #
  if( !defined($debug) ) {
    $cmd = "curl \"$url\" > $raw_file";
    system($cmd);
  }

  return $raw_file;
}
