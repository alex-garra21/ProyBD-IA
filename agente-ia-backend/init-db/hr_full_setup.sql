-- hr_full_setup.sql
-- Este script crea todas las tablas del esquema HR y las puebla con datos.

-- Deshabilitar la verificación de FK temporalmente para facilitar el DROP
SET session_replication_role = replica;

-- 1. ELIMINAR TABLAS (DROP TABLES)
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS departments CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;
DROP TABLE IF EXISTS locations CASCADE;
DROP TABLE IF EXISTS countries CASCADE;
DROP TABLE IF EXISTS regions CASCADE;


-- 2. CREAR TABLAS (CREATE TABLES)
CREATE TABLE regions (
    region_id INTEGER NOT NULL,
    region_name VARCHAR(25) NOT NULL UNIQUE,
    CONSTRAINT region_id_pk PRIMARY KEY (region_id)
);

CREATE TABLE countries (
    country_id VARCHAR(2) NOT NULL,
    country_name VARCHAR(40) NOT NULL,
    region_id INTEGER NOT NULL,
    CONSTRAINT country_id_pk PRIMARY KEY (country_id),
    CONSTRAINT countr_reg_fk FOREIGN KEY (region_id) REFERENCES regions (region_id)
);

CREATE TABLE locations (
    location_id INTEGER NOT NULL,
    street_address VARCHAR(40),
    postal_code VARCHAR(12),
    city VARCHAR(30) NOT NULL,
    state_province VARCHAR(25),
    country_id VARCHAR(2) NOT NULL,
    CONSTRAINT loc_id_pk PRIMARY KEY (location_id),
    CONSTRAINT loc_c_id_fk FOREIGN KEY (country_id) REFERENCES countries (country_id)
);

CREATE TABLE jobs (
    job_id VARCHAR(10) NOT NULL,
    job_title VARCHAR(35) NOT NULL,
    min_salary NUMERIC(6, 0),
    max_salary NUMERIC(6, 0),
    CONSTRAINT job_id_pk PRIMARY KEY (job_id)
);

CREATE TABLE departments (
    department_id INTEGER NOT NULL,
    department_name VARCHAR(30) NOT NULL UNIQUE,
    manager_id INTEGER,
    location_id INTEGER,
    CONSTRAINT dept_id_pk PRIMARY KEY (department_id),
    CONSTRAINT dept_loc_fk FOREIGN KEY (location_id) REFERENCES locations (location_id)
);

CREATE TABLE employees (
    employee_id INTEGER NOT NULL,
    first_name VARCHAR(20),
    last_name VARCHAR(25) NOT NULL,
    email VARCHAR(25) NOT NULL UNIQUE,
    phone_number VARCHAR(20),
    hire_date DATE NOT NULL,
    job_id VARCHAR(10) NOT NULL,
    salary NUMERIC(8, 2) NOT NULL,
    commission_pct NUMERIC(2, 2),
    manager_id INTEGER,
    department_id INTEGER,
    
    CONSTRAINT emp_id_pk PRIMARY KEY (employee_id),
    CONSTRAINT emp_dept_fk FOREIGN KEY (department_id) REFERENCES departments (department_id),
    CONSTRAINT emp_job_fk FOREIGN KEY (job_id) REFERENCES jobs (job_id),
    CONSTRAINT emp_manager_fk FOREIGN KEY (manager_id) REFERENCES employees (employee_id)
);


-- 3. INSERCIÓN DE DATOS (INSERT INTO)
-- REGIONS
INSERT INTO regions (region_id, region_name) VALUES (1, 'Europe');
INSERT INTO regions (region_id, region_name) VALUES (2, 'Americas');
INSERT INTO regions (region_id, region_name) VALUES (3, 'Asia');
INSERT INTO regions (region_id, region_name) VALUES (4, 'Middle East and Africa');

-- COUNTRIES
INSERT INTO countries (country_id, country_name, region_id) VALUES ('US', 'United States of America', 2);
INSERT INTO countries (country_id, country_name, region_id) VALUES ('CA', 'Canada', 2);
INSERT INTO countries (country_id, country_name, region_id) VALUES ('UK', 'United Kingdom', 1);
INSERT INTO countries (country_id, country_name, region_id) VALUES ('DE', 'Germany', 1);
INSERT INTO countries (country_id, country_name, region_id) VALUES ('IT', 'Italy', 1);
INSERT INTO countries (country_id, country_name, region_id) VALUES ('JP', 'Japan', 3);

-- LOCATIONS
INSERT INTO locations (location_id, street_address, postal_code, city, state_province, country_id) VALUES (1000, '1297 Via Cola di Rie', '00989', 'Rome', NULL, 'IT');
INSERT INTO locations (location_id, street_address, postal_code, city, state_province, country_id) VALUES (1700, '20045 Loxahatchee', '98199', 'Seattle', 'Washington', 'US');
INSERT INTO locations (location_id, street_address, postal_code, city, state_province, country_id) VALUES (1800, '460 Bloor St.', NULL, 'Toronto', 'Ontario', 'CA');
INSERT INTO locations (location_id, street_address, postal_code, city, state_province, country_id) VALUES (2500, 'Schwanthalerstrasse 7031', '98199', 'Munich', 'Bavaria', 'DE');

-- JOBS
INSERT INTO jobs (job_id, job_title, min_salary, max_salary) VALUES ('AD_PRES', 'President', 20000, 40000);
INSERT INTO jobs (job_id, job_title, min_salary, max_salary) VALUES ('IT_PROG', 'Programmer', 4000, 10000);
INSERT INTO jobs (job_id, job_title, min_salary, max_salary) VALUES ('SA_REP', 'Sales Representative', 6000, 12000);
INSERT INTO jobs (job_id, job_title, min_salary, max_salary) VALUES ('HR_REP', 'HR Representative', 5000, 9000);
INSERT INTO jobs (job_id, job_title, min_salary, max_salary) VALUES ('MK_MAN', 'Marketing Manager', 9000, 15000);
INSERT INTO jobs (job_id, job_title, min_salary, max_salary) VALUES ('AD_VP', 'Admin Vice President', 15000, 30000);

-- DEPARTMENTS
INSERT INTO departments (department_id, department_name, manager_id, location_id) VALUES (10, 'Administration', 100, 1700); 
INSERT INTO departments (department_id, department_name, manager_id, location_id) VALUES (20, 'Marketing', 200, 1800); 
INSERT INTO departments (department_id, department_name, manager_id, location_id) VALUES (50, 'Shipping', 201, 1700); 
INSERT INTO departments (department_id, department_name, manager_id, location_id) VALUES (80, 'Sales', 202, 2500); 

-- EMPLOYEES
-- Nota: Los manager_id se configuran aquí y deben existir (ej. 100 y 200)
INSERT INTO employees (employee_id, first_name, last_name, email, phone_number, hire_date, job_id, salary, commission_pct, manager_id, department_id) VALUES (100, 'Steven', 'King', 'SKING', '515.123.4567', '2003-06-17', 'AD_PRES', 24000.00, NULL, NULL, 10);
INSERT INTO employees (employee_id, first_name, last_name, email, phone_number, hire_date, job_id, salary, commission_pct, manager_id, department_id) VALUES (200, 'Michael', 'Hartstein', 'MHARTSTE', '515.123.5555', '2004-02-17', 'MK_MAN', 13000.00, NULL, 100, 20); 
INSERT INTO employees (employee_id, first_name, last_name, email, phone_number, hire_date, job_id, salary, commission_pct, manager_id, department_id) VALUES (201, 'Susan', 'Mavris', 'SMAVRIS', '515.123.7777', '2005-06-07', 'HR_REP', 6500.00, NULL, 100, 50); 
INSERT INTO employees (employee_id, first_name, last_name, email, phone_number, hire_date, job_id, salary, commission_pct, manager_id, department_id) VALUES (202, 'Pat', 'Fay', 'PFAY', '515.123.6666', '2005-08-17', 'MK_MAN', 6000.00, NULL, 200, 20); 
INSERT INTO employees (employee_id, first_name, last_name, email, phone_number, hire_date, job_id, salary, commission_pct, manager_id, department_id) VALUES (203, 'Hermann', 'Baer', 'HBAER', '515.123.8888', '2002-06-07', 'SA_REP', 10000.00, 0.15, 100, 80); 
INSERT INTO employees (employee_id, first_name, last_name, email, phone_number, hire_date, job_id, salary, commission_pct, manager_id, department_id) VALUES (204, 'Shelley', 'Higgins', 'SHIGGINS', '515.123.8080', '2002-06-07', 'IT_PROG', 12000.00, NULL, 200, 20); 
INSERT INTO employees (employee_id, first_name, last_name, email, phone_number, hire_date, job_id, salary, commission_pct, manager_id, department_id) VALUES (205, 'William', 'Gietz', 'WGIETZ', '515.123.8181', '2002-06-07', 'IT_PROG', 8300.00, NULL, 200, 20); 

-- Habilitar la verificación de FK de nuevo
SET session_replication_role = default;