#!/usr/bin/env perl

use strict;

my $date_str = `date +\"%F_%H%M%S\"`;
chomp($date_str);
#my $filename = "/scratch/local-mttflat-backup-".$date_str . ".gz";
my $filename = "/scratch/local-mttv3-backup-".$date_str . ".gz";

#my $cmd = "time (pg_dump -U mtt mtt | gzip -9 > ".$filename.")";
#my $cmd = "time (pg_dump -U mtt mttflat -h flux1 | gzip -9 > ".$filename.")";
my $cmd = "time (pg_dump -U mtt mttv3 -h flux1 | gzip -9 > ".$filename.")";


print "-"x50 . "\n";
print "-"x10 . " Backing up the database...\n";
print "-"x50 . "\n";
system("date");
#print $cmd . "\n";
system($cmd);
system("date");

print "\n";
print "-"x50 . "\n";
print "-"x10 . " Now access the file...\n";
print "-"x50 . "\n";
my $size = `du -sh $filename | cut -f 1`;
chomp($size);

print "Filename: $filename\n";
print "Size: ".$size."\n";
system("date");

system("/home/jjhursey/local/bin/pushover-notice.pl \"MTT Backup available at Flux 1\"");

print "\n";
print "-"x50 . "\n";
print "-"x10 . " Now send to Flux2...\n";
print "-"x50 . "\n";
$cmd = "time (scp ".$filename." 192.168.3.102:/scratch/)";
system($cmd);

system("date");
system("/home/jjhursey/local/bin/pushover-notice.pl \"SCP finished to Flux2\"");

exit 0;
