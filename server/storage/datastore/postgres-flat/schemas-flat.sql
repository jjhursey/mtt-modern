--
-- Submit Table
--
\echo "Inserting submit table"
DROP TABLE IF EXISTS submit CASCADE;
CREATE TABLE submit (
    submit_id           serial,

    -- Tmp while converting from old data
    old_submit_id       int DEFAULT -999,

    -- Current Max: 95 chars
    hostname            varchar(128) NOT NULL DEFAULT 'bogus',
    -- Current Max: 8 chars
    local_username      varchar(16)  NOT NULL DEFAULT 'bogus',
    -- Current Max: 8 chars
    http_username       varchar(16)  NOT NULL DEFAULT 'bogus',
    -- Current Max: 8 chars
    mtt_client_version  varchar(16)  NOT NULL DEFAULT '',

    PRIMARY KEY (submit_id)
);

-- An invlid row in case we need it
INSERT INTO submit VALUES ('0', DEFAULT, 'undef', 'undef', 'undef', 'undef');

DROP INDEX IF EXISTS idx_submit_old_id;
CREATE INDEX idx_submit_old_id on submit(old_submit_id);

--
-- Collect 'results' data into a table for easy updating
-- Note: Never select on this table, it give missleading results.
--  It will count all the tuples of its children even though it 
--  doesn't contain any tuples. I guess this is a quick way to 
--  get the total number of results in the database.
--
\echo "Inserting results_fields table"
DROP TABLE IF EXISTS results_fields CASCADE;
CREATE TABLE results_fields (
    description         text DEFAULT 'bogus',

    start_timestamp     timestamp without time zone NOT NULL DEFAULT now() - interval '24 hours',
    submit_timestamp    timestamp without time zone NOT NULL DEFAULT now(),
    duration            interval NOT NULL DEFAULT '-38 seconds',

    -- flag data submitted by experimental MTT runs
    trial               boolean DEFAULT 'f',

    -- result value: 0=fail, 1=pass, 2=skipped, 3=timed out
    test_result         smallint NOT NULL DEFAULT '-38',

    environment         text DEFAULT 'bogus',
    result_stdout       text NOT NULL DEFAULT '', 
    result_stderr       text NOT NULL DEFAULT '',
    result_message      text DEFAULT 'bogus',
    merge_stdout_stderr boolean NOT NULL DEFAULT 't',

    -- set if process exited
    exit_value          integer NOT NULL DEFAULT '-38',

    -- set if process was signaled
    exit_signal         integer NOT NULL DEFAULT '-38'
);

--
-- MPI Install Table
--
\echo "Inserting mpi_install table"
DROP TABLE IF EXISTS mpi_install CASCADE;
CREATE TABLE mpi_install (
    mpi_install_id      serial,

    -- Tmp while converting from old data
    old_mpi_install_id       int DEFAULT -999,

    -- -----------------------------
    -- Parent Reference
    -- -----------------------------
    submit_id           integer NOT NULL DEFAULT '-38',

    -- -----------------------------
    -- Compute Cluster
    -- -----------------------------
    -- Current Max: 42 chars
    platform_name       varchar(128) NOT NULL DEFAULT 'bogus',
    -- Current Max: 6 chars
    platform_hardware   varchar(128) NOT NULL DEFAULT 'bogus',
    -- Current Max: 54 chars
    platform_type       varchar(128) NOT NULL DEFAULT 'bogus',
    -- Current Max: 5 chars
    os_name             varchar(128) NOT NULL DEFAULT 'bogus',
    -- Current Max: 43 chars
    os_version          varchar(128) NOT NULL DEFAULT 'bogus',

    -- -------------------------
    -- MPI Get
    -- -------------------------
    -- Current Max: 21 chars
    mpi_name    varchar(64) NOT NULL DEFAULT 'bogus',
    -- Current Max: 24 chars
    mpi_version varchar(128) NOT NULL DEFAULT 'bogus',

    -- -------------------------
    -- Compiler
    -- -------------------------
    -- Current Max: 9 chars
    compiler_name    varchar(64) NOT NULL DEFAULT 'bogus',
    -- Current Max: 35 chars
    compiler_version varchar(64) NOT NULL DEFAULT 'bogus',

    -- -------------------------
    -- MPI Configure
    -- -------------------------
    -- http://www.postgresql.org/docs/8.2/interactive/datatype-bit.html
    -- 00 = none
    -- 01 = relative
    -- 10 = absolute
    vpath_mode          bit(2)  NOT NULL DEFAULT B'00',
    -- 000000 = unknown
    -- 000001 = 8
    -- 000010 = 16
    -- 000100 = 32
    -- 001000 = 64
    -- 010000 = 128
    bitness             bit(6) NOT NULL DEFAULT B'000000',
    -- 00 = unknown
    -- 01 = little
    -- 10 = big
    -- 11 = both (Mac OS X Universal Binaries)
    endian              bit(2) NOT NULL DEFAULT B'00',

    -- Current Max: 1319 chars
    configure_arguments text NOT NULL DEFAULT '', 

    -- ********** --

    PRIMARY KEY (mpi_install_id),

    FOREIGN KEY (submit_id) REFERENCES submit(submit_id)
) INHERITS(results_fields);

-- An invlid row in case we need it
INSERT INTO mpi_install 
   (mpi_install_id,
    submit_id,
    description,
    start_timestamp,
    submit_timestamp
   ) VALUES (
    '0',
    '0',
    'Detached MPI Install (Bogus)',
    TIMESTAMP '2006-11-01',
    TIMESTAMP '2006-11-01'
   );

DROP INDEX IF EXISTS idx_mpi_install_old_id;
CREATE INDEX idx_mpi_install_old_id on mpi_install(old_mpi_install_id);


--
-- Test Build Table
--
\echo "Inserting test_build table"
DROP TABLE IF EXISTS test_build CASCADE;
CREATE TABLE test_build (
    test_build_id       serial,

    -- Tmp while converting from old data
    old_test_build_id       int DEFAULT -999,

    -- -----------------------------
    -- Parent Reference
    -- -----------------------------
    submit_id           integer NOT NULL DEFAULT '-38',
    mpi_install_id      integer NOT NULL DEFAULT '-38',

    -- -----------------------------
    -- Compute Cluster - Access from mpi_install_id
    -- -----------------------------

    -- -------------------------
    -- Compiler (Could be different than MPI Install, so duplicate
    -- -------------------------
    -- Current Max: 9 chars
    compiler_name    varchar(64) NOT NULL DEFAULT 'bogus',
    -- Current Max: 35 chars
    compiler_version varchar(64) NOT NULL DEFAULT 'bogus',

    -- -------------------------
    -- Test Suite
    -- -------------------------
    -- Current Max: 15 chars
    test_suite_name          varchar(32) NOT NULL DEFAULT 'bogus',
    test_suite_description   text DEFAULT '',


    -- ********** --

    PRIMARY KEY (test_build_id),

    FOREIGN KEY (submit_id) REFERENCES submit(submit_id),
    FOREIGN KEY (mpi_install_id) REFERENCES mpi_install(mpi_install_id)
) INHERITS(results_fields);

-- An invlid row in case we need it
INSERT INTO test_build 
   (test_build_id,
    mpi_install_id,
    submit_id,
    description,
    start_timestamp,
    submit_timestamp
   ) VALUES (
    '0',
    '0',
    '0',
    'Detached Test Build (Bogus)',
    TIMESTAMP '2006-11-01',
    TIMESTAMP '2006-11-01'
   );

DROP INDEX IF EXISTS idx_test_build_old_id;
CREATE INDEX idx_test_build_old_id on test_build(old_test_build_id);

--
-- Test Run Table
--
\echo "Inserting test_run table"
DROP TABLE IF EXISTS test_run CASCADE;
CREATE TABLE test_run (
    test_run_id         serial,

    -- Tmp while converting from old data
    old_test_run_id       int DEFAULT -999,

    -- -----------------------------
    -- Parent Reference
    -- -----------------------------
    submit_id           integer NOT NULL DEFAULT '-38',
    mpi_install_id      integer NOT NULL DEFAULT '-38',
    test_build_id       integer NOT NULL DEFAULT '-38',

    -- -----------------------------
    -- Compute Cluster - Access from mpi_install_id
    -- -----------------------------

    -- -----------------------------
    -- Test Suite - Referenced by the test_build_id
    -- -----------------------------

    -- -----------------------------
    -- Individual test
    -- -----------------------------
    -- Current Max: 39  chars
    test_name                varchar(64) NOT NULL DEFAULT 'bogus',
    test_name_description    text DEFAULT '',

    -- -----------------------------
    -- Test Run Setup
    -- -----------------------------
    -- mpirun, mpiexec, yod, ... 128 chars to handle script names
    launcher            varchar(128) DEFAULT '',
    -- Resource Manager [RSH, SLURM, PBS, ...]
    resource_mgr        varchar(32) DEFAULT '',
    -- Runtime Parameters [MCA, SSI, ...]
    parameters          text DEFAULT '',
    -- Network
    network             varchar(32) DEFAULT '',

    np                  smallint NOT NULL DEFAULT '-38',
    full_command        text NOT NULL DEFAULT 'bogus',

    -- ********** --

    PRIMARY KEY (test_run_id),

    FOREIGN KEY (submit_id) REFERENCES submit(submit_id),
    FOREIGN KEY (mpi_install_id) REFERENCES mpi_install(mpi_install_id),
    FOREIGN KEY (test_build_id) REFERENCES test_build(test_build_id)
) INHERITS(results_fields);

-- An invlid row in case we need it
INSERT INTO test_run 
   (test_run_id,
    test_build_id,
    mpi_install_id,
    submit_id,
    description,
    start_timestamp,
    submit_timestamp
   ) VALUES (
    '0',
    '0',
    '0',
    '0',
    'Detached Test Run (Bogus)',
    TIMESTAMP '2006-11-01',
    TIMESTAMP '2006-11-01'
   );
