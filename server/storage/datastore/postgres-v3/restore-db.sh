DB=mttv3
USER=mtt
SERVER=flux1

#BACKUP=mtt-backup-2014-10-29_103109.gz
BACKUP=mtt-backup-2015-04-11_133406.gz

echo "-----------"
echo "Drop/Create the database"
echo "-----------"
dropdb -h $SERVER $DB

createdb -U $USER -O $USER $DB "MTT Database (v3)" -h $SERVER && \
echo "-----------" && \
echo "Fill DB with the backup data" && \
echo "-----------" && \
date
gunzip -c $BACKUP | psql -q $DB
date 
echo "-----------" && \
echo "All Done!" && \
echo "-----------"
pushover-notice.pl "Restore Finished on " $SERVER