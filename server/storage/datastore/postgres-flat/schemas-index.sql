--
-- Submit table
--
DROP INDEX IF EXISTS idx_submit_http_username;
CREATE INDEX idx_submit_http_username on submit (http_username);

--
-- MPI Install
--
DROP INDEX IF EXISTS idx_mpi_install_timestamp;
CREATE INDEX idx_mpi_install_timestamp ON mpi_install (start_timestamp);

DROP INDEX IF EXISTS idx_mpi_install_trial;
CREATE INDEX idx_mpi_install_trial ON mpi_install (trial);

DROP INDEX IF EXISTS idx_mpi_install_test_result;
CREATE INDEX idx_mpi_install_test_result ON mpi_install (test_result);

--
-- Test Build
--
DROP INDEX IF EXISTS idx_test_build_timestamp;
CREATE INDEX idx_test_build_timestamp ON test_build (start_timestamp);

DROP INDEX IF EXISTS idx_test_build_trial;
CREATE INDEX idx_test_build_trial ON test_build (trial);

DROP INDEX IF EXISTS idx_test_build_test_result;
CREATE INDEX idx_test_build_test_result ON test_build (test_result);


--
-- Test Run
--
DROP INDEX IF EXISTS idx_test_run_timestamp;
CREATE INDEX idx_test_run_timestamp ON test_run (start_timestamp);

DROP INDEX IF EXISTS idx_test_run_trial;
CREATE INDEX idx_test_run_trial ON test_run (trial);

DROP INDEX IF EXISTS idx_test_run_test_result;
CREATE INDEX idx_test_run_test_result ON test_run (test_result);
