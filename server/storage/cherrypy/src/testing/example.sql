--EXPLAIN
SELECT
    http_username,
    platform_name,
    platform_hardware,
    mpi_name,
    mpi_version,
    SUM(_mpi_p) as mpi_install_pass,
    SUM(_mpi_f) as mpi_install_fail,
    SUM(_build_p) as test_build_pass,
    SUM(_build_f) as test_build_fail,
    SUM(_run_p) as test_run_pass,
    SUM(_run_f) as test_run_fail,
    SUM(_run_s) as test_run_skip,
    SUM(_run_t) as test_run_timed
FROM 
(
    (
        SELECT
            http_username,
            platform_name,
            platform_hardware,
            os_name,
            mpi_name,
            mpi_version,
            (CASE WHEN mpi_install.test_result = 1 THEN 1 ELSE 0 END) as _mpi_p,
            (CASE WHEN mpi_install.test_result = 0 THEN 1 ELSE 0 END) as _mpi_f,
            (0)  as _build_p,
            (0)  as _build_f,
            (0)  as _run_p,
            (0)  as _run_f,
            (0)  as _run_s,
            (0)  as _run_t
        FROM submit JOIN mpi_install using (submit_id)
        WHERE 
             start_timestamp >= '2014-10-15 02:00:00' AND 
             start_timestamp <= '2014-10-15 22:00:00' AND
             (trial = 'f')
        )
        UNION ALL
        (
        SELECT
            http_username,
            platform_name,
            platform_hardware,
            os_name,
            mpi_name,
            mpi_version,
            (0)  as _mpi_p,
            (0)  as _mpi_f,
            (CASE WHEN test_build.test_result = 1 THEN 1 ELSE 0 END) as _build_p,
            (CASE WHEN test_build.test_result = 0 THEN 1 ELSE 0 END) as _build_f,
            (0)  as _run_p,
            (0)  as _run_f,
            (0)  as _run_s,
            (0)  as _run_t
        FROM submit JOIN test_build  using (submit_id) 
                    JOIN mpi_install using (mpi_install_id)
        WHERE 
            test_build.start_timestamp >= '2014-10-15 02:00:00' AND 
            test_build.start_timestamp <= '2014-10-15 22:00:00' AND
            (test_build.trial = 'f')
        )
        UNION ALL
        (
        SELECT
            http_username,
            platform_name,
            platform_hardware,
            os_name,
            mpi_name,
            mpi_version,
             (0)  as _mpi_p,
             (0)  as _mpi_f,
             (0)  as _build_p,
             (0)  as _build_f,
             (CASE WHEN test_run.test_result = 1 THEN 1 ELSE 0 END) as _run_p,
             (CASE WHEN test_run.test_result = 0 THEN 1 ELSE 0 END) as _run_f,
             (CASE WHEN test_run.test_result = 2 THEN 1 ELSE 0 END) as _run_s,
             (CASE WHEN test_run.test_result = 3 THEN 1 ELSE 0 END) as _run_t
        FROM submit JOIN test_run using (submit_id)
                    JOIN mpi_install using (mpi_install_id)
        WHERE 
             test_run.start_timestamp >= '2014-10-15 02:00:00' AND 
             test_run.start_timestamp <= '2014-10-15 22:00:00' AND
             (test_run.trial = 'f')
        )
   ) as summary
GROUP BY 
      http_username,
      platform_name,
      platform_hardware,
      os_name,
      mpi_name,
      mpi_version
ORDER BY 
      http_username,
      platform_name,
      platform_hardware,
      os_name,
      mpi_name,
      mpi_version

OFFSET 0;

--
-- This is a different technique, but will only return results
-- in the date range respective to the mpi_install submission
-- not the test_build or test_run
--
--EXPLAIN
SELECT
    http_username,
    platform_name,
    platform_hardware,
    mpi_name,
    mpi_version,
    SUM(_mpi_p) as mpi_install_pass,
    SUM(_mpi_f) as mpi_install_fail,
    SUM(_build_p) as test_build_pass,
    SUM(_build_f) as test_build_fail,
    SUM(_run_p) as test_run_pass,
    SUM(_run_f) as test_run_fail,
    SUM(_run_s) as test_run_skip,
    SUM(_run_t) as test_run_timed
FROM 
(
    (
        SELECT
            http_username,
            platform_name,
            platform_hardware,
            os_name,
            mpi_name,
            mpi_version,
            (CASE WHEN mpi_install.test_result = 1 THEN 1 ELSE 0 END) as _mpi_p,
            (CASE WHEN mpi_install.test_result = 0 THEN 1 ELSE 0 END) as _mpi_f,
            (0)  as _build_p,
            (0)  as _build_f,
            (0)  as _run_p,
            (0)  as _run_f,
            (0)  as _run_s,
            (0)  as _run_t
        FROM submit JOIN mpi_install using (submit_id)
        WHERE 
             start_timestamp >= '2014-10-15 02:00:00' AND 
             start_timestamp <= '2014-10-15 22:00:00' AND
             (trial = 'f')
        )
        UNION ALL
        (
        SELECT
            http_username,
            platform_name,
            platform_hardware,
            os_name,
            mpi_name,
            mpi_version,
            (0)  as _mpi_p,
            (0)  as _mpi_f,
            (CASE WHEN test_build.test_result = 1 THEN 1 ELSE 0 END) as _build_p,
            (CASE WHEN test_build.test_result = 0 THEN 1 ELSE 0 END) as _build_f,
            (0)  as _run_p,
            (0)  as _run_f,
            (0)  as _run_s,
            (0)  as _run_t
        FROM submit JOIN test_build  using (submit_id) 
                    JOIN mpi_install using (mpi_install_id)
        WHERE 
            test_build.start_timestamp >= '2014-10-15 02:00:00' AND 
            test_build.start_timestamp <= '2014-10-15 22:00:00' AND
            (test_build.trial = 'f') AND
            test_build.mpi_install_id = ANY(
               SELECT mpi_install_id
               FROM submit JOIN mpi_install using (submit_id)
               WHERE 
                  start_timestamp >= '2014-10-15 02:00:00' AND 
                  start_timestamp <= '2014-10-15 22:00:00' AND
                  (trial = 'f')
               )
        )
        UNION ALL
        (
        SELECT
            http_username,
            platform_name,
            platform_hardware,
            os_name,
            mpi_name,
            mpi_version,
             (0)  as _mpi_p,
             (0)  as _mpi_f,
             (0)  as _build_p,
             (0)  as _build_f,
             (CASE WHEN test_run.test_result = 1 THEN 1 ELSE 0 END) as _run_p,
             (CASE WHEN test_run.test_result = 0 THEN 1 ELSE 0 END) as _run_f,
             (CASE WHEN test_run.test_result = 2 THEN 1 ELSE 0 END) as _run_s,
             (CASE WHEN test_run.test_result = 3 THEN 1 ELSE 0 END) as _run_t
        FROM submit JOIN test_run using (submit_id)
                    JOIN mpi_install using (mpi_install_id)
        WHERE 
             test_run.start_timestamp >= '2014-10-15 02:00:00' AND 
             test_run.start_timestamp <= '2014-10-15 22:00:00' AND
             (test_run.trial = 'f') AND
             test_run.mpi_install_id = ANY(
               SELECT mpi_install_id
               FROM submit JOIN mpi_install using (submit_id)
               WHERE 
                  start_timestamp >= '2014-10-15 02:00:00' AND 
                  start_timestamp <= '2014-10-15 22:00:00' AND
                  (trial = 'f')
               )
        )
   ) as summary
GROUP BY 
      http_username,
      platform_name,
      platform_hardware,
      os_name,
      mpi_name,
      mpi_version
ORDER BY 
      http_username,
      platform_name,
      platform_hardware,
      os_name,
      mpi_name,
      mpi_version

OFFSET 0;
