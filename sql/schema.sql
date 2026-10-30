--
-- PostgreSQL database dump
--

\restrict 1r6wJqDV8Y2QAd1YqZH3tKvZpoH6tVGWWH7abKHXEhvzfcMaASc50eH5GGWUu1h

-- Dumped from database version 17.11 (Homebrew)
-- Dumped by pg_dump version 17.11 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: staging; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA staging;


--
-- Name: warehouse; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA warehouse;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: ae_attendances; Type: TABLE; Schema: staging; Owner: -
--

CREATE TABLE staging.ae_attendances (
    period text NOT NULL,
    org_code text NOT NULL,
    parent_org text,
    org_name text,
    ae_attendances_type_1 bigint,
    ae_attendances_type_2 bigint,
    ae_attendances_other_department bigint,
    ae_booked_appointments_type_1 bigint,
    ae_booked_appointments_type_2 bigint,
    ae_booked_appointments_other_department bigint,
    attendances_over_4hrs_type_1 bigint,
    attendances_over_4hrs_type_2 bigint,
    attendances_over_4hrs_other_department bigint,
    over_4hrs_booked_type_1 bigint,
    over_4hrs_booked_type_2 bigint,
    over_4hrs_booked_other_department bigint,
    dta_wait_4_to_12hrs bigint,
    dta_wait_12plus_hrs bigint,
    emergency_admissions_type_1 bigint,
    emergency_admissions_type_2 bigint,
    emergency_admissions_other_department bigint,
    other_emergency_admissions bigint
);


--
-- Name: dim_date; Type: TABLE; Schema: warehouse; Owner: -
--

CREATE TABLE warehouse.dim_date (
    date_key integer NOT NULL,
    reporting_month date NOT NULL,
    year integer NOT NULL,
    month_number integer NOT NULL,
    month_name text NOT NULL
);


--
-- Name: dim_organisation; Type: TABLE; Schema: warehouse; Owner: -
--

CREATE TABLE warehouse.dim_organisation (
    organisation_key bigint NOT NULL,
    org_code text NOT NULL,
    org_name text NOT NULL,
    parent_org text
);


--
-- Name: dim_organisation_organisation_key_seq; Type: SEQUENCE; Schema: warehouse; Owner: -
--

ALTER TABLE warehouse.dim_organisation ALTER COLUMN organisation_key ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME warehouse.dim_organisation_organisation_key_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: fact_ae_monthly; Type: TABLE; Schema: warehouse; Owner: -
--

CREATE TABLE warehouse.fact_ae_monthly (
    date_key integer NOT NULL,
    organisation_key bigint NOT NULL,
    ae_attendances_type_1 bigint,
    ae_attendances_type_2 bigint,
    ae_attendances_other_department bigint,
    ae_booked_appointments_type_1 bigint,
    ae_booked_appointments_type_2 bigint,
    ae_booked_appointments_other_department bigint,
    attendances_over_4hrs_type_1 bigint,
    attendances_over_4hrs_type_2 bigint,
    attendances_over_4hrs_other_department bigint,
    over_4hrs_booked_type_1 bigint,
    over_4hrs_booked_type_2 bigint,
    over_4hrs_booked_other_department bigint,
    dta_wait_4_to_12hrs bigint,
    dta_wait_12plus_hrs bigint,
    emergency_admissions_type_1 bigint,
    emergency_admissions_type_2 bigint,
    emergency_admissions_other_department bigint,
    other_emergency_admissions bigint
);


--
-- Name: ae_attendances pk_ae_attendances; Type: CONSTRAINT; Schema: staging; Owner: -
--

ALTER TABLE ONLY staging.ae_attendances
    ADD CONSTRAINT pk_ae_attendances PRIMARY KEY (period, org_code);


--
-- Name: dim_date dim_date_pkey; Type: CONSTRAINT; Schema: warehouse; Owner: -
--

ALTER TABLE ONLY warehouse.dim_date
    ADD CONSTRAINT dim_date_pkey PRIMARY KEY (date_key);


--
-- Name: dim_date dim_date_reporting_month_key; Type: CONSTRAINT; Schema: warehouse; Owner: -
--

ALTER TABLE ONLY warehouse.dim_date
    ADD CONSTRAINT dim_date_reporting_month_key UNIQUE (reporting_month);


--
-- Name: dim_organisation dim_organisation_org_code_key; Type: CONSTRAINT; Schema: warehouse; Owner: -
--

ALTER TABLE ONLY warehouse.dim_organisation
    ADD CONSTRAINT dim_organisation_org_code_key UNIQUE (org_code);


--
-- Name: dim_organisation dim_organisation_pkey; Type: CONSTRAINT; Schema: warehouse; Owner: -
--

ALTER TABLE ONLY warehouse.dim_organisation
    ADD CONSTRAINT dim_organisation_pkey PRIMARY KEY (organisation_key);


--
-- Name: fact_ae_monthly pk_fact_ae_monthly; Type: CONSTRAINT; Schema: warehouse; Owner: -
--

ALTER TABLE ONLY warehouse.fact_ae_monthly
    ADD CONSTRAINT pk_fact_ae_monthly PRIMARY KEY (date_key, organisation_key);


--
-- Name: fact_ae_monthly fk_fact_date; Type: FK CONSTRAINT; Schema: warehouse; Owner: -
--

ALTER TABLE ONLY warehouse.fact_ae_monthly
    ADD CONSTRAINT fk_fact_date FOREIGN KEY (date_key) REFERENCES warehouse.dim_date(date_key);


--
-- Name: fact_ae_monthly fk_fact_organisation; Type: FK CONSTRAINT; Schema: warehouse; Owner: -
--

ALTER TABLE ONLY warehouse.fact_ae_monthly
    ADD CONSTRAINT fk_fact_organisation FOREIGN KEY (organisation_key) REFERENCES warehouse.dim_organisation(organisation_key);


--
-- PostgreSQL database dump complete
--

\unrestrict 1r6wJqDV8Y2QAd1YqZH3tKvZpoH6tVGWWH7abKHXEhvzfcMaASc50eH5GGWUu1h

