System Layout
-------------
 flux1: Main DB server
 flux2: Backup DB server used during conversion for main queries

1) Copy the old database from flux1 to flux2
   a) Remove any old DB from flux2
      dropdb mttflat
      dropdb mttv3

   b) Create the db on flux2
      createdb -U mtt -O mtt mttv3 "MTT Database (v3)" -h flux2

   c) Copy the old DB from flux1 to flux2
      // The database is too large to do the following (this will take days)
      pg_dump -C -h flux1 -U mtt mttv3 | psql -h flux2 -U mtt mttv3
      // So use a create-pg-dump.pl script and manually copy the files over
      // This takes only a few hours

2) Redirect the service using flux1 to flux2
   cd mtt-modern/server/storage/cherrypy/conf
   emacs mtt.conf

3) Generate the backup from the MTT server (takes about 4 hours)
   ./create-pg-dump.pl
   // This will backup and send the file to the server (and let you know when it is done)

   a) Move the backup to the /scratch on flux1 (takes about 30 minutes to an hour)
      scp mtt-backup-* flux1:/scratch/

4) Run the restore-db.sh script on flux1 for the mttv3 database
   ssh flux1
   cd /scratch
   cp mtt-modern/server/storage/datastore/postgres-v3/restore-db.sh .
   emacs restore-db.sh
   ./restore-db.sh

5) Setup the mttflat DB on flux1
   cd mtt-modern/server/storage/datastore/postgres-flat
   ./setup-db.sh 

6) Start the conversion process
   cd mtt-modern/server/storage/datastore/postgres-flat/convert-v3-to-flat/
   ./run-convert-all-ranges.sh 
   Started: Sunday, April 12 at 10 am
   4/12 10:14 - start base
   4/12 10:23 - finished base

   4/12 10:23 - start pre 2012
   4/12 15:48 - fin (5:24:57)

   4/12 16:04 - start 1-01-2012 to 6-01-2012
   4/12 18:28 - fin (2:24:07)
   4/12 18:28 - start 6-01-2012 to 1-01-2013
   4/13  0:36 - fin (6:07:24)

   4/13  0:36 - start 1-01-2013 to 4-01-2013
   4/13  1:49 - fin (1:13:31)
   4/13  1:49 - start 4-01-2013 to 8-01-2013
   4/13  2:58 - fin (1:08:47)
   4/13  2:58 - start 8-01-2013 to 1-01-2014
   4/13  4:51 - fin (1:52:17)

   4/13  4:51 - start 1-01-2014 to 4-01-2014
   4/13  6:25 - fin (1:37:17)
   4/13  6:25 - start 4-01-2014 to 8-01-2014
   4/13  7:55 - fin (1:29:35)
   4/13  7:55 - start 8-01-2014 to 1-01-2015
   4/13  9:05 - fin (1:10:15)

   4/13  9:05 - start 1-01-2015 to ---
   4/13 10:05 - fin (00:59:41)

7) Redirect the service using flux2 back to flux1
   cd mtt-modern/server/storage/cherrypy/conf
   emacs mtt.conf

8) (Optional) Clean up flux2 since we don't need that data and prep for next time

9) Take note of the most recent timestamp
   psql -U mtt mttflat -h flux1
mttflat=> select MAX(start_timestamp) from mpi_install;
         max         
---------------------
 2015-04-11 12:31:42
(1 row)


10) ...
