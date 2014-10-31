DB=mttv3
USER=mtt
BACKUP=mtt-backup-2014-10-29_103109.gz

echo "-----------"
echo "Drop/Create the database"
echo "-----------"
dropdb $DB

createdb -U $USER -O $USER $DB "MTT Database (v3)" && \
echo "-----------" && \
echo "Fill DB with the backup data" && \
echo "-----------" && \
date
gunzip -c $BACKUP | psql -q $DB
date 
echo "-----------" && \
echo "All Done!" && \
echo "-----------"
