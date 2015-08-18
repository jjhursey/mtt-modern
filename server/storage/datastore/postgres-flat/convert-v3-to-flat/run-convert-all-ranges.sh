echo ---------------------
echo Base Tables
echo ---------------------
#pushover-notice.pl "Base tables"
#./convert_v3_backup_to_flat.pl -s -m -b

echo ---------------------
echo Pre 2012
echo ---------------------
#pushover-notice.pl "Starting Pre 2012"
#./convert_v3_backup_to_flat.pl -r


echo ---------------------
echo 2012
echo ---------------------
pushover-notice.pl "Starting 2012"
echo 1 to 6
./convert_v3_backup_to_flat.pl -r 1-01-2012 6-01-2012 || (pushover-notice.pl "Convert Failed" ; exit -1)
echo 6 to after 12
./convert_v3_backup_to_flat.pl -r 6-01-2012 1-01-2013 || (pushover-notice.pl "Convert Failed" ; exit -1)

echo ---------------------
echo 2013
echo ---------------------
pushover-notice.pl "Starting 2013"
echo 1 to 4
./convert_v3_backup_to_flat.pl -r 1-01-2013 4-01-2013 || (pushover-notice.pl "Convert Failed" ; exit -1)
echo 4 to 8
./convert_v3_backup_to_flat.pl -r 4-01-2013 8-01-2013 || (pushover-notice.pl "Convert Failed" ; exit -1)
echo 8 to after 12
./convert_v3_backup_to_flat.pl -r 8-01-2013 1-01-2014 || (pushover-notice.pl "Convert Failed" ; exit -1)

echo ---------------------
echo 2014
echo ---------------------
pushover-notice.pl "Starting 2014"
echo 1 to 4
./convert_v3_backup_to_flat.pl -r 1-01-2014 4-01-2014 || (pushover-notice.pl "Convert Failed" ; exit -1)
echo 4 to 8
./convert_v3_backup_to_flat.pl -r 4-01-2014 8-01-2014 || (pushover-notice.pl "Convert Failed" ; exit -1)
echo 8 to after 12
./convert_v3_backup_to_flat.pl -r 8-01-2014 1-01-2015 || (pushover-notice.pl "Convert Failed" ; exit -1)

echo ---------------------
echo 2015
echo ---------------------
pushover-notice.pl "Starting 2015"
echo 1 to 4
./convert_v3_backup_to_flat.pl -r 1-01-2015 || (pushover-notice.pl "Convert Failed" ; exit -1)

echo ---------------------
echo ---------------------
echo ---------------------
pushover-notice.pl "All Convert Finished"
