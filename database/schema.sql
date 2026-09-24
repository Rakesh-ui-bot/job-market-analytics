-- ============================================================
-- Job Market Analytics & Skill Demand Analyzer - MySQL Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS job_market_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE job_market_db;

-- 1. Companies Table
CREATE TABLE IF NOT EXISTS companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    industry VARCHAR(100) DEFAULT 'Information Technology',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Locations Table
CREATE TABLE IF NOT EXISTS locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location_name VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_location_country (location_name, country)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Jobs Table
CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id VARCHAR(50) NOT NULL UNIQUE,
    job_title VARCHAR(150) NOT NULL,
    raw_job_title VARCHAR(255),
    seniority_level VARCHAR(50) DEFAULT 'Mid-level',
    company_id INT NOT NULL,
    location_id INT NOT NULL,
    employment_type VARCHAR(50) DEFAULT 'Full-time',
    experience_level VARCHAR(50) DEFAULT 'Mid-level',
    remote_type VARCHAR(50) DEFAULT 'On-site',
    salary_min DECIMAL(12, 2),
    salary_max DECIMAL(12, 2),
    salary_currency VARCHAR(10) DEFAULT 'USD',
    salary_is_imputed BOOLEAN DEFAULT FALSE,
    description TEXT,
    education VARCHAR(100) DEFAULT 'Unspecified',
    posting_date DATE NOT NULL,
    is_synthetic BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE CASCADE,
    INDEX idx_job_title (job_title),
    INDEX idx_posting_date (posting_date),
    INDEX idx_experience_level (experience_level),
    INDEX idx_remote_type (remote_type),
    INDEX idx_salary_min (salary_min),
    INDEX idx_salary_max (salary_max)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Skills Table
CREATE TABLE IF NOT EXISTS skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) DEFAULT 'Technical',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Job-Skills Mapping Table
CREATE TABLE IF NOT EXISTS job_skills (
    job_id INT NOT NULL,
    skill_id INT NOT NULL,
    source VARCHAR(50) DEFAULT 'required_skills',
    is_normalized BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (job_id, skill_id),
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    INDEX idx_skill_id (skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
