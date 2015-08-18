DB=mttflat
USER=mtt
SERVER=flux1

echo "-----------"
echo "Drop/Create the database"
echo "-----------"
dropdb -h $SERVER $DB

createdb -U $USER -O $USER $DB "MTT Database (Flat)" -h $SERVER && \
echo "-----------" && \
echo "Base Schemas" && \
echo "-----------" && \
psql $DB -U $USER -h $SERVER -f schemas-flat.sql && \
psql $DB -U $USER -h $SERVER -f schemas-index.sql && \
echo "-----------" && \
echo "All Done!" && \
echo "-----------"
#pushover-notice.pl "Created" $DB "on" $SERVER
