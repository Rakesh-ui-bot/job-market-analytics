-- ============================================================
-- SQL Analytics Queries for Job Market Analytics
-- ============================================================

USE job_market_db;

-- 1. Total Jobs Count
SELECT COUNT(*) AS total_jobs FROM jobs;


-- 2. Jobs by Role (Job Title Distribution)
SELECT 
    job_title,
    COUNT(*) AS job_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs), 2) AS percentage
FROM jobs
GROUP BY job_title
ORDER BY job_count DESC;


-- 3. Jobs by Location
SELECT 
    l.location_name,
    l.country,
    COUNT(j.id) AS job_count
FROM jobs j
JOIN locations l ON j.location_id = l.id
GROUP BY l.location_name, l.country
ORDER BY job_count DESC
LIMIT 15;


-- 4. Jobs by Skill (Top In-Demand Tech Skills)
SELECT 
    s.skill_name,
    COUNT(js.job_id) AS demand_count,
    ROUND(COUNT(js.job_id) * 100.0 / (SELECT COUNT(*) FROM jobs), 2) AS market_penetration_pct
FROM job_skills js
JOIN skills s ON js.skill_id = s.id
GROUP BY s.id, s.skill_name
ORDER BY demand_count DESC
LIMIT 20;


-- 5. Jobs by Experience Level
SELECT 
    experience_level,
    COUNT(*) AS job_count
FROM jobs
GROUP BY experience_level
ORDER BY job_count DESC;


-- 6. Jobs by Remote Work Type
SELECT 
    remote_type,
    COUNT(*) AS job_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs), 2) AS percentage
FROM jobs
GROUP BY remote_type
ORDER BY job_count DESC;


-- 7. Overall Average Salary Metrics (USD Normalized)
SELECT 
    COUNT(*) AS total_jobs_with_salary,
    ROUND(AVG(salary_min), 2) AS avg_salary_min,
    ROUND(AVG(salary_max), 2) AS avg_salary_max,
    ROUND(AVG((salary_min + salary_max) / 2), 2) AS overall_avg_salary,
    ROUND(MIN(salary_min), 2) AS min_recorded_salary,
    ROUND(MAX(salary_max), 2) AS max_recorded_salary
FROM jobs
WHERE salary_currency = 'USD';


-- 8. Salary by Job Role (Sorted by Highest Average Salary)
SELECT 
    job_title,
    COUNT(*) AS job_count,
    ROUND(AVG(salary_min), 2) AS avg_salary_min,
    ROUND(AVG(salary_max), 2) AS avg_salary_max,
    ROUND(AVG((salary_min + salary_max) / 2), 2) AS avg_midpoint_salary
FROM jobs
WHERE salary_currency = 'USD'
GROUP BY job_title
ORDER BY avg_midpoint_salary DESC;


-- 9. Salary by Location
SELECT 
    l.location_name,
    l.country,
    COUNT(j.id) AS job_count,
    ROUND(AVG(j.salary_min), 2) AS avg_salary_min,
    ROUND(AVG(j.salary_max), 2) AS avg_salary_max,
    ROUND(AVG((j.salary_min + j.salary_max) / 2), 2) AS avg_midpoint_salary
FROM jobs j
JOIN locations l ON j.location_id = l.id
WHERE j.salary_currency = 'USD'
GROUP BY l.location_name, l.country
HAVING COUNT(j.id) >= 10
ORDER BY avg_midpoint_salary DESC;
