# MTT Storage (Backend) - CherryPy

Installation instructions for the [CherryPy](http://www.cherrypy.org/) backend option.

```
pip install wheel
pip install cherrypy

# PostgreSQL support (Centos 6)
export PATH=/usr/pgsql-9.3/bin/:$PATH
pip install psycopg2
```

Cancel a SQL query
```
postgres=# select * from pg_stat_activity ;
postgres=# select pg_cancel_backend(31957);
```