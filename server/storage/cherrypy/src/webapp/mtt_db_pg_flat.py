"""Support for PostgreSQL database 'flat'
"""

import os
import mtt_db

import pprint
import psycopg2
import string
import re

#################################################################
# Interface to the database
#################################################################
class Database_pg_flat( mtt_db.Database ):
    _name = '[DB PG Flat]'

    def __init__(self, logger, auth):
        mtt_db.Database.__init__(self, logger, auth)
        self._auth = auth

        self._cursor = None
        self._connection = None


    ##########################################################
    def is_available(self):
        if None == self._auth.get("type") or None == self._auth["type"]:
            self._logger.error(self._name + "Error: Configuration settings missing the \"type\" field")
            return False
        if None == self._auth.get("dbname") or None == self._auth["dbname"]:
            self._logger.error(self._name + "Error: Configuration settings missing the \"dbname\" field")
            return False
        if None == self._auth.get("username") or None == self._auth["username"]:
            self._logger.error(self._name + "Error: Configuration settings missing the \"username\" field")
            return False
        if None == self._auth.get("password") or None == self._auth["password"]:
            self._logger.error(self._name + "Error: Configuration settings missing the \"password\" field")
            return False
        return True

    ##########################################################
    def is_connected(self):
        if self._cursor is not None:
            return True
        else:
            return False

    def connect(self):
        conn_str = ("dbname=" +    str(self._auth["dbname"]) +
                    " user=" +     str(self._auth["username"]) +
                    " password="+ str(self._auth["password"]) +
                    " host="+     str(self._auth["server"]) +
                    " port="+     str(self._auth["port"]) )
        self._connection = psycopg2.connect( conn_str )
        self._cursor = self._connection.cursor()


    def disconnect(self):
        self._cursor.close()
        self._connection.close()

        self._cursor = None
        self._connection = None

    ##########################################################
    def which_table_contains(self, field):
        tables = []
        sql_tables = self._get_sql_table_structure()

        for t in sql_tables:
            for f in sql_tables[t]:
                if field == f:
                    tables.append(t)

        return tables

    def run_summary(self, session=[], data=[]):
        sql, fields = self._build_summary_sql(session, data)
        if None == sql:
            return None

        self._logger.debug(self._name + " (SQL) = \n" + sql)

        self._cursor.execute(sql + ";")
        rows = self._cursor.fetchall()

        if 'options' in data and "count_only" in data['options']:
            fields = ["count"]
            rows = [ [ len(rows) ] ]

        return rows, fields

    def run_detail(self, session=[], data=[]):
        sql, fields = self._build_detail_sql(session, data)
        if None == sql:
            return None

        self._logger.debug(self._name + " (SQL) = \n" + sql)

        self._cursor.execute(sql + ";")
        rows = self._cursor.fetchall()

        if 'options' in data and "count_only" in data['options']:
            fields = ["count"]
            rows = [ [ len(rows) ] ]

        return rows, fields

    ##########################################################
    # Internal functionality
    ##########################################################



    #################################################################
    # The SQL Table structure helps us determine which tables are
    # needed to access the necessary fields that the user requested.
    #################################################################
    def _get_sql_table_structure(self):
        rtn = { "submit": [
                    "hostname",
                    "local_username",
                    "http_username",
                    "mtt_client_version"
                    ],
                "results_fields": [
                    "description",
                    "start_timestamp",
                    "submit_timestamp",
                    "duration",
                    "trial",
                    "test_result",
                    "environment",
                    "result_stdout",
                    "result_stderr",
                    "result_message",
                    "merge_stdout_stderr",
                    "exit_value",
                    "exit_signal"
                    ],
                "mpi_install": [
                    "mpi_install_id",
                    "platform_name",     ###
                    "platform_hardware", ###
                    "platform_type",
                    "os_name",           ###
                    "os_version",
                    "mpi_name",          ###
                    "mpi_version",       ###
                    "compiler_name",     ###
                    "compiler_version",
                    "vpath_mode",
                    "bitness",
                    "endian",
                    "configure_arguments"
                    ],
                "test_build": [
                    "test_build_id",
                    "compiler_name",
                    "compiler_version",
                    "test_suite_name",
                    "test_suite_description"
                    ],
                "test_run": [
                    "test_run_id",
                    "test_name",
                    "test_name_description",
                    "launcher",
                    "resource_mgr",
                    "parameters",
                    "network",
                    "np",
                    "full_command"
                    ]
                }
        return rtn;

    def _check_if_phase(self, phase, allphases=[]):
        if phase in allphases:
            return True
        else:
            return False

    def _preprocess_field(self, field):
        if field == "start_timestamp":
            return "start_timestamp"
        elif field == "end_timestamp":
            return "start_timestamp"
        else:
            return field


    def _get_keys_test_result(self):
        return [ "mpi_install_pass",
                 "mpi_install_fail",
                 "test_build_pass",
                 "test_build_fail",
                 "test_run_pass",
                 "test_run_fail",
                 "test_run_skip",
                 "test_run_timed"]
#                "test_run_perf"]

    def _is_special_key(self, field):
        return field in self._get_keys_test_result()

    def _need_table(self, table_name, all_cols):
        for field, table in all_cols.iteritems():
            if table_name == table:
                return True
        return False

    def _sql_create_outer_select_field(self, field, qualify=""):
        if field == "bitness":
            return """(CASE
          WHEN (bitness = B'000000')  THEN 'unknown'
          WHEN (bitness = B'000001')  THEN '8'
          WHEN (bitness = B'000010')  THEN '16'
          WHEN (bitness = B'000100')  THEN '32'
          WHEN (bitness = B'001000')  THEN '64'
          WHEN (bitness = B'001100')  THEN '32/64'
          WHEN (bitness = B'010000')  THEN '128'
          ELSE 'unknown' END) as bitness
            """
        elif field == "endian":
            return """(CASE
          WHEN (endian = B'01')       THEN 'little'
          WHEN (endian = B'10')       THEN 'big'
          ELSE 'unknown' END) as endian
            """
        elif field == "vpath_mode":
            return """(CASE
          WHEN (vpath_mode = B'01')       THEN 'relative'
          WHEN (vpath_mode = B'10')       THEN 'absolute'
          ELSE 'unknown' END) as vpath_mode
            """
        elif field == "duration":
            return "to_char("+qualify+"duration, 'HH24:MI:SS') as duration"
        else:
            return qualify + field


    def _build_summary_sql(self, session=[], data=[]):
        fields = []
        tables = []
        tablesd = {}
        keys = {}
    
        where = "mpi_install.mpi_install_id > 0 "
    
        sql = None
     
        #################################################################
        # Columns required
        #################################################################
        sql_tables = self._get_sql_table_structure()
    
        #
        # For each of the columns requested, determine which table(s) we need
        #
        self._logger.debug(self._name + " Columns:")
        for col in data['columns']:
            col = self._preprocess_field(col)
        
            tables = self.which_table_contains(col)
            if 0 == len(tables):
                self._logger.error(self._name + " Error: Cound not find the field ("+str(col)+"). Skipping!" )
            elif 1 == len(tables):
                self._logger.debug("%s\t%20s\tTable: %s" %(self._name, col, tables[0]) )
                if col not in tablesd:
                    tablesd[col] = tables[0]
            else:
                if 'install' in data['phases'] and 'mpi_install' in tables:
                    col = "mpi_install."+col
                    tablesd[col] = "mpi_install"
                elif 'test_build' in data['phases'] and 'test_build' in tables:
                    col = "test_build."+col
                    tablesd[col] = "test_build"
                elif 'test_run' in data['phases'] and 'test_run' in tables:
                    col = "test_run."+col
                    tablesd[col] = "test_run"
                elif 'all' in data['phases']:
                    col = "mpi_install."+col
                    tablesd[col] = "mpi_install"
                else:
                    self._logger.debug("%s Multiple matches for (%s). In tables %s" %(self._name, col, ", ".join(tables)))

            fields.append(col)
        

        #
        # For each of the search parameters requested, determine which table(s) we need
        #
        self._logger.debug(self._name + " Search:")
        for col in data['search']:
            col = self._preprocess_field(col)

            tables = self.which_table_contains(col)
            if 0 == len(tables):
                if self._is_special_key(col) == True:
                    keys[col] = data['search'][col]
                else:
                    self._logger.error("%s Error: Cound not find the field (%s). Skipping!" % (self._name, col))
            elif 1 == len(tables):
                self._logger.debug("%s\t%20s\tTable: %s" %(self._name, col, tables[0]))
                if col not in tablesd:
                    tablesd[col] = tables[0]
            else:
                if 'install' in data['phases'] and 'mpi_install' in tables:
                    tablesd[col] = "mpi_install"
                elif 'test_build' in data['phases'] and 'test_build' in tables:
                    tablesd[col] = "test_build"
                elif 'test_run' in data['phases'] and 'test_run' in tables:
                    tablesd[col] = "test_run"
                self._logger.debug("%s Multiple matches for (%s). In tables %s" %(self._name, col, ", ".join(tables)))

            
        #
        # Debug Display the fields and the required tables
        #
        searching = {}
        self._logger.debug(self._name + "-"*40)
        for f in fields:
            self._logger.debug(self._name + " FIELDS : " + f)

        self._logger.debug(self._name + "-"*40)
        for k,v in tablesd.iteritems():
            self._logger.debug("%s REQUIRE: %20s in %s" % (self._name,k,v))

        for k,v in keys.iteritems():
            self._logger.debug("%s KEY: %20s matching '%s'" % (self._name,k,v))

        for k,v in data['search'].iteritems():
            if "start_timestamp" != k and "end_timestamp" != k :
                searching[k] = v
                self._logger.debug("%s S+: %20s matching '%s'" % (self._name,k,v))
        self._logger.debug(self._name + "-"*40)

    
        #################################################################
        # Search Parameters
        #################################################################
        qualify = ""
        if 'install' in data['phases']:
            qualify = "mpi_install."
        elif 'test_build' in data['phases']:
            qualify = "test_build."
        elif 'test_run' in data['phases']:
            qualify = "test_run."
        else:
            qualify = ""

        #
        # Process data range - Done below per case to avoid conflicts
        #

        #
        # Process Compiler
        #
        if "compiler_name" in searching:
            if 'install' in data['phases']:
                qualify = "mpi_install."
            elif 'test_build' in data['phases']:
                qualify = "test_build."
            else:
                qualify = "mpi_install."
            where += "\n\t AND "+qualify+"compiler_name = '"+searching['compiler_name']+"'"
            del searching["compiler_name"]
        if "compiler_version" in searching:
            if 'install' in data['phases']:
                qualify = "mpi_install."
            elif 'test_build' in data['phases']:
                qualify = "test_build."
            else:
                qualify = "mpi_install."
            where += "\n\t AND "+qualify+"compiler_version = '"+searching['compiler_version']+"'"
            del searching["compiler_version"]
        
        #
        # Special Key: pass/fail/skip/timed/perf
        #
        outer_where = ""
        outer_k = ""
        outer_v = ""
        keys_test_result = self._get_keys_test_result()
        for k in keys:
            if k in keys_test_result:
                del searching[k]

                outer_k = ""
                outer_v = ""

                if 'install' in data['phases'] or 'all' in data['phases']:
                    if "mpi_install_pass" == k:
                        outer_k = " _mpi_p "
                    elif "mpi_install_fail" == k:
                        outer_k = " _mpi_f "

                if 'test_build' in data['phases'] or 'all' in data['phases']:
                    if "test_build_pass" == k:
                        outer_k = " _build_p "
                    elif "test_build_fail" == k:
                        outer_k = " _build_f "

                if 'test_run' in data['phases'] or 'all' in data['phases']:
                    if "test_run_pass" == k:
                        outer_k = " _run_p "
                    elif "test_run_fail" == k:
                        outer_k = " _run_f "
                    elif "test_run_skip" == k:
                        outer_k = " _run_s "
                    elif "test_run_timed" == k:
                        outer_k = " _run_t "
                    elif "test_run_perf" == k:
                        outer_k = " _run_p "

                if outer_k != "":
                    outer_where += "\n\t"
                    if outer_where != "\n\t":
                        outer_where += " AND"

                    outer_where += outer_k
                    if keys[k] > 0:
                        outer_where += "> 0"
                    else:
                        outer_where += " <= 0"



        #
        # Process Search fields
        #
        self._logger.debug(self._name + "-"*40)
        for k,v in searching.iteritems():
            self._logger.debug("%s S-: %20s matching '%s'" % (self._name, k,v))
        self._logger.debug(self._name + "-"*40)

        for k,v in searching.iteritems():
            where += "\n\t AND "+ k +" = '"+ v +"'"



        #################################################################
        # Phases
        #################################################################
        group_by_fields = ""
        order_by_fields = ""
        select_inner_fields = ""

        #
        # Outer Select: Primary fields
        #
        countF = 0
        select_base_fields = ""
        qf = ""
        tbl_str = self._get_sql_table_structure()
        for f in fields:
            if f in tbl_str["results_fields"]:
                if qualify == "":
                    qf = "mpi_install."
                else:
                    qf = qualify
            elif f == "compiler_name":
                qf = "mpi_install."
            elif f == "compiler_version":
                qf = "mpi_install."
            else:
                qf = ""

            if countF == 0:
                select_base_fields  += "\n\t" + self._sql_create_outer_select_field(f, qf)
                group_by_fields     += "\n\t" + f
                order_by_fields     += "\n\t" + f
                select_inner_fields += "\n\t" + qf + f
            else:
                select_base_fields  += ",\n\t" + self._sql_create_outer_select_field(f, qf)
                group_by_fields     += ",\n\t" + f
                order_by_fields     += ",\n\t" + f
                select_inner_fields += ",\n\t" + qf + f

            self._logger.debug(self._name + " F : (" + qf + ") [" +f+ "]")
            countF += 1

        select_base_out_fields = select_base_fields
        select_base_out_fields = re.sub(r'mpi_install.', 'results.', select_base_out_fields)
        select_base_out_fields = re.sub(r'test_build.', 'results.', select_base_out_fields)
        select_base_out_fields = re.sub(r'test_run.', 'results.', select_base_out_fields)
        group_by_fields = re.sub(r'mpi_install.', 'results.', group_by_fields)
        group_by_fields = re.sub(r'test_build.', 'results.', group_by_fields)
        order_by_fields = re.sub(r'mpi_install.', 'results.', order_by_fields)
        order_by_fields = re.sub(r'test_build.', 'results.', order_by_fields)


        #
        # Outer Select: aggregation fields
        #
        select_agg_out_fields = ""

        if 'install' in data['phases'] or 'all' in data['phases']:
            fields.append("mpi_install_pass")
            fields.append("mpi_install_fail")

            select_agg_out_fields += ",\n\tSUM(_mpi_p) as mpi_install_pass"
            select_agg_out_fields += ",\n\tSUM(_mpi_f) as mpi_install_fail"

        if 'test_build' in data['phases'] or 'all' in data['phases']:
            fields.append("test_build_pass")
            fields.append("test_build_fail")

            select_agg_out_fields += ",\n\tSUM(_build_p) as test_build_pass"
            select_agg_out_fields += ",\n\tSUM(_build_f) as test_build_fail"

        if 'test_run' in data['phases'] or 'all' in data['phases']:
            fields.append("test_run_pass")
            fields.append("test_run_fail")
            fields.append("test_run_skip")
            fields.append("test_run_timed")

            select_agg_out_fields += ",\n\tSUM(_run_p) as test_run_pass"
            select_agg_out_fields += ",\n\tSUM(_run_f) as test_run_fail"
            select_agg_out_fields += ",\n\tSUM(_run_s) as test_run_skip"
            select_agg_out_fields += ",\n\tSUM(_run_t) as test_run_timed"

        #
        # Outer Select: Build it
        #
        sql  = "SELECT "
        sql += select_base_out_fields
        sql += select_agg_out_fields



        #
        # Inner Select: define aggregation fields and dummy versions
        #
        select_agg_sub_m_fields    = ""
        select_agg_sub_m_fields   += ",\n\t(CASE WHEN mpi_install.test_result = 1 THEN 1 ELSE 0 END) as _mpi_p"
        select_agg_sub_m_fields   += ",\n\t(CASE WHEN mpi_install.test_result = 0 THEN 1 ELSE 0 END) as _mpi_f"
        select_agg_dummy_m_fields  = ""
        select_agg_dummy_m_fields += ",\n\t(0) as _mpi_p"
        select_agg_dummy_m_fields += ",\n\t(0) as _mpi_f"

        select_agg_sub_b_fields    = ""
        select_agg_sub_b_fields   += ",\n\t(CASE WHEN test_build.test_result = 1 THEN 1 ELSE 0 END) as _build_p"
        select_agg_sub_b_fields   += ",\n\t(CASE WHEN test_build.test_result = 0 THEN 1 ELSE 0 END) as _build_f"
        select_agg_dummy_b_fields  = ""
        select_agg_dummy_b_fields += ",\n\t(0) as _build_p"
        select_agg_dummy_b_fields += ",\n\t(0) as _build_f"

        select_agg_sub_r_fields = ""
        select_agg_sub_r_fields += ",\n\t(CASE WHEN test_run.test_result = 1 THEN 1 ELSE 0 END) as _run_p"
        select_agg_sub_r_fields += ",\n\t(CASE WHEN test_run.test_result = 0 THEN 1 ELSE 0 END) as _run_f"
        select_agg_sub_r_fields += ",\n\t(CASE WHEN test_run.test_result = 2 THEN 1 ELSE 0 END) as _run_s"
        select_agg_sub_r_fields += ",\n\t(CASE WHEN test_run.test_result = 3 THEN 1 ELSE 0 END) as _run_t"
        select_agg_dummy_r_fields  = ""
        select_agg_dummy_r_fields += ",\n\t(0) as _run_p"
        select_agg_dummy_r_fields += ",\n\t(0) as _run_f"
        select_agg_dummy_r_fields += ",\n\t(0) as _run_s"
        select_agg_dummy_r_fields += ",\n\t(0) as _run_t"


        #
        # From tables
        #
        select_from_m = "\n\t mpi_install"
        select_from_b = "\n\t test_build"
        select_from_r = "\n\t test_run"
        if self._need_table("submit", tablesd) == True:
            select_from_m += "\n\t\t JOIN submit using (submit_id)"
            select_from_b += "\n\t\t JOIN submit using (submit_id)"
            select_from_r += "\n\t\t JOIN submit using (submit_id)"
        if self._need_table("mpi_install", tablesd) == True:
            select_from_b += "\n\t\t JOIN mpi_install using (mpi_install_id)"
            select_from_r += "\n\t\t JOIN mpi_install using (mpi_install_id)"
        if self._need_table("test_build", tablesd) == True:
            select_from_r += "\n\t\t JOIN test_build using (test_build_id)"

        #
        # Build Basic SQL
        #

        sql += "\nFROM ("

        #
        # All phases - Union the three tables of data
        #
        if 'all' in data['phases'] or len(data['phases']) == 3:
            sql += "\n("

            #
            # MPI Install
            #
            sql += "\n\t\tSELECT \n\t"
            sql += select_inner_fields
            sql += select_agg_sub_m_fields
            sql += select_agg_dummy_b_fields
            sql += select_agg_dummy_r_fields
            sql += "\n\tFROM " + select_from_m
            sql += "\n\tWHERE " + where
            qualify = "mpi_install."
            if "start_timestamp" in data['search']:
                sql += "\n\t AND "+qualify+"start_timestamp >= '"+data['search']['start_timestamp']+"'"
            if "end_timestamp" in data['search']:
                sql += "\n\t AND "+qualify+"start_timestamp <= '"+data['search']['end_timestamp']+"'"

            ###############
            sql += "\n) UNION ALL ("
            ###############

            #
            # Test Build
            #
            sql += "\n\t\tSELECT \n\t"
            sql += select_inner_fields
            sql += select_agg_dummy_m_fields
            sql += select_agg_sub_b_fields
            sql += select_agg_dummy_r_fields
            sql += "\n\tFROM " + select_from_b
            sql += "\n\tWHERE " + where
            qualify = "test_build."
            if "start_timestamp" in data['search']:
                sql += "\n\t AND "+qualify+"start_timestamp >= '"+data['search']['start_timestamp']+"'"
            if "end_timestamp" in data['search']:
                sql += "\n\t AND "+qualify+"start_timestamp <= '"+data['search']['end_timestamp']+"'"

            ###############
            sql += "\n) UNION ALL ("
            ###############

            #
            # Test Run
            #
            sql += "\n\t\tSELECT \n\t"
            sql += select_inner_fields
            sql += select_agg_dummy_m_fields
            sql += select_agg_dummy_b_fields
            sql += select_agg_sub_r_fields
            sql += "\n\tFROM " + select_from_r
            sql += "\n\tWHERE " + where
            qualify = "test_run."
            if "start_timestamp" in data['search']:
                sql += "\n\t AND "+qualify+"start_timestamp >= '"+data['search']['start_timestamp']+"'"
            if "end_timestamp" in data['search']:
                sql += "\n\t AND "+qualify+"start_timestamp <= '"+data['search']['end_timestamp']+"'"

            ###############
            sql += "\n)"
            ###############
        #
        # MPI Install
        #
        elif 'install' in data['phases'] and len(data['phases']) == 1:
            qualify = "mpi_install."
            if "start_timestamp" in data['search']:
                where += "\n\t AND "+qualify+"start_timestamp >= '"+data['search']['start_timestamp']+"'"

            if "end_timestamp" in data['search']:
                where += "\n\t AND "+qualify+"start_timestamp <= '"+data['search']['end_timestamp']+"'"

            sql += "\n\tSELECT "
            sql += select_inner_fields
            sql += select_agg_sub_m_fields

            sql += "\n\tFROM " + select_from_m
            sql += "\n\tWHERE " + where
        #
        # Test Build
        #
        elif 'test_build' in data['phases'] and len(data['phases']) == 1: 
            qualify = "test_build."
            if "start_timestamp" in data['search']:
                where += "\n\t AND "+qualify+"start_timestamp >= '"+data['search']['start_timestamp']+"'"

            if "end_timestamp" in data['search']:
                where += "\n\t AND "+qualify+"start_timestamp <= '"+data['search']['end_timestamp']+"'"

            sql += "\n\tSELECT "
            sql += select_inner_fields
            sql += select_agg_sub_b_fields

            sql += "\n\tFROM " + select_from_b
            sql += "\n\tWHERE " + where
        #
        # Test Run
        #
        elif 'test_run' in data['phases'] and len(data['phases']) == 1:
            qualify = "test_run."
            if "start_timestamp" in data['search']:
                where += "\n\t AND "+qualify+"start_timestamp >= '"+data['search']['start_timestamp']+"'"

            if "end_timestamp" in data['search']:
                where += "\n\t AND "+qualify+"start_timestamp <= '"+data['search']['end_timestamp']+"'"

            sql += "\n\tSELECT "
            sql += select_inner_fields
            sql += select_agg_sub_r_fields

            sql += "\n\tFROM " + select_from_r
            sql += "\n\tWHERE " + where
        #
        # MPI Install, Test Build
        #
        elif 'install' in data['phases'] and 'test_build' in data['phases'] and len(data['phases']) == 2:
            return None
        #
        # Test Build, Test Run
        #
        elif 'test_build' in data['phases'] and 'test_run' in data['phases'] and len(data['phases']) == 2:
            return None
        #
        # MPI Install, Test Run
        #
        elif 'install' in data['phases'] and 'test_run' in data['phases'] and len(data['phases']) == 2:
            return None


        #
        # Return SQL
        #
        sql += "\n     ) as results"

        if outer_where != "":
            sql += "\nWHERE " + outer_where

        sql += "\nGROUP BY " + group_by_fields
        sql += "\nORDER BY " + order_by_fields
        if 'options' in data and "offset" in data['options']:
            sql += "\nOFFSET " + str(data['options']['offset'])
        if 'options' in data and "limit" in data['options']:
            sql += "\nLIMIT " + str(data['options']['limit'])

        final_fields = []
        for f in fields:
            if re.match(r'mpi_install.', f):
                final_fields.append(re.sub(r'mpi_install\.', '', f))
            elif re.match(r'test_build.', f):
                final_fields.append(re.sub(r'test_build\.', '', f))
            elif re.match(r'test_run.', f):
                final_fields.append(re.sub(r'test_run\.', '', f))
            else:
                final_fields.append(f)

        return sql, final_fields


    def _build_detail_sql(self, session=[], data=[]):
        fields = []
        tables = []
        tablesd = {}
        keys = {}

        where = "\n\t" + "mpi_install.mpi_install_id > 0 "

        sql = None


        #################################################################
        # Columns required
        #################################################################
        sql_tables = self._get_sql_table_structure()

        #
        # For each of the columns requested, determine which table(s) we need
        #
        self._logger.debug(self._name + " Columns:")
        for col in data['columns']:
            col = self._preprocess_field(col)

            tables = self.which_table_contains(col)
            if 0 == len(tables):
                self._logger.error(self._name + "Error: Cound not find the field ("+str(col)+"). Skipping!" )
            elif 1 == len(tables):
                self._logger.debug("%s\t%20s\tTable: %s" %(self._name, col, tables[0]) )
                if col not in tablesd:
                    tablesd[col] = tables[0]
            else:
                if 'install' in data['phases'] and 'mpi_install' in tables:
                    col = "mpi_install."+col
                    tablesd[col] = "mpi_install"
                elif 'test_build' in data['phases'] and 'test_build' in tables:
                    col = "test_build."+col
                    tablesd[col] = "test_build"
                elif 'test_run' in data['phases'] and 'test_run' in tables:
                    col = "test_run."+col
                    tablesd[col] = "test_run"
                elif 'all' in data['phases']:
                    col = "mpi_install."+col
                    tablesd[col] = "mpi_install"
                else:
                    self._logger.debug("%s Multiple matches for (%s). In tables %s" %(self._name, col, ", ".join(tables)))

            fields.append(col)


        #
        # For each of the search parameters requested, determine which table(s) we need
        #
        self._logger.debug(self._name + " Search:")
        for col in data['search']:
            col = self._preprocess_field(col)

            tables = self.which_table_contains(col)
            if 0 == len(tables):
                if self._is_special_key(col) == True:
                    keys[col] = data['search'][col]
                else:
                    self._logger.error("%s Error: Cound not find the field (%s). Skipping!" % (self._name, col))
            elif 1 == len(tables):
                self._logger.debug("%s\t%20s\tTable: %s" %(self._name, col, tables[0]))
                if col not in tablesd:
                    tablesd[col] = tables[0]
            else:
                if 'install' in data['phases'] and 'mpi_install' in tables:
                    tablesd[col] = "mpi_install"
                elif 'test_build' in data['phases'] and 'test_build' in tables:
                    tablesd[col] = "test_build"
                elif 'test_run' in data['phases'] and 'test_run' in tables:
                    tablesd[col] = "test_run"
                self._logger.debug("%s Multiple matches for (%s). In tables %s" %(self._name, col, ", ".join(tables)))


        #
        # Debug Display the fields and the required tables
        #
        searching = {}
        self._logger.debug(self._name + "-"*40)
        for f in fields:
            self._logger.debug(self._name + " FIELDS : " + f)

        self._logger.debug(self._name + "-"*40)
        for k,v in tablesd.iteritems():
            self._logger.debug("%s REQUIRE: %20s in %s" % (self._name,k,v))

        for k,v in keys.iteritems():
            self._logger.debug("%s KEY: %20s matching '%s'" % (self._name,k,v))

        for k,v in data['search'].iteritems():
            if "start_timestamp" != k and "end_timestamp" != k :
                searching[k] = v
                self._logger.debug("%s S+: %20s matching '%s'" % (self._name,k,v))
        self._logger.debug(self._name + "-"*40)


        #################################################################
        # Search Parameters
        #################################################################
        qualify = ""
        if 'install' in data['phases']:
            qualify = "mpi_install."
        elif 'test_build' in data['phases']:
            qualify = "test_build."
        elif 'test_run' in data['phases']:
            qualify = "test_run."
        else:
            qualify = ""

        #
        # Process data range - Done below per case to avoid conflicts
        #

        #
        # Process Compiler
        #
        if "compiler_name" in searching:
            if 'install' in data['phases']:
                qualify = "mpi_install."
            elif 'test_build' in data['phases']:
                qualify = "test_build."
            else:
                qualify = "mpi_install."
            where += "\n\t AND "+qualify+"compiler_name = '"+searching['compiler_name']+"'"
            del searching["compiler_name"]
        if "compiler_version" in searching:
            if 'install' in data['phases']:
                qualify = "mpi_install."
            elif 'test_build' in data['phases']:
                qualify = "test_build."
            else:
                qualify = "mpi_install."
            where += "\n\t AND "+qualify+"compiler_version = '"+searching['compiler_version']+"'"
            del searching["compiler_version"]

        #
        # Special Key: pass/fail/skip/timed/perf
        #
        outer_where = ""
        outer_k = ""
        outer_v = ""
        keys_test_result = self._get_keys_test_result()
        for k in keys:
            if k in keys_test_result:
                del searching[k]

                outer_k = ""
                outer_v = ""

                if 'install' in data['phases'] or 'all' in data['phases']:
                    if "mpi_install_pass" == k or "mpi_install_fail" == k:
                        outer_k += " mpi_install.test_result "

                if 'test_build' in data['phases'] or 'all' in data['phases']:
                    if "test_build_pass" == k or "test_build_fail" == k:
                        outer_k += " test_build.test_result "

                if 'test_run' in data['phases'] or 'all' in data['phases']:
                    if "test_run_pass" == k or "test_run_fail" == k:
                        outer_k += " test_run.test_result "
                    elif "test_run_skip" == k or "test_run_timed" == k or "test_run_perf" == k:
                        outer_k += " test_run.test_result "

                if outer_k != "":
                    outer_where += "\n\t"
                    if outer_where != "\n\t":
                        outer_where += " AND"

                    outer_where += outer_k
                    if keys[k] <= 0:
                        outer_where += "!"

                    if re.search(r'_pass', k):
                        outer_where += "= 1"
                    elif re.search(r'fail', k):
                        outer_where += "= 0"
                    elif re.search(r'_skip', k):
                        outer_where += "= 2"
                    elif re.search(r'_timed', k):
                        outer_where += "= 3"
                    elif re.search(r'_perf', k):
                        outer_where += "= 4"
                    else:
                        outer_where += "= 999"

        #
        # Process Search fields
        #
        self._logger.debug(self._name + "-"*40)
        for k,v in searching.iteritems():
            self._logger.debug("%s S-: %20s matching '%s'" % (self._name, k,v))
        self._logger.debug(self._name + "-"*40)

        for k,v in searching.iteritems():
            where += "\n\t AND "+ k +" = '"+ v +"'"


        #################################################################
        # Phases
        #################################################################
        group_by_fields = ""
        order_by_fields = ""
        select_from_table = ""

        #
        # determine qualifier
        #
        if 'install' in data['phases']:
            select_from_table = "mpi_install"
        elif 'test_build' in data['phases']:
            select_from_table = "test_build"
        elif 'test_run' in data['phases']:
            select_from_table = "test_run"
        else:
            return None

        qualify = select_from_table + "."

        select_from_table = "\n\t" + select_from_table

        #
        # Add qualifier to all common "results_fields"
        #
        countF = 0
        qf = ""
        select_base_fields = ""
        tbl_str = self._get_sql_table_structure()
        for f in fields:
            if f in tbl_str["results_fields"]:
                qf = qualify
            elif f == "compiler_name":
                qf = "mpi_install."
            elif f == "compiler_version":
                qf = "mpi_install."
            else:
                qf = ""

            if countF == 0:
                select_base_fields  += "\n\t" + self._sql_create_outer_select_field(f, qf)
                group_by_fields     += "\n\t" + f
                order_by_fields     += "\n\t" + f
            else:
                select_base_fields  += ",\n\t" + self._sql_create_outer_select_field(f, qf)
                group_by_fields     += ",\n\t" + f
                order_by_fields     += ",\n\t" + f

            self._logger.debug(self._name + " F : (" + qf + ") [" +f+ "]")
            countF += 1

        select_base_out_fields = select_base_fields

        #
        # Outer Select: Build it
        #
        sql  = "SELECT "
        sql += select_base_out_fields


        #
        # From
        #
        select_from_other_table = ""
        if self._need_table("submit", tablesd) == True:
            select_from_other_table += "\n\t JOIN submit using (submit_id)"

        if self._need_table("mpi_install", tablesd) == True and not 'install' in data['phases']:
            select_from_other_table += "\n\t JOIN mpi_install using (mpi_install_id)"

        if self._need_table("test_build", tablesd) == True and not 'test_build' in data['phases']:
            select_from_other_table += "\n\t\t JOIN test_build using (test_build_id)"

        sql += "\n"
        sql += " FROM ";
        sql += select_from_table
        sql += select_from_other_table

        #
        # Where
        #
        if "start_timestamp" in data['search']:
            where += "\n\t" + "AND "+qualify+"start_timestamp >= '"+data['search']['start_timestamp']+"'"

        if "end_timestamp" in data['search']:
            where += "\n\t" + "AND "+qualify+"start_timestamp <= '"+data['search']['end_timestamp']+"'"

        sql += "\n"
        sql += " WHERE "
        sql +=  where
        if outer_where != "":
            sql += "\n\t AND "+ outer_where

        #
        # Return SQL
        #
        #sql += " GROUP BY \n\t" + group_by_fields
        #sql += " ORDER BY \n\t" + order_by_fields
        if 'options' in data and "offset" in data['options']:
            sql += "\nOFFSET " + str(data['options']['offset'])
        if 'options' in data and "limit" in data['options']:
            sql += "\nLIMIT " + str(data['options']['limit'])

        final_fields = []
        for f in fields:
            if re.match(qualify, f):
                final_fields.append(re.sub(qualify, '', f))
            else:
                final_fields.append(f)

        return sql, final_fields
