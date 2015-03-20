DB=mttv3
USER=mtt
SERVER=flux2

#BACKUP=mtt-backup-2014-10-29_103109.gz
BACKUP=mtt-backup-2015-01-16_104327.gz

echo "-----------"
echo "Drop/Create the database"
echo "-----------"
dropdb $DB

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
