--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: queue_log; Type: TABLE; Schema: public; Owner: kamailio; Tablespace:
--

CREATE TABLE queue_log (
    id integer NOT NULL,
    "time" character varying(26) DEFAULT NULL::character varying,
    callid character varying(32) DEFAULT ''::character varying NOT NULL,
    queuename character varying(32) DEFAULT ''::character varying NOT NULL,
    agent character varying(32) DEFAULT ''::character varying NOT NULL,
    event character varying(32) DEFAULT ''::character varying NOT NULL,
    data1 character varying(100) DEFAULT ''::character varying NOT NULL,
    data2 character varying(100) DEFAULT ''::character varying NOT NULL,
    data3 character varying(100) DEFAULT ''::character varying NOT NULL,
    data4 character varying(100) DEFAULT ''::character varying NOT NULL,
    data5 character varying(100) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE queue_log OWNER TO omnileads;

--
-- Name: queue_log_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE queue_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE queue_log_id_seq OWNER TO omnileads;

--
-- Name: queue_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE queue_log_id_seq OWNED BY queue_log.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY queue_log ALTER COLUMN id SET DEFAULT nextval('queue_log_id_seq'::regclass);


--
-- Name: queue_log_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace:
--

ALTER TABLE ONLY queue_log
    ADD CONSTRAINT queue_log_pkey PRIMARY KEY (id);

--
-- PostgreSQL database dump complete
--
