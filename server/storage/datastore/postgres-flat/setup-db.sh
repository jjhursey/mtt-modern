DB=mttflat
USER=mtt

echo "-----------"
echo "Drop/Create the database"
echo "-----------"
dropdb $DB

createdb -U $USER -O $USER $DB "MTT Database (Flat)" && \
echo "-----------" && \
echo "Base Schemas" && \
echo "-----------" && \
psql $DB -U $USER -f schemas-flat.sql && \
echo "-----------" && \
echo "All Done!" && \
echo "-----------"
