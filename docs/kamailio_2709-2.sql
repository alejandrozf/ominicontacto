--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.4
-- Dumped by pg_dump version 9.5.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
-- Name: concat(text, text); Type: FUNCTION; Schema: public; Owner: kamailio
--

CREATE FUNCTION concat(text, text) RETURNS text
    LANGUAGE sql
    AS $_$SELECT $1 || $2;$_$;


ALTER FUNCTION public.concat(text, text) OWNER TO kamailio;

--
-- Name: rand(); Type: FUNCTION; Schema: public; Owner: kamailio
--

CREATE FUNCTION rand() RETURNS double precision
    LANGUAGE sql
    AS $$SELECT random();$$;


ALTER FUNCTION public.rand() OWNER TO kamailio;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: acc; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE acc (
    id integer NOT NULL,
    method character varying(16) DEFAULT ''::character varying NOT NULL,
    from_tag character varying(64) DEFAULT ''::character varying NOT NULL,
    to_tag character varying(64) DEFAULT ''::character varying NOT NULL,
    callid character varying(255) DEFAULT ''::character varying NOT NULL,
    sip_code character varying(3) DEFAULT ''::character varying NOT NULL,
    sip_reason character varying(128) DEFAULT ''::character varying NOT NULL,
    "time" timestamp without time zone NOT NULL
);


ALTER TABLE acc OWNER TO kamailio;

--
-- Name: acc_cdrs; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE acc_cdrs (
    id integer NOT NULL,
    start_time timestamp without time zone DEFAULT '2000-01-01 00:00:00'::timestamp without time zone NOT NULL,
    end_time timestamp without time zone DEFAULT '2000-01-01 00:00:00'::timestamp without time zone NOT NULL,
    duration real DEFAULT 0 NOT NULL
);


ALTER TABLE acc_cdrs OWNER TO kamailio;

--
-- Name: acc_cdrs_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE acc_cdrs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE acc_cdrs_id_seq OWNER TO kamailio;

--
-- Name: acc_cdrs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE acc_cdrs_id_seq OWNED BY acc_cdrs.id;


--
-- Name: acc_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE acc_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE acc_id_seq OWNER TO kamailio;

--
-- Name: acc_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE acc_id_seq OWNED BY acc.id;


--
-- Name: active_watchers; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE active_watchers (
    id integer NOT NULL,
    presentity_uri character varying(128) NOT NULL,
    watcher_username character varying(64) NOT NULL,
    watcher_domain character varying(64) NOT NULL,
    to_user character varying(64) NOT NULL,
    to_domain character varying(64) NOT NULL,
    event character varying(64) DEFAULT 'presence'::character varying NOT NULL,
    event_id character varying(64),
    to_tag character varying(64) NOT NULL,
    from_tag character varying(64) NOT NULL,
    callid character varying(255) NOT NULL,
    local_cseq integer NOT NULL,
    remote_cseq integer NOT NULL,
    contact character varying(128) NOT NULL,
    record_route text,
    expires integer NOT NULL,
    status integer DEFAULT 2 NOT NULL,
    reason character varying(64) NOT NULL,
    version integer DEFAULT 0 NOT NULL,
    socket_info character varying(64) NOT NULL,
    local_contact character varying(128) NOT NULL,
    from_user character varying(64) NOT NULL,
    from_domain character varying(64) NOT NULL,
    updated integer NOT NULL,
    updated_winfo integer NOT NULL
);


ALTER TABLE active_watchers OWNER TO kamailio;

--
-- Name: active_watchers_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE active_watchers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE active_watchers_id_seq OWNER TO kamailio;

--
-- Name: active_watchers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE active_watchers_id_seq OWNED BY active_watchers.id;


--
-- Name: address; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE address (
    id integer NOT NULL,
    grp integer DEFAULT 1 NOT NULL,
    ip_addr character varying(50) NOT NULL,
    mask integer DEFAULT 32 NOT NULL,
    port smallint DEFAULT 0 NOT NULL,
    tag character varying(64)
);


ALTER TABLE address OWNER TO kamailio;

--
-- Name: address_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE address_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE address_id_seq OWNER TO kamailio;

--
-- Name: address_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE address_id_seq OWNED BY address.id;


--
-- Name: aliases; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE aliases (
    id integer NOT NULL,
    ruid character varying(64) DEFAULT ''::character varying NOT NULL,
    username character varying(64) DEFAULT ''::character varying NOT NULL,
    domain character varying(64) DEFAULT NULL::character varying,
    contact character varying(255) DEFAULT ''::character varying NOT NULL,
    received character varying(128) DEFAULT NULL::character varying,
    path character varying(512) DEFAULT NULL::character varying,
    expires timestamp without time zone DEFAULT '2030-05-28 21:32:15'::timestamp without time zone NOT NULL,
    q real DEFAULT 1.0 NOT NULL,
    callid character varying(255) DEFAULT 'Default-Call-ID'::character varying NOT NULL,
    cseq integer DEFAULT 1 NOT NULL,
    last_modified timestamp without time zone DEFAULT '1900-01-01 00:00:01'::timestamp without time zone NOT NULL,
    flags integer DEFAULT 0 NOT NULL,
    cflags integer DEFAULT 0 NOT NULL,
    user_agent character varying(255) DEFAULT ''::character varying NOT NULL,
    socket character varying(64) DEFAULT NULL::character varying,
    methods integer,
    instance character varying(255) DEFAULT NULL::character varying,
    reg_id integer DEFAULT 0 NOT NULL,
    server_id integer DEFAULT 0 NOT NULL,
    connection_id integer DEFAULT 0 NOT NULL,
    keepalive integer DEFAULT 0 NOT NULL,
    partition integer DEFAULT 0 NOT NULL
);


ALTER TABLE aliases OWNER TO kamailio;

--
-- Name: aliases_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE aliases_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE aliases_id_seq OWNER TO kamailio;

--
-- Name: aliases_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE aliases_id_seq OWNED BY aliases.id;


--
-- Name: carrier_name; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE carrier_name (
    id integer NOT NULL,
    carrier character varying(64) DEFAULT NULL::character varying
);


ALTER TABLE carrier_name OWNER TO kamailio;

--
-- Name: carrier_name_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE carrier_name_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE carrier_name_id_seq OWNER TO kamailio;

--
-- Name: carrier_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE carrier_name_id_seq OWNED BY carrier_name.id;


--
-- Name: carrierfailureroute; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE carrierfailureroute (
    id integer NOT NULL,
    carrier integer DEFAULT 0 NOT NULL,
    domain integer DEFAULT 0 NOT NULL,
    scan_prefix character varying(64) DEFAULT ''::character varying NOT NULL,
    host_name character varying(128) DEFAULT ''::character varying NOT NULL,
    reply_code character varying(3) DEFAULT ''::character varying NOT NULL,
    flags integer DEFAULT 0 NOT NULL,
    mask integer DEFAULT 0 NOT NULL,
    next_domain integer DEFAULT 0 NOT NULL,
    description character varying(255) DEFAULT NULL::character varying
);


ALTER TABLE carrierfailureroute OWNER TO kamailio;

--
-- Name: carrierfailureroute_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE carrierfailureroute_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE carrierfailureroute_id_seq OWNER TO kamailio;

--
-- Name: carrierfailureroute_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE carrierfailureroute_id_seq OWNED BY carrierfailureroute.id;


--
-- Name: carrierroute; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE carrierroute (
    id integer NOT NULL,
    carrier integer DEFAULT 0 NOT NULL,
    domain integer DEFAULT 0 NOT NULL,
    scan_prefix character varying(64) DEFAULT ''::character varying NOT NULL,
    flags integer DEFAULT 0 NOT NULL,
    mask integer DEFAULT 0 NOT NULL,
    prob real DEFAULT 0 NOT NULL,
    strip integer DEFAULT 0 NOT NULL,
    rewrite_host character varying(128) DEFAULT ''::character varying NOT NULL,
    rewrite_prefix character varying(64) DEFAULT ''::character varying NOT NULL,
    rewrite_suffix character varying(64) DEFAULT ''::character varying NOT NULL,
    description character varying(255) DEFAULT NULL::character varying
);


ALTER TABLE carrierroute OWNER TO kamailio;

--
-- Name: carrierroute_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE carrierroute_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE carrierroute_id_seq OWNER TO kamailio;

--
-- Name: carrierroute_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE carrierroute_id_seq OWNED BY carrierroute.id;

--
-- Name: cdr; Type: TABLE; Schema: public; Owner: kamailio; Tablespace:
--


CREATE TABLE cdr (
    calldate timestamp without time zone NOT NULL,
    clid character varying(80) NOT NULL,
    src character varying(80) NOT NULL,
    dst character varying(80) NOT NULL,
    dcontext character varying(80) NOT NULL,
    channel character varying(80) NOT NULL,
    dstchannel character varying(80) NOT NULL,
    lastapp character varying(80) NOT NULL,
    lastdata character varying(80) NOT NULL,
    duration integer NOT NULL,
    billsec integer NOT NULL,
    disposition character varying(45) NOT NULL,
    amaflags integer NOT NULL,
    accountcode character varying(20) NOT NULL,
    uniqueid character varying(150) NOT NULL,
    userfield character varying(255) NOT NULL
);

ALTER TABLE cdr OWNER TO kamailio;

--
-- Name: cpl; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE cpl (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    domain character varying(64) DEFAULT ''::character varying NOT NULL,
    cpl_xml text,
    cpl_bin text
);


ALTER TABLE cpl OWNER TO kamailio;

--
-- Name: cpl_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE cpl_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE cpl_id_seq OWNER TO kamailio;

--
-- Name: cpl_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE cpl_id_seq OWNED BY cpl.id;


--
-- Name: dbaliases; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE dbaliases (
    id integer NOT NULL,
    alias_username character varying(64) DEFAULT ''::character varying NOT NULL,
    alias_domain character varying(64) DEFAULT ''::character varying NOT NULL,
    username character varying(64) DEFAULT ''::character varying NOT NULL,
    domain character varying(64) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE dbaliases OWNER TO kamailio;

--
-- Name: dbaliases_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE dbaliases_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dbaliases_id_seq OWNER TO kamailio;

--
-- Name: dbaliases_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE dbaliases_id_seq OWNED BY dbaliases.id;


--
-- Name: dialog; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE dialog (
    id integer NOT NULL,
    hash_entry integer NOT NULL,
    hash_id integer NOT NULL,
    callid character varying(255) NOT NULL,
    from_uri character varying(128) NOT NULL,
    from_tag character varying(64) NOT NULL,
    to_uri character varying(128) NOT NULL,
    to_tag character varying(64) NOT NULL,
    caller_cseq character varying(20) NOT NULL,
    callee_cseq character varying(20) NOT NULL,
    caller_route_set character varying(512),
    callee_route_set character varying(512),
    caller_contact character varying(128) NOT NULL,
    callee_contact character varying(128) NOT NULL,
    caller_sock character varying(64) NOT NULL,
    callee_sock character varying(64) NOT NULL,
    state integer NOT NULL,
    start_time integer NOT NULL,
    timeout integer DEFAULT 0 NOT NULL,
    sflags integer DEFAULT 0 NOT NULL,
    iflags integer DEFAULT 0 NOT NULL,
    toroute_name character varying(32),
    req_uri character varying(128) NOT NULL,
    xdata character varying(512)
);


ALTER TABLE dialog OWNER TO kamailio;

--
-- Name: dialog_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE dialog_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dialog_id_seq OWNER TO kamailio;

--
-- Name: dialog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE dialog_id_seq OWNED BY dialog.id;


--
-- Name: dialog_vars; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE dialog_vars (
    id integer NOT NULL,
    hash_entry integer NOT NULL,
    hash_id integer NOT NULL,
    dialog_key character varying(128) NOT NULL,
    dialog_value character varying(512) NOT NULL
);


ALTER TABLE dialog_vars OWNER TO kamailio;

--
-- Name: dialog_vars_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE dialog_vars_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dialog_vars_id_seq OWNER TO kamailio;

--
-- Name: dialog_vars_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE dialog_vars_id_seq OWNED BY dialog_vars.id;


--
-- Name: dialplan; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE dialplan (
    id integer NOT NULL,
    dpid integer NOT NULL,
    pr integer NOT NULL,
    match_op integer NOT NULL,
    match_exp character varying(64) NOT NULL,
    match_len integer NOT NULL,
    subst_exp character varying(64) NOT NULL,
    repl_exp character varying(64) NOT NULL,
    attrs character varying(64) NOT NULL
);


ALTER TABLE dialplan OWNER TO kamailio;

--
-- Name: dialplan_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE dialplan_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dialplan_id_seq OWNER TO kamailio;

--
-- Name: dialplan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE dialplan_id_seq OWNED BY dialplan.id;


--
-- Name: dispatcher; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE dispatcher (
    id integer NOT NULL,
    setid integer DEFAULT 0 NOT NULL,
    destination character varying(192) DEFAULT ''::character varying NOT NULL,
    flags integer DEFAULT 0 NOT NULL,
    priority integer DEFAULT 0 NOT NULL,
    attrs character varying(128) DEFAULT ''::character varying NOT NULL,
    description character varying(64) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE dispatcher OWNER TO kamailio;

--
-- Name: dispatcher_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE dispatcher_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dispatcher_id_seq OWNER TO kamailio;

--
-- Name: dispatcher_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE dispatcher_id_seq OWNED BY dispatcher.id;


--
-- Name: domain; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE domain (
    id integer NOT NULL,
    domain character varying(64) NOT NULL,
    did character varying(64) DEFAULT NULL::character varying,
    last_modified timestamp without time zone DEFAULT '1900-01-01 00:00:01'::timestamp without time zone NOT NULL
);


ALTER TABLE domain OWNER TO kamailio;

--
-- Name: domain_attrs; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE domain_attrs (
    id integer NOT NULL,
    did character varying(64) NOT NULL,
    name character varying(32) NOT NULL,
    type integer NOT NULL,
    value character varying(255) NOT NULL,
    last_modified timestamp without time zone DEFAULT '1900-01-01 00:00:01'::timestamp without time zone NOT NULL
);


ALTER TABLE domain_attrs OWNER TO kamailio;

--
-- Name: domain_attrs_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE domain_attrs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE domain_attrs_id_seq OWNER TO kamailio;

--
-- Name: domain_attrs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE domain_attrs_id_seq OWNED BY domain_attrs.id;


--
-- Name: domain_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE domain_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE domain_id_seq OWNER TO kamailio;

--
-- Name: domain_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE domain_id_seq OWNED BY domain.id;


--
-- Name: domain_name; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE domain_name (
    id integer NOT NULL,
    domain character varying(64) DEFAULT NULL::character varying
);


ALTER TABLE domain_name OWNER TO kamailio;

--
-- Name: domain_name_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE domain_name_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE domain_name_id_seq OWNER TO kamailio;

--
-- Name: domain_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE domain_name_id_seq OWNED BY domain_name.id;


--
-- Name: domainpolicy; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE domainpolicy (
    id integer NOT NULL,
    rule character varying(255) NOT NULL,
    type character varying(255) NOT NULL,
    att character varying(255),
    val character varying(128),
    description character varying(255) NOT NULL
);


ALTER TABLE domainpolicy OWNER TO kamailio;

--
-- Name: domainpolicy_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE domainpolicy_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE domainpolicy_id_seq OWNER TO kamailio;

--
-- Name: domainpolicy_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE domainpolicy_id_seq OWNED BY domainpolicy.id;


--
-- Name: globalblacklist; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE globalblacklist (
    id integer NOT NULL,
    prefix character varying(64) DEFAULT ''::character varying NOT NULL,
    whitelist smallint DEFAULT 0 NOT NULL,
    description character varying(255) DEFAULT NULL::character varying
);


ALTER TABLE globalblacklist OWNER TO kamailio;

--
-- Name: globalblacklist_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE globalblacklist_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE globalblacklist_id_seq OWNER TO kamailio;

--
-- Name: globalblacklist_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE globalblacklist_id_seq OWNED BY globalblacklist.id;


--
-- Name: grp; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE grp (
    id integer NOT NULL,
    username character varying(64) DEFAULT ''::character varying NOT NULL,
    domain character varying(64) DEFAULT ''::character varying NOT NULL,
    grp character varying(64) DEFAULT ''::character varying NOT NULL,
    last_modified timestamp without time zone DEFAULT '1900-01-01 00:00:01'::timestamp without time zone NOT NULL
);


ALTER TABLE grp OWNER TO kamailio;

--
-- Name: grp_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE grp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE grp_id_seq OWNER TO kamailio;

--
-- Name: grp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE grp_id_seq OWNED BY grp.id;


--
-- Name: htable; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE htable (
    id integer NOT NULL,
    key_name character varying(64) DEFAULT ''::character varying NOT NULL,
    key_type integer DEFAULT 0 NOT NULL,
    value_type integer DEFAULT 0 NOT NULL,
    key_value character varying(128) DEFAULT ''::character varying NOT NULL,
    expires integer DEFAULT 0 NOT NULL
);


ALTER TABLE htable OWNER TO kamailio;

--
-- Name: htable_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE htable_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE htable_id_seq OWNER TO kamailio;

--
-- Name: htable_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE htable_id_seq OWNED BY htable.id;


--
-- Name: imc_members; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE imc_members (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    domain character varying(64) NOT NULL,
    room character varying(64) NOT NULL,
    flag integer NOT NULL
);


ALTER TABLE imc_members OWNER TO kamailio;

--
-- Name: imc_members_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE imc_members_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE imc_members_id_seq OWNER TO kamailio;

--
-- Name: imc_members_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE imc_members_id_seq OWNED BY imc_members.id;


--
-- Name: imc_rooms; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE imc_rooms (
    id integer NOT NULL,
    name character varying(64) NOT NULL,
    domain character varying(64) NOT NULL,
    flag integer NOT NULL
);


ALTER TABLE imc_rooms OWNER TO kamailio;

--
-- Name: imc_rooms_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE imc_rooms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE imc_rooms_id_seq OWNER TO kamailio;

--
-- Name: imc_rooms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE imc_rooms_id_seq OWNED BY imc_rooms.id;


--
-- Name: lcr_gw; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE lcr_gw (
    id integer NOT NULL,
    lcr_id smallint NOT NULL,
    gw_name character varying(128),
    ip_addr character varying(50),
    hostname character varying(64),
    port smallint,
    params character varying(64),
    uri_scheme smallint,
    transport smallint,
    strip smallint,
    prefix character varying(16) DEFAULT NULL::character varying,
    tag character varying(64) DEFAULT NULL::character varying,
    flags integer DEFAULT 0 NOT NULL,
    defunct integer
);


ALTER TABLE lcr_gw OWNER TO kamailio;

--
-- Name: lcr_gw_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE lcr_gw_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE lcr_gw_id_seq OWNER TO kamailio;

--
-- Name: lcr_gw_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE lcr_gw_id_seq OWNED BY lcr_gw.id;


--
-- Name: lcr_rule; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE lcr_rule (
    id integer NOT NULL,
    lcr_id smallint NOT NULL,
    prefix character varying(16) DEFAULT NULL::character varying,
    from_uri character varying(64) DEFAULT NULL::character varying,
    request_uri character varying(64) DEFAULT NULL::character varying,
    stopper integer DEFAULT 0 NOT NULL,
    enabled integer DEFAULT 1 NOT NULL
);


ALTER TABLE lcr_rule OWNER TO kamailio;

--
-- Name: lcr_rule_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE lcr_rule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE lcr_rule_id_seq OWNER TO kamailio;

--
-- Name: lcr_rule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE lcr_rule_id_seq OWNED BY lcr_rule.id;


--
-- Name: lcr_rule_target; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE lcr_rule_target (
    id integer NOT NULL,
    lcr_id smallint NOT NULL,
    rule_id integer NOT NULL,
    gw_id integer NOT NULL,
    priority smallint NOT NULL,
    weight integer DEFAULT 1 NOT NULL
);


ALTER TABLE lcr_rule_target OWNER TO kamailio;

--
-- Name: lcr_rule_target_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE lcr_rule_target_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE lcr_rule_target_id_seq OWNER TO kamailio;

--
-- Name: lcr_rule_target_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE lcr_rule_target_id_seq OWNED BY lcr_rule_target.id;


--
-- Name: location; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE location (
    id integer NOT NULL,
    ruid character varying(64) DEFAULT ''::character varying NOT NULL,
    username character varying(64) DEFAULT ''::character varying NOT NULL,
    domain character varying(64) DEFAULT NULL::character varying,
    contact character varying(255) DEFAULT ''::character varying NOT NULL,
    received character varying(128) DEFAULT NULL::character varying,
    path character varying(512) DEFAULT NULL::character varying,
    expires timestamp without time zone DEFAULT '2030-05-28 21:32:15'::timestamp without time zone NOT NULL,
    q real DEFAULT 1.0 NOT NULL,
    callid character varying(255) DEFAULT 'Default-Call-ID'::character varying NOT NULL,
    cseq integer DEFAULT 1 NOT NULL,
    last_modified timestamp without time zone DEFAULT '1900-01-01 00:00:01'::timestamp without time zone NOT NULL,
    flags integer DEFAULT 0 NOT NULL,
    cflags integer DEFAULT 0 NOT NULL,
    user_agent character varying(255) DEFAULT ''::character varying NOT NULL,
    socket character varying(64) DEFAULT NULL::character varying,
    methods integer,
    instance character varying(255) DEFAULT NULL::character varying,
    reg_id integer DEFAULT 0 NOT NULL,
    server_id integer DEFAULT 0 NOT NULL,
    connection_id integer DEFAULT 0 NOT NULL,
    keepalive integer DEFAULT 0 NOT NULL,
    partition integer DEFAULT 0 NOT NULL
);


ALTER TABLE location OWNER TO kamailio;

--
-- Name: location_attrs; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE location_attrs (
    id integer NOT NULL,
    ruid character varying(64) DEFAULT ''::character varying NOT NULL,
    username character varying(64) DEFAULT ''::character varying NOT NULL,
    domain character varying(64) DEFAULT NULL::character varying,
    aname character varying(64) DEFAULT ''::character varying NOT NULL,
    atype integer DEFAULT 0 NOT NULL,
    avalue character varying(255) DEFAULT ''::character varying NOT NULL,
    last_modified timestamp without time zone DEFAULT '1900-01-01 00:00:01'::timestamp without time zone NOT NULL
);


ALTER TABLE location_attrs OWNER TO kamailio;

--
-- Name: location_attrs_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE location_attrs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE location_attrs_id_seq OWNER TO kamailio;

--
-- Name: location_attrs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE location_attrs_id_seq OWNED BY location_attrs.id;


--
-- Name: location_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE location_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE location_id_seq OWNER TO kamailio;

--
-- Name: location_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE location_id_seq OWNED BY location.id;


--
-- Name: missed_calls; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE missed_calls (
    id integer NOT NULL,
    method character varying(16) DEFAULT ''::character varying NOT NULL,
    from_tag character varying(64) DEFAULT ''::character varying NOT NULL,
    to_tag character varying(64) DEFAULT ''::character varying NOT NULL,
    callid character varying(255) DEFAULT ''::character varying NOT NULL,
    sip_code character varying(3) DEFAULT ''::character varying NOT NULL,
    sip_reason character varying(128) DEFAULT ''::character varying NOT NULL,
    "time" timestamp without time zone NOT NULL
);


ALTER TABLE missed_calls OWNER TO kamailio;

--
-- Name: missed_calls_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE missed_calls_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE missed_calls_id_seq OWNER TO kamailio;

--
-- Name: missed_calls_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE missed_calls_id_seq OWNED BY missed_calls.id;


--
-- Name: mohqcalls; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE mohqcalls (
    id integer NOT NULL,
    mohq_id integer NOT NULL,
    call_id character varying(100) NOT NULL,
    call_status integer NOT NULL,
    call_from character varying(100) NOT NULL,
    call_contact character varying(100),
    call_time timestamp without time zone NOT NULL
);


ALTER TABLE mohqcalls OWNER TO kamailio;

--
-- Name: mohqcalls_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE mohqcalls_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE mohqcalls_id_seq OWNER TO kamailio;

--
-- Name: mohqcalls_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE mohqcalls_id_seq OWNED BY mohqcalls.id;


--
-- Name: mohqueues; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE mohqueues (
    id integer NOT NULL,
    name character varying(25) NOT NULL,
    uri character varying(100) NOT NULL,
    mohdir character varying(100),
    mohfile character varying(100) NOT NULL,
    debug integer NOT NULL
);


ALTER TABLE mohqueues OWNER TO kamailio;

--
-- Name: mohqueues_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE mohqueues_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE mohqueues_id_seq OWNER TO kamailio;

--
-- Name: mohqueues_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE mohqueues_id_seq OWNED BY mohqueues.id;


--
-- Name: mtree; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE mtree (
    id integer NOT NULL,
    tprefix character varying(32) DEFAULT ''::character varying NOT NULL,
    tvalue character varying(128) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE mtree OWNER TO kamailio;

--
-- Name: mtree_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE mtree_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE mtree_id_seq OWNER TO kamailio;

--
-- Name: mtree_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE mtree_id_seq OWNED BY mtree.id;


--
-- Name: mtrees; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE mtrees (
    id integer NOT NULL,
    tname character varying(128) DEFAULT ''::character varying NOT NULL,
    tprefix character varying(32) DEFAULT ''::character varying NOT NULL,
    tvalue character varying(128) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE mtrees OWNER TO kamailio;

--
-- Name: mtrees_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE mtrees_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE mtrees_id_seq OWNER TO kamailio;

--
-- Name: mtrees_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE mtrees_id_seq OWNED BY mtrees.id;


--
-- Name: pdt; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE pdt (
    id integer NOT NULL,
    sdomain character varying(128) NOT NULL,
    prefix character varying(32) NOT NULL,
    domain character varying(128) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE pdt OWNER TO kamailio;

--
-- Name: pdt_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE pdt_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE pdt_id_seq OWNER TO kamailio;

--
-- Name: pdt_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE pdt_id_seq OWNED BY pdt.id;


--
-- Name: pl_pipes; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE pl_pipes (
    id integer NOT NULL,
    pipeid character varying(64) DEFAULT ''::character varying NOT NULL,
    algorithm character varying(32) DEFAULT ''::character varying NOT NULL,
    plimit integer DEFAULT 0 NOT NULL
);


ALTER TABLE pl_pipes OWNER TO kamailio;

--
-- Name: pl_pipes_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE pl_pipes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE pl_pipes_id_seq OWNER TO kamailio;

--
-- Name: pl_pipes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE pl_pipes_id_seq OWNED BY pl_pipes.id;


--
-- Name: presentity; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE presentity (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    domain character varying(64) NOT NULL,
    event character varying(64) NOT NULL,
    etag character varying(64) NOT NULL,
    expires integer NOT NULL,
    received_time integer NOT NULL,
    body bytea NOT NULL,
    sender character varying(128) NOT NULL,
    priority integer DEFAULT 0 NOT NULL
);


ALTER TABLE presentity OWNER TO kamailio;

--
-- Name: presentity_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE presentity_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE presentity_id_seq OWNER TO kamailio;

--
-- Name: presentity_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE presentity_id_seq OWNED BY presentity.id;


--
-- Name: pua; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE pua (
    id integer NOT NULL,
    pres_uri character varying(128) NOT NULL,
    pres_id character varying(255) NOT NULL,
    event integer NOT NULL,
    expires integer NOT NULL,
    desired_expires integer NOT NULL,
    flag integer NOT NULL,
    etag character varying(64) NOT NULL,
    tuple_id character varying(64),
    watcher_uri character varying(128) NOT NULL,
    call_id character varying(255) NOT NULL,
    to_tag character varying(64) NOT NULL,
    from_tag character varying(64) NOT NULL,
    cseq integer NOT NULL,
    record_route text,
    contact character varying(128) NOT NULL,
    remote_contact character varying(128) NOT NULL,
    version integer NOT NULL,
    extra_headers text NOT NULL
);


ALTER TABLE pua OWNER TO kamailio;

--
-- Name: pua_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE pua_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE pua_id_seq OWNER TO kamailio;

--
-- Name: pua_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE pua_id_seq OWNED BY pua.id;


--
-- Name: purplemap; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE purplemap (
    id integer NOT NULL,
    sip_user character varying(128) NOT NULL,
    ext_user character varying(128) NOT NULL,
    ext_prot character varying(16) NOT NULL,
    ext_pass character varying(64)
);


ALTER TABLE purplemap OWNER TO kamailio;

--
-- Name: purplemap_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE purplemap_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE purplemap_id_seq OWNER TO kamailio;

--
-- Name: purplemap_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE purplemap_id_seq OWNED BY purplemap.id;


--
-- Name: re_grp; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE re_grp (
    id integer NOT NULL,
    reg_exp character varying(128) DEFAULT ''::character varying NOT NULL,
    group_id integer DEFAULT 0 NOT NULL
);


ALTER TABLE re_grp OWNER TO kamailio;

--
-- Name: re_grp_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE re_grp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE re_grp_id_seq OWNER TO kamailio;

--
-- Name: re_grp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE re_grp_id_seq OWNED BY re_grp.id;


--
-- Name: rls_presentity; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE rls_presentity (
    id integer NOT NULL,
    rlsubs_did character varying(255) NOT NULL,
    resource_uri character varying(128) NOT NULL,
    content_type character varying(255) NOT NULL,
    presence_state bytea NOT NULL,
    expires integer NOT NULL,
    updated integer NOT NULL,
    auth_state integer NOT NULL,
    reason character varying(64) NOT NULL
);


ALTER TABLE rls_presentity OWNER TO kamailio;

--
-- Name: rls_presentity_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE rls_presentity_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rls_presentity_id_seq OWNER TO kamailio;

--
-- Name: rls_presentity_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE rls_presentity_id_seq OWNED BY rls_presentity.id;


--
-- Name: rls_watchers; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE rls_watchers (
    id integer NOT NULL,
    presentity_uri character varying(128) NOT NULL,
    to_user character varying(64) NOT NULL,
    to_domain character varying(64) NOT NULL,
    watcher_username character varying(64) NOT NULL,
    watcher_domain character varying(64) NOT NULL,
    event character varying(64) DEFAULT 'presence'::character varying NOT NULL,
    event_id character varying(64),
    to_tag character varying(64) NOT NULL,
    from_tag character varying(64) NOT NULL,
    callid character varying(255) NOT NULL,
    local_cseq integer NOT NULL,
    remote_cseq integer NOT NULL,
    contact character varying(128) NOT NULL,
    record_route text,
    expires integer NOT NULL,
    status integer DEFAULT 2 NOT NULL,
    reason character varying(64) NOT NULL,
    version integer DEFAULT 0 NOT NULL,
    socket_info character varying(64) NOT NULL,
    local_contact character varying(128) NOT NULL,
    from_user character varying(64) NOT NULL,
    from_domain character varying(64) NOT NULL,
    updated integer NOT NULL
);


ALTER TABLE rls_watchers OWNER TO kamailio;

--
-- Name: rls_watchers_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE rls_watchers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rls_watchers_id_seq OWNER TO kamailio;

--
-- Name: rls_watchers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE rls_watchers_id_seq OWNED BY rls_watchers.id;


--
-- Name: rtpproxy; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE rtpproxy (
    id integer NOT NULL,
    setid character varying(32) DEFAULT 0 NOT NULL,
    url character varying(64) DEFAULT ''::character varying NOT NULL,
    flags integer DEFAULT 0 NOT NULL,
    weight integer DEFAULT 1 NOT NULL,
    description character varying(64) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE rtpproxy OWNER TO kamailio;

--
-- Name: rtpproxy_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE rtpproxy_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rtpproxy_id_seq OWNER TO kamailio;

--
-- Name: rtpproxy_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE rtpproxy_id_seq OWNED BY rtpproxy.id;


--
-- Name: sca_subscriptions; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE sca_subscriptions (
    id integer NOT NULL,
    subscriber character varying(255) NOT NULL,
    aor character varying(255) NOT NULL,
    event integer DEFAULT 0 NOT NULL,
    expires integer DEFAULT 0 NOT NULL,
    state integer DEFAULT 0 NOT NULL,
    app_idx integer DEFAULT 0 NOT NULL,
    call_id character varying(255) NOT NULL,
    from_tag character varying(64) NOT NULL,
    to_tag character varying(64) NOT NULL,
    record_route text,
    notify_cseq integer NOT NULL,
    subscribe_cseq integer NOT NULL
);


ALTER TABLE sca_subscriptions OWNER TO kamailio;

--
-- Name: sca_subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE sca_subscriptions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE sca_subscriptions_id_seq OWNER TO kamailio;

--
-- Name: sca_subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE sca_subscriptions_id_seq OWNED BY sca_subscriptions.id;


--
-- Name: silo; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE silo (
    id integer NOT NULL,
    src_addr character varying(128) DEFAULT ''::character varying NOT NULL,
    dst_addr character varying(128) DEFAULT ''::character varying NOT NULL,
    username character varying(64) DEFAULT ''::character varying NOT NULL,
    domain character varying(64) DEFAULT ''::character varying NOT NULL,
    inc_time integer DEFAULT 0 NOT NULL,
    exp_time integer DEFAULT 0 NOT NULL,
    snd_time integer DEFAULT 0 NOT NULL,
    ctype character varying(32) DEFAULT 'text/plain'::character varying NOT NULL,
    body bytea,
    extra_hdrs text,
    callid character varying(128) DEFAULT ''::character varying NOT NULL,
    status integer DEFAULT 0 NOT NULL
);


ALTER TABLE silo OWNER TO kamailio;

--
-- Name: silo_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE silo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE silo_id_seq OWNER TO kamailio;

--
-- Name: silo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE silo_id_seq OWNED BY silo.id;


--
-- Name: sip_trace; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE sip_trace (
    id integer NOT NULL,
    time_stamp timestamp without time zone DEFAULT '1900-01-01 00:00:01'::timestamp without time zone NOT NULL,
    time_us integer DEFAULT 0 NOT NULL,
    callid character varying(255) DEFAULT ''::character varying NOT NULL,
    traced_user character varying(128) DEFAULT ''::character varying NOT NULL,
    msg text NOT NULL,
    method character varying(50) DEFAULT ''::character varying NOT NULL,
    status character varying(128) DEFAULT ''::character varying NOT NULL,
    fromip character varying(50) DEFAULT ''::character varying NOT NULL,
    toip character varying(50) DEFAULT ''::character varying NOT NULL,
    fromtag character varying(64) DEFAULT ''::character varying NOT NULL,
    totag character varying(64) DEFAULT ''::character varying NOT NULL,
    direction character varying(4) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE sip_trace OWNER TO kamailio;

--
-- Name: sip_trace_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE sip_trace_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE sip_trace_id_seq OWNER TO kamailio;

--
-- Name: sip_trace_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE sip_trace_id_seq OWNED BY sip_trace.id;


--
-- Name: speed_dial; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE speed_dial (
    id integer NOT NULL,
    username character varying(64) DEFAULT ''::character varying NOT NULL,
    domain character varying(64) DEFAULT ''::character varying NOT NULL,
    sd_username character varying(64) DEFAULT ''::character varying NOT NULL,
    sd_domain character varying(64) DEFAULT ''::character varying NOT NULL,
    new_uri character varying(128) DEFAULT ''::character varying NOT NULL,
    fname character varying(64) DEFAULT ''::character varying NOT NULL,
    lname character varying(64) DEFAULT ''::character varying NOT NULL,
    description character varying(64) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE speed_dial OWNER TO kamailio;

--
-- Name: speed_dial_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE speed_dial_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE speed_dial_id_seq OWNER TO kamailio;

--
-- Name: speed_dial_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE speed_dial_id_seq OWNED BY speed_dial.id;


--
-- Name: subscriber; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE subscriber (
    id integer NOT NULL,
    username character varying(64) DEFAULT ''::character varying NOT NULL,
    domain character varying(64) DEFAULT ''::character varying NOT NULL,
    password character varying(25) DEFAULT ''::character varying NOT NULL,
    email_address character varying(64) DEFAULT ''::character varying NOT NULL,
    ha1 character varying(64) DEFAULT ''::character varying NOT NULL,
    ha1b character varying(64) DEFAULT ''::character varying NOT NULL,
    rpid character varying(64) DEFAULT NULL::character varying
);


ALTER TABLE subscriber OWNER TO kamailio;

--
-- Name: subscriber_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE subscriber_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE subscriber_id_seq OWNER TO kamailio;

--
-- Name: subscriber_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE subscriber_id_seq OWNED BY subscriber.id;


--
-- Name: trusted; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE trusted (
    id integer NOT NULL,
    src_ip character varying(50) NOT NULL,
    proto character varying(4) NOT NULL,
    from_pattern character varying(64) DEFAULT NULL::character varying,
    tag character varying(64)
);


ALTER TABLE trusted OWNER TO kamailio;

--
-- Name: trusted_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE trusted_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE trusted_id_seq OWNER TO kamailio;

--
-- Name: trusted_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE trusted_id_seq OWNED BY trusted.id;


--
-- Name: uacreg; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE uacreg (
    id integer NOT NULL,
    l_uuid character varying(64) DEFAULT ''::character varying NOT NULL,
    l_username character varying(64) DEFAULT ''::character varying NOT NULL,
    l_domain character varying(128) DEFAULT ''::character varying NOT NULL,
    r_username character varying(64) DEFAULT ''::character varying NOT NULL,
    r_domain character varying(128) DEFAULT ''::character varying NOT NULL,
    realm character varying(64) DEFAULT ''::character varying NOT NULL,
    auth_username character varying(64) DEFAULT ''::character varying NOT NULL,
    auth_password character varying(64) DEFAULT ''::character varying NOT NULL,
    auth_proxy character varying(64) DEFAULT ''::character varying NOT NULL,
    expires integer DEFAULT 0 NOT NULL
);


ALTER TABLE uacreg OWNER TO kamailio;

--
-- Name: uacreg_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE uacreg_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE uacreg_id_seq OWNER TO kamailio;

--
-- Name: uacreg_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE uacreg_id_seq OWNED BY uacreg.id;


--
-- Name: uri; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE uri (
    id integer NOT NULL,
    username character varying(64) DEFAULT ''::character varying NOT NULL,
    domain character varying(64) DEFAULT ''::character varying NOT NULL,
    uri_user character varying(64) DEFAULT ''::character varying NOT NULL,
    last_modified timestamp without time zone DEFAULT '1900-01-01 00:00:01'::timestamp without time zone NOT NULL
);


ALTER TABLE uri OWNER TO kamailio;

--
-- Name: uri_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE uri_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE uri_id_seq OWNER TO kamailio;

--
-- Name: uri_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE uri_id_seq OWNED BY uri.id;


--
-- Name: userblacklist; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE userblacklist (
    id integer NOT NULL,
    username character varying(64) DEFAULT ''::character varying NOT NULL,
    domain character varying(64) DEFAULT ''::character varying NOT NULL,
    prefix character varying(64) DEFAULT ''::character varying NOT NULL,
    whitelist smallint DEFAULT 0 NOT NULL
);


ALTER TABLE userblacklist OWNER TO kamailio;

--
-- Name: userblacklist_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE userblacklist_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE userblacklist_id_seq OWNER TO kamailio;

--
-- Name: userblacklist_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE userblacklist_id_seq OWNED BY userblacklist.id;


--
-- Name: usr_preferences; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE usr_preferences (
    id integer NOT NULL,
    uuid character varying(64) DEFAULT ''::character varying NOT NULL,
    username character varying(128) DEFAULT 0 NOT NULL,
    domain character varying(64) DEFAULT ''::character varying NOT NULL,
    attribute character varying(32) DEFAULT ''::character varying NOT NULL,
    type integer DEFAULT 0 NOT NULL,
    value character varying(128) DEFAULT ''::character varying NOT NULL,
    last_modified timestamp without time zone DEFAULT '1900-01-01 00:00:01'::timestamp without time zone NOT NULL
);


ALTER TABLE usr_preferences OWNER TO kamailio;

--
-- Name: usr_preferences_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE usr_preferences_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE usr_preferences_id_seq OWNER TO kamailio;

--
-- Name: usr_preferences_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE usr_preferences_id_seq OWNED BY usr_preferences.id;


--
-- Name: version; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE version (
    table_name character varying(32) NOT NULL,
    table_version integer DEFAULT 0 NOT NULL
);


ALTER TABLE version OWNER TO kamailio;

--
-- Name: watchers; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE watchers (
    id integer NOT NULL,
    presentity_uri character varying(128) NOT NULL,
    watcher_username character varying(64) NOT NULL,
    watcher_domain character varying(64) NOT NULL,
    event character varying(64) DEFAULT 'presence'::character varying NOT NULL,
    status integer NOT NULL,
    reason character varying(64),
    inserted_time integer NOT NULL
);


ALTER TABLE watchers OWNER TO kamailio;

--
-- Name: watchers_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE watchers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE watchers_id_seq OWNER TO kamailio;

--
-- Name: watchers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE watchers_id_seq OWNED BY watchers.id;


--
-- Name: xcap; Type: TABLE; Schema: public; Owner: kamailio
--

CREATE TABLE xcap (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    domain character varying(64) NOT NULL,
    doc bytea NOT NULL,
    doc_type integer NOT NULL,
    etag character varying(64) NOT NULL,
    source integer NOT NULL,
    doc_uri character varying(255) NOT NULL,
    port integer NOT NULL
);


ALTER TABLE xcap OWNER TO kamailio;

--
-- Name: xcap_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE xcap_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE xcap_id_seq OWNER TO kamailio;

--
-- Name: xcap_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE xcap_id_seq OWNED BY xcap.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY acc ALTER COLUMN id SET DEFAULT nextval('acc_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY acc_cdrs ALTER COLUMN id SET DEFAULT nextval('acc_cdrs_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY active_watchers ALTER COLUMN id SET DEFAULT nextval('active_watchers_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY address ALTER COLUMN id SET DEFAULT nextval('address_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY aliases ALTER COLUMN id SET DEFAULT nextval('aliases_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY carrier_name ALTER COLUMN id SET DEFAULT nextval('carrier_name_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY carrierfailureroute ALTER COLUMN id SET DEFAULT nextval('carrierfailureroute_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY carrierroute ALTER COLUMN id SET DEFAULT nextval('carrierroute_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY cpl ALTER COLUMN id SET DEFAULT nextval('cpl_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY dbaliases ALTER COLUMN id SET DEFAULT nextval('dbaliases_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY dialog ALTER COLUMN id SET DEFAULT nextval('dialog_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY dialog_vars ALTER COLUMN id SET DEFAULT nextval('dialog_vars_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY dialplan ALTER COLUMN id SET DEFAULT nextval('dialplan_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY dispatcher ALTER COLUMN id SET DEFAULT nextval('dispatcher_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY domain ALTER COLUMN id SET DEFAULT nextval('domain_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY domain_attrs ALTER COLUMN id SET DEFAULT nextval('domain_attrs_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY domain_name ALTER COLUMN id SET DEFAULT nextval('domain_name_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY domainpolicy ALTER COLUMN id SET DEFAULT nextval('domainpolicy_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY globalblacklist ALTER COLUMN id SET DEFAULT nextval('globalblacklist_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY grp ALTER COLUMN id SET DEFAULT nextval('grp_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY htable ALTER COLUMN id SET DEFAULT nextval('htable_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY imc_members ALTER COLUMN id SET DEFAULT nextval('imc_members_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY imc_rooms ALTER COLUMN id SET DEFAULT nextval('imc_rooms_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY lcr_gw ALTER COLUMN id SET DEFAULT nextval('lcr_gw_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY lcr_rule ALTER COLUMN id SET DEFAULT nextval('lcr_rule_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY lcr_rule_target ALTER COLUMN id SET DEFAULT nextval('lcr_rule_target_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY location ALTER COLUMN id SET DEFAULT nextval('location_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY location_attrs ALTER COLUMN id SET DEFAULT nextval('location_attrs_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY missed_calls ALTER COLUMN id SET DEFAULT nextval('missed_calls_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY mohqcalls ALTER COLUMN id SET DEFAULT nextval('mohqcalls_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY mohqueues ALTER COLUMN id SET DEFAULT nextval('mohqueues_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY mtree ALTER COLUMN id SET DEFAULT nextval('mtree_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY mtrees ALTER COLUMN id SET DEFAULT nextval('mtrees_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY pdt ALTER COLUMN id SET DEFAULT nextval('pdt_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY pl_pipes ALTER COLUMN id SET DEFAULT nextval('pl_pipes_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY presentity ALTER COLUMN id SET DEFAULT nextval('presentity_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY pua ALTER COLUMN id SET DEFAULT nextval('pua_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY purplemap ALTER COLUMN id SET DEFAULT nextval('purplemap_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY re_grp ALTER COLUMN id SET DEFAULT nextval('re_grp_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY rls_presentity ALTER COLUMN id SET DEFAULT nextval('rls_presentity_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY rls_watchers ALTER COLUMN id SET DEFAULT nextval('rls_watchers_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY rtpproxy ALTER COLUMN id SET DEFAULT nextval('rtpproxy_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY sca_subscriptions ALTER COLUMN id SET DEFAULT nextval('sca_subscriptions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY silo ALTER COLUMN id SET DEFAULT nextval('silo_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY sip_trace ALTER COLUMN id SET DEFAULT nextval('sip_trace_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY speed_dial ALTER COLUMN id SET DEFAULT nextval('speed_dial_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY subscriber ALTER COLUMN id SET DEFAULT nextval('subscriber_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY trusted ALTER COLUMN id SET DEFAULT nextval('trusted_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY uacreg ALTER COLUMN id SET DEFAULT nextval('uacreg_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY uri ALTER COLUMN id SET DEFAULT nextval('uri_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY userblacklist ALTER COLUMN id SET DEFAULT nextval('userblacklist_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY usr_preferences ALTER COLUMN id SET DEFAULT nextval('usr_preferences_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY watchers ALTER COLUMN id SET DEFAULT nextval('watchers_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY xcap ALTER COLUMN id SET DEFAULT nextval('xcap_id_seq'::regclass);


--
-- Data for Name: acc; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY acc (id, method, from_tag, to_tag, callid, sip_code, sip_reason, "time") FROM stdin;
\.


--
-- Data for Name: acc_cdrs; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY acc_cdrs (id, start_time, end_time, duration) FROM stdin;
\.


--
-- Name: acc_cdrs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('acc_cdrs_id_seq', 1, false);


--
-- Name: acc_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('acc_id_seq', 1, false);


--
-- Data for Name: active_watchers; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY active_watchers (id, presentity_uri, watcher_username, watcher_domain, to_user, to_domain, event, event_id, to_tag, from_tag, callid, local_cseq, remote_cseq, contact, record_route, expires, status, reason, version, socket_info, local_contact, from_user, from_domain, updated, updated_winfo) FROM stdin;
\.


--
-- Name: active_watchers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('active_watchers_id_seq', 1, false);


--
-- Data for Name: address; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY address (id, grp, ip_addr, mask, port, tag) FROM stdin;
\.


--
-- Name: address_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('address_id_seq', 1, false);


--
-- Data for Name: aliases; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY aliases (id, ruid, username, domain, contact, received, path, expires, q, callid, cseq, last_modified, flags, cflags, user_agent, socket, methods, instance, reg_id, server_id, connection_id, keepalive, partition) FROM stdin;
\.


--
-- Name: aliases_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('aliases_id_seq', 1, false);


--
-- Data for Name: carrier_name; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY carrier_name (id, carrier) FROM stdin;
\.


--
-- Name: carrier_name_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('carrier_name_id_seq', 1, false);


--
-- Data for Name: carrierfailureroute; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY carrierfailureroute (id, carrier, domain, scan_prefix, host_name, reply_code, flags, mask, next_domain, description) FROM stdin;
\.


--
-- Name: carrierfailureroute_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('carrierfailureroute_id_seq', 1, false);


--
-- Data for Name: carrierroute; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY carrierroute (id, carrier, domain, scan_prefix, flags, mask, prob, strip, rewrite_host, rewrite_prefix, rewrite_suffix, description) FROM stdin;
\.


--
-- Name: carrierroute_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('carrierroute_id_seq', 1, false);


--
-- Data for Name: cpl; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY cpl (id, username, domain, cpl_xml, cpl_bin) FROM stdin;
\.


--
-- Name: cpl_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('cpl_id_seq', 1, false);


--
-- Data for Name: dbaliases; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY dbaliases (id, alias_username, alias_domain, username, domain) FROM stdin;
\.


--
-- Name: dbaliases_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('dbaliases_id_seq', 1, false);


--
-- Data for Name: dialog; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY dialog (id, hash_entry, hash_id, callid, from_uri, from_tag, to_uri, to_tag, caller_cseq, callee_cseq, caller_route_set, callee_route_set, caller_contact, callee_contact, caller_sock, callee_sock, state, start_time, timeout, sflags, iflags, toroute_name, req_uri, xdata) FROM stdin;
\.


--
-- Name: dialog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('dialog_id_seq', 1, false);


--
-- Data for Name: dialog_vars; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY dialog_vars (id, hash_entry, hash_id, dialog_key, dialog_value) FROM stdin;
\.


--
-- Name: dialog_vars_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('dialog_vars_id_seq', 1, false);


--
-- Data for Name: dialplan; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY dialplan (id, dpid, pr, match_op, match_exp, match_len, subst_exp, repl_exp, attrs) FROM stdin;
\.


--
-- Name: dialplan_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('dialplan_id_seq', 1, false);


--
-- Data for Name: dispatcher; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY dispatcher (id, setid, destination, flags, priority, attrs, description) FROM stdin;
\.


--
-- Name: dispatcher_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('dispatcher_id_seq', 1, false);


--
-- Data for Name: domain; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY domain (id, domain, did, last_modified) FROM stdin;
\.


--
-- Data for Name: domain_attrs; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY domain_attrs (id, did, name, type, value, last_modified) FROM stdin;
\.


--
-- Name: domain_attrs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('domain_attrs_id_seq', 1, false);


--
-- Name: domain_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('domain_id_seq', 1, false);


--
-- Data for Name: domain_name; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY domain_name (id, domain) FROM stdin;
\.


--
-- Name: domain_name_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('domain_name_id_seq', 1, false);


--
-- Data for Name: domainpolicy; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY domainpolicy (id, rule, type, att, val, description) FROM stdin;
\.


--
-- Name: domainpolicy_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('domainpolicy_id_seq', 1, false);


--
-- Data for Name: globalblacklist; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY globalblacklist (id, prefix, whitelist, description) FROM stdin;
\.


--
-- Name: globalblacklist_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('globalblacklist_id_seq', 1, false);


--
-- Data for Name: grp; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY grp (id, username, domain, grp, last_modified) FROM stdin;
\.


--
-- Name: grp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('grp_id_seq', 1, false);


--
-- Data for Name: htable; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY htable (id, key_name, key_type, value_type, key_value, expires) FROM stdin;
\.


--
-- Name: htable_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('htable_id_seq', 1, false);


--
-- Data for Name: imc_members; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY imc_members (id, username, domain, room, flag) FROM stdin;
\.


--
-- Name: imc_members_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('imc_members_id_seq', 1, false);


--
-- Data for Name: imc_rooms; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY imc_rooms (id, name, domain, flag) FROM stdin;
\.


--
-- Name: imc_rooms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('imc_rooms_id_seq', 1, false);


--
-- Data for Name: lcr_gw; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY lcr_gw (id, lcr_id, gw_name, ip_addr, hostname, port, params, uri_scheme, transport, strip, prefix, tag, flags, defunct) FROM stdin;
\.


--
-- Name: lcr_gw_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('lcr_gw_id_seq', 1, false);


--
-- Data for Name: lcr_rule; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY lcr_rule (id, lcr_id, prefix, from_uri, request_uri, stopper, enabled) FROM stdin;
\.


--
-- Name: lcr_rule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('lcr_rule_id_seq', 1, false);


--
-- Data for Name: lcr_rule_target; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY lcr_rule_target (id, lcr_id, rule_id, gw_id, priority, weight) FROM stdin;
\.


--
-- Name: lcr_rule_target_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('lcr_rule_target_id_seq', 1, false);


--
-- Data for Name: location; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY location (id, ruid, username, domain, contact, received, path, expires, q, callid, cseq, last_modified, flags, cflags, user_agent, socket, methods, instance, reg_id, server_id, connection_id, keepalive, partition) FROM stdin;
\.


--
-- Data for Name: location_attrs; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY location_attrs (id, ruid, username, domain, aname, atype, avalue, last_modified) FROM stdin;
\.


--
-- Name: location_attrs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('location_attrs_id_seq', 1, false);


--
-- Name: location_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('location_id_seq', 9, true);


--
-- Data for Name: missed_calls; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY missed_calls (id, method, from_tag, to_tag, callid, sip_code, sip_reason, "time") FROM stdin;
\.


--
-- Name: missed_calls_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('missed_calls_id_seq', 1, false);


--
-- Data for Name: mohqcalls; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY mohqcalls (id, mohq_id, call_id, call_status, call_from, call_contact, call_time) FROM stdin;
\.


--
-- Name: mohqcalls_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('mohqcalls_id_seq', 1, false);


--
-- Data for Name: mohqueues; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY mohqueues (id, name, uri, mohdir, mohfile, debug) FROM stdin;
\.


--
-- Name: mohqueues_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('mohqueues_id_seq', 1, false);


--
-- Data for Name: mtree; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY mtree (id, tprefix, tvalue) FROM stdin;
\.


--
-- Name: mtree_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('mtree_id_seq', 1, false);


--
-- Data for Name: mtrees; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY mtrees (id, tname, tprefix, tvalue) FROM stdin;
\.


--
-- Name: mtrees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('mtrees_id_seq', 1, false);


--
-- Data for Name: pdt; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY pdt (id, sdomain, prefix, domain) FROM stdin;
\.


--
-- Name: pdt_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('pdt_id_seq', 1, false);


--
-- Data for Name: pl_pipes; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY pl_pipes (id, pipeid, algorithm, plimit) FROM stdin;
\.


--
-- Name: pl_pipes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('pl_pipes_id_seq', 1, false);


--
-- Data for Name: presentity; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY presentity (id, username, domain, event, etag, expires, received_time, body, sender, priority) FROM stdin;
\.


--
-- Name: presentity_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('presentity_id_seq', 1, false);


--
-- Data for Name: pua; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY pua (id, pres_uri, pres_id, event, expires, desired_expires, flag, etag, tuple_id, watcher_uri, call_id, to_tag, from_tag, cseq, record_route, contact, remote_contact, version, extra_headers) FROM stdin;
\.


--
-- Name: pua_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('pua_id_seq', 1, false);


--
-- Data for Name: purplemap; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY purplemap (id, sip_user, ext_user, ext_prot, ext_pass) FROM stdin;
\.


--
-- Name: purplemap_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('purplemap_id_seq', 1, false);


--
-- Data for Name: re_grp; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY re_grp (id, reg_exp, group_id) FROM stdin;
\.


--
-- Name: re_grp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('re_grp_id_seq', 1, false);


--
-- Data for Name: rls_presentity; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY rls_presentity (id, rlsubs_did, resource_uri, content_type, presence_state, expires, updated, auth_state, reason) FROM stdin;
\.


--
-- Name: rls_presentity_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('rls_presentity_id_seq', 1, false);


--
-- Data for Name: rls_watchers; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY rls_watchers (id, presentity_uri, to_user, to_domain, watcher_username, watcher_domain, event, event_id, to_tag, from_tag, callid, local_cseq, remote_cseq, contact, record_route, expires, status, reason, version, socket_info, local_contact, from_user, from_domain, updated) FROM stdin;
\.


--
-- Name: rls_watchers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('rls_watchers_id_seq', 1, false);


--
-- Data for Name: rtpproxy; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY rtpproxy (id, setid, url, flags, weight, description) FROM stdin;
\.


--
-- Name: rtpproxy_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('rtpproxy_id_seq', 1, false);


--
-- Data for Name: sca_subscriptions; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY sca_subscriptions (id, subscriber, aor, event, expires, state, app_idx, call_id, from_tag, to_tag, record_route, notify_cseq, subscribe_cseq) FROM stdin;
\.


--
-- Name: sca_subscriptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('sca_subscriptions_id_seq', 1, false);


--
-- Data for Name: silo; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY silo (id, src_addr, dst_addr, username, domain, inc_time, exp_time, snd_time, ctype, body, extra_hdrs, callid, status) FROM stdin;
\.


--
-- Name: silo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('silo_id_seq', 1, false);


--
-- Data for Name: sip_trace; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY sip_trace (id, time_stamp, time_us, callid, traced_user, msg, method, status, fromip, toip, fromtag, totag, direction) FROM stdin;
\.


--
-- Name: sip_trace_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('sip_trace_id_seq', 1, false);


--
-- Data for Name: speed_dial; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY speed_dial (id, username, domain, sd_username, sd_domain, new_uri, fname, lname, description) FROM stdin;
\.


--
-- Name: speed_dial_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('speed_dial_id_seq', 1, false);


--
-- Data for Name: subscriber; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY subscriber (id, username, domain, password, email_address, ha1, ha1b, rpid) FROM stdin;
1	2001		2001abc		6da7f911d36166d470ac85600e533de9	6da7f911d36166d470ac85600e533de9	\N
\.


--
-- Name: subscriber_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('subscriber_id_seq', 1, true);


--
-- Data for Name: trusted; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY trusted (id, src_ip, proto, from_pattern, tag) FROM stdin;
\.


--
-- Name: trusted_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('trusted_id_seq', 1, false);


--
-- Data for Name: uacreg; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY uacreg (id, l_uuid, l_username, l_domain, r_username, r_domain, realm, auth_username, auth_password, auth_proxy, expires) FROM stdin;
\.


--
-- Name: uacreg_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('uacreg_id_seq', 1, false);


--
-- Data for Name: uri; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY uri (id, username, domain, uri_user, last_modified) FROM stdin;
\.


--
-- Name: uri_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('uri_id_seq', 1, false);


--
-- Data for Name: userblacklist; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY userblacklist (id, username, domain, prefix, whitelist) FROM stdin;
\.


--
-- Name: userblacklist_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('userblacklist_id_seq', 1, false);


--
-- Data for Name: usr_preferences; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY usr_preferences (id, uuid, username, domain, attribute, type, value, last_modified) FROM stdin;
\.


--
-- Name: usr_preferences_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('usr_preferences_id_seq', 1, false);


--
-- Data for Name: version; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY version (table_name, table_version) FROM stdin;
acc	5
acc_cdrs	2
missed_calls	4
lcr_gw	3
lcr_rule_target	1
lcr_rule	2
domain	2
domain_attrs	1
grp	2
re_grp	1
trusted	5
address	6
aliases	8
location	8
location_attrs	1
silo	8
dbaliases	1
uri	1
speed_dial	2
usr_preferences	2
subscriber	6
pdt	1
dialog	7
dialog_vars	1
dispatcher	4
dialplan	2
presentity	4
active_watchers	11
watchers	3
xcap	4
pua	7
rls_presentity	1
rls_watchers	3
imc_rooms	1
imc_members	1
cpl	1
sip_trace	4
domainpolicy	2
carrierroute	3
carrierfailureroute	2
carrier_name	1
domain_name	1
userblacklist	1
globalblacklist	1
htable	2
purplemap	1
uacreg	1
pl_pipes	1
mtree	1
mtrees	2
sca_subscriptions	1
mohqcalls	1
mohqueues	1
rtpproxy	1
\.


--
-- Data for Name: watchers; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY watchers (id, presentity_uri, watcher_username, watcher_domain, event, status, reason, inserted_time) FROM stdin;
\.


--
-- Name: watchers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('watchers_id_seq', 1, false);


--
-- Data for Name: xcap; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY xcap (id, username, domain, doc, doc_type, etag, source, doc_uri, port) FROM stdin;
\.


--
-- Name: xcap_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('xcap_id_seq', 1, false);


--
-- Name: acc_cdrs_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY acc_cdrs
    ADD CONSTRAINT acc_cdrs_pkey PRIMARY KEY (id);


--
-- Name: acc_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY acc
    ADD CONSTRAINT acc_pkey PRIMARY KEY (id);


--
-- Name: active_watchers_active_watchers_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY active_watchers
    ADD CONSTRAINT active_watchers_active_watchers_idx UNIQUE (callid, to_tag, from_tag);


--
-- Name: active_watchers_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY active_watchers
    ADD CONSTRAINT active_watchers_pkey PRIMARY KEY (id);


--
-- Name: address_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY address
    ADD CONSTRAINT address_pkey PRIMARY KEY (id);


--
-- Name: aliases_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY aliases
    ADD CONSTRAINT aliases_pkey PRIMARY KEY (id);


--
-- Name: aliases_ruid_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY aliases
    ADD CONSTRAINT aliases_ruid_idx UNIQUE (ruid);


--
-- Name: carrier_name_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY carrier_name
    ADD CONSTRAINT carrier_name_pkey PRIMARY KEY (id);


--
-- Name: carrierfailureroute_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY carrierfailureroute
    ADD CONSTRAINT carrierfailureroute_pkey PRIMARY KEY (id);


--
-- Name: carrierroute_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY carrierroute
    ADD CONSTRAINT carrierroute_pkey PRIMARY KEY (id);


--
-- Name: cpl_account_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY cpl
    ADD CONSTRAINT cpl_account_idx UNIQUE (username, domain);


--
-- Name: cpl_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY cpl
    ADD CONSTRAINT cpl_pkey PRIMARY KEY (id);


--
-- Name: dbaliases_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY dbaliases
    ADD CONSTRAINT dbaliases_pkey PRIMARY KEY (id);


--
-- Name: dialog_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY dialog
    ADD CONSTRAINT dialog_pkey PRIMARY KEY (id);


--
-- Name: dialog_vars_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY dialog_vars
    ADD CONSTRAINT dialog_vars_pkey PRIMARY KEY (id);


--
-- Name: dialplan_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY dialplan
    ADD CONSTRAINT dialplan_pkey PRIMARY KEY (id);


--
-- Name: dispatcher_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY dispatcher
    ADD CONSTRAINT dispatcher_pkey PRIMARY KEY (id);


--
-- Name: domain_attrs_domain_attrs_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY domain_attrs
    ADD CONSTRAINT domain_attrs_domain_attrs_idx UNIQUE (did, name, value);


--
-- Name: domain_attrs_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY domain_attrs
    ADD CONSTRAINT domain_attrs_pkey PRIMARY KEY (id);


--
-- Name: domain_domain_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY domain
    ADD CONSTRAINT domain_domain_idx UNIQUE (domain);


--
-- Name: domain_name_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY domain_name
    ADD CONSTRAINT domain_name_pkey PRIMARY KEY (id);


--
-- Name: domain_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY domain
    ADD CONSTRAINT domain_pkey PRIMARY KEY (id);


--
-- Name: domainpolicy_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY domainpolicy
    ADD CONSTRAINT domainpolicy_pkey PRIMARY KEY (id);


--
-- Name: domainpolicy_rav_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY domainpolicy
    ADD CONSTRAINT domainpolicy_rav_idx UNIQUE (rule, att, val);


--
-- Name: globalblacklist_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY globalblacklist
    ADD CONSTRAINT globalblacklist_pkey PRIMARY KEY (id);


--
-- Name: grp_account_group_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY grp
    ADD CONSTRAINT grp_account_group_idx UNIQUE (username, domain, grp);


--
-- Name: grp_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY grp
    ADD CONSTRAINT grp_pkey PRIMARY KEY (id);


--
-- Name: htable_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY htable
    ADD CONSTRAINT htable_pkey PRIMARY KEY (id);


--
-- Name: imc_members_account_room_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY imc_members
    ADD CONSTRAINT imc_members_account_room_idx UNIQUE (username, domain, room);


--
-- Name: imc_members_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY imc_members
    ADD CONSTRAINT imc_members_pkey PRIMARY KEY (id);


--
-- Name: imc_rooms_name_domain_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY imc_rooms
    ADD CONSTRAINT imc_rooms_name_domain_idx UNIQUE (name, domain);


--
-- Name: imc_rooms_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY imc_rooms
    ADD CONSTRAINT imc_rooms_pkey PRIMARY KEY (id);


--
-- Name: lcr_gw_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY lcr_gw
    ADD CONSTRAINT lcr_gw_pkey PRIMARY KEY (id);


--
-- Name: lcr_rule_lcr_id_prefix_from_uri_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY lcr_rule
    ADD CONSTRAINT lcr_rule_lcr_id_prefix_from_uri_idx UNIQUE (lcr_id, prefix, from_uri);


--
-- Name: lcr_rule_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY lcr_rule
    ADD CONSTRAINT lcr_rule_pkey PRIMARY KEY (id);


--
-- Name: lcr_rule_target_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY lcr_rule_target
    ADD CONSTRAINT lcr_rule_target_pkey PRIMARY KEY (id);


--
-- Name: lcr_rule_target_rule_id_gw_id_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY lcr_rule_target
    ADD CONSTRAINT lcr_rule_target_rule_id_gw_id_idx UNIQUE (rule_id, gw_id);


--
-- Name: location_attrs_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY location_attrs
    ADD CONSTRAINT location_attrs_pkey PRIMARY KEY (id);


--
-- Name: location_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY location
    ADD CONSTRAINT location_pkey PRIMARY KEY (id);


--
-- Name: location_ruid_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY location
    ADD CONSTRAINT location_ruid_idx UNIQUE (ruid);


--
-- Name: missed_calls_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY missed_calls
    ADD CONSTRAINT missed_calls_pkey PRIMARY KEY (id);


--
-- Name: mohqcalls_mohqcalls_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY mohqcalls
    ADD CONSTRAINT mohqcalls_mohqcalls_idx UNIQUE (call_id);


--
-- Name: mohqcalls_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY mohqcalls
    ADD CONSTRAINT mohqcalls_pkey PRIMARY KEY (id);


--
-- Name: mohqueues_mohqueue_name_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY mohqueues
    ADD CONSTRAINT mohqueues_mohqueue_name_idx UNIQUE (name);


--
-- Name: mohqueues_mohqueue_uri_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY mohqueues
    ADD CONSTRAINT mohqueues_mohqueue_uri_idx UNIQUE (uri);


--
-- Name: mohqueues_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY mohqueues
    ADD CONSTRAINT mohqueues_pkey PRIMARY KEY (id);


--
-- Name: mtree_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY mtree
    ADD CONSTRAINT mtree_pkey PRIMARY KEY (id);


--
-- Name: mtree_tprefix_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY mtree
    ADD CONSTRAINT mtree_tprefix_idx UNIQUE (tprefix);


--
-- Name: mtrees_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY mtrees
    ADD CONSTRAINT mtrees_pkey PRIMARY KEY (id);


--
-- Name: mtrees_tname_tprefix_tvalue_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY mtrees
    ADD CONSTRAINT mtrees_tname_tprefix_tvalue_idx UNIQUE (tname, tprefix, tvalue);


--
-- Name: pdt_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY pdt
    ADD CONSTRAINT pdt_pkey PRIMARY KEY (id);


--
-- Name: pdt_sdomain_prefix_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY pdt
    ADD CONSTRAINT pdt_sdomain_prefix_idx UNIQUE (sdomain, prefix);


--
-- Name: pl_pipes_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY pl_pipes
    ADD CONSTRAINT pl_pipes_pkey PRIMARY KEY (id);


--
-- Name: presentity_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY presentity
    ADD CONSTRAINT presentity_pkey PRIMARY KEY (id);


--
-- Name: presentity_presentity_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY presentity
    ADD CONSTRAINT presentity_presentity_idx UNIQUE (username, domain, event, etag);


--
-- Name: pua_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY pua
    ADD CONSTRAINT pua_pkey PRIMARY KEY (id);


--
-- Name: pua_pua_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY pua
    ADD CONSTRAINT pua_pua_idx UNIQUE (etag, tuple_id, call_id, from_tag);


--
-- Name: purplemap_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY purplemap
    ADD CONSTRAINT purplemap_pkey PRIMARY KEY (id);


--
-- Name: re_grp_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY re_grp
    ADD CONSTRAINT re_grp_pkey PRIMARY KEY (id);


--
-- Name: rls_presentity_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY rls_presentity
    ADD CONSTRAINT rls_presentity_pkey PRIMARY KEY (id);


--
-- Name: rls_presentity_rls_presentity_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY rls_presentity
    ADD CONSTRAINT rls_presentity_rls_presentity_idx UNIQUE (rlsubs_did, resource_uri);


--
-- Name: rls_watchers_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY rls_watchers
    ADD CONSTRAINT rls_watchers_pkey PRIMARY KEY (id);


--
-- Name: rls_watchers_rls_watcher_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY rls_watchers
    ADD CONSTRAINT rls_watchers_rls_watcher_idx UNIQUE (callid, to_tag, from_tag);


--
-- Name: rtpproxy_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY rtpproxy
    ADD CONSTRAINT rtpproxy_pkey PRIMARY KEY (id);


--
-- Name: sca_subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY sca_subscriptions
    ADD CONSTRAINT sca_subscriptions_pkey PRIMARY KEY (id);


--
-- Name: sca_subscriptions_sca_subscriptions_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY sca_subscriptions
    ADD CONSTRAINT sca_subscriptions_sca_subscriptions_idx UNIQUE (subscriber, call_id, from_tag, to_tag);


--
-- Name: silo_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY silo
    ADD CONSTRAINT silo_pkey PRIMARY KEY (id);


--
-- Name: sip_trace_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY sip_trace
    ADD CONSTRAINT sip_trace_pkey PRIMARY KEY (id);


--
-- Name: speed_dial_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY speed_dial
    ADD CONSTRAINT speed_dial_pkey PRIMARY KEY (id);


--
-- Name: speed_dial_speed_dial_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY speed_dial
    ADD CONSTRAINT speed_dial_speed_dial_idx UNIQUE (username, domain, sd_domain, sd_username);


--
-- Name: subscriber_account_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY subscriber
    ADD CONSTRAINT subscriber_account_idx UNIQUE (username, domain);


--
-- Name: subscriber_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY subscriber
    ADD CONSTRAINT subscriber_pkey PRIMARY KEY (id);


--
-- Name: trusted_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY trusted
    ADD CONSTRAINT trusted_pkey PRIMARY KEY (id);


--
-- Name: uacreg_l_uuid_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY uacreg
    ADD CONSTRAINT uacreg_l_uuid_idx UNIQUE (l_uuid);


--
-- Name: uacreg_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY uacreg
    ADD CONSTRAINT uacreg_pkey PRIMARY KEY (id);


--
-- Name: uri_account_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY uri
    ADD CONSTRAINT uri_account_idx UNIQUE (username, domain, uri_user);


--
-- Name: uri_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY uri
    ADD CONSTRAINT uri_pkey PRIMARY KEY (id);


--
-- Name: userblacklist_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY userblacklist
    ADD CONSTRAINT userblacklist_pkey PRIMARY KEY (id);


--
-- Name: usr_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY usr_preferences
    ADD CONSTRAINT usr_preferences_pkey PRIMARY KEY (id);


--
-- Name: version_table_name_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY version
    ADD CONSTRAINT version_table_name_idx UNIQUE (table_name);


--
-- Name: watchers_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY watchers
    ADD CONSTRAINT watchers_pkey PRIMARY KEY (id);


--
-- Name: watchers_watcher_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY watchers
    ADD CONSTRAINT watchers_watcher_idx UNIQUE (presentity_uri, watcher_username, watcher_domain, event);


--
-- Name: xcap_doc_uri_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY xcap
    ADD CONSTRAINT xcap_doc_uri_idx UNIQUE (doc_uri);


--
-- Name: xcap_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY xcap
    ADD CONSTRAINT xcap_pkey PRIMARY KEY (id);


--
-- Name: acc_callid_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX acc_callid_idx ON acc USING btree (callid);


--
-- Name: acc_cdrs_start_time_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX acc_cdrs_start_time_idx ON acc_cdrs USING btree (start_time);


--
-- Name: active_watchers_active_watchers_expires; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX active_watchers_active_watchers_expires ON active_watchers USING btree (expires);


--
-- Name: active_watchers_active_watchers_pres; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX active_watchers_active_watchers_pres ON active_watchers USING btree (presentity_uri, event);


--
-- Name: active_watchers_updated_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX active_watchers_updated_idx ON active_watchers USING btree (updated);


--
-- Name: active_watchers_updated_winfo_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX active_watchers_updated_winfo_idx ON active_watchers USING btree (updated_winfo, presentity_uri);


--
-- Name: aliases_account_contact_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX aliases_account_contact_idx ON aliases USING btree (username, domain, contact);


--
-- Name: aliases_expires_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX aliases_expires_idx ON aliases USING btree (expires);


--
-- Name: dbaliases_alias_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX dbaliases_alias_idx ON dbaliases USING btree (alias_username, alias_domain);


--
-- Name: dbaliases_alias_user_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX dbaliases_alias_user_idx ON dbaliases USING btree (alias_username);


--
-- Name: dbaliases_target_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX dbaliases_target_idx ON dbaliases USING btree (username, domain);


--
-- Name: dialog_hash_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX dialog_hash_idx ON dialog USING btree (hash_entry, hash_id);


--
-- Name: dialog_vars_hash_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX dialog_vars_hash_idx ON dialog_vars USING btree (hash_entry, hash_id);


--
-- Name: domainpolicy_rule_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX domainpolicy_rule_idx ON domainpolicy USING btree (rule);


--
-- Name: globalblacklist_globalblacklist_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX globalblacklist_globalblacklist_idx ON globalblacklist USING btree (prefix);


--
-- Name: lcr_gw_lcr_id_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX lcr_gw_lcr_id_idx ON lcr_gw USING btree (lcr_id);


--
-- Name: lcr_rule_target_lcr_id_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX lcr_rule_target_lcr_id_idx ON lcr_rule_target USING btree (lcr_id);


--
-- Name: location_account_contact_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX location_account_contact_idx ON location USING btree (username, domain, contact);


--
-- Name: location_attrs_account_record_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX location_attrs_account_record_idx ON location_attrs USING btree (username, domain, ruid);


--
-- Name: location_attrs_last_modified_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX location_attrs_last_modified_idx ON location_attrs USING btree (last_modified);


--
-- Name: location_expires_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX location_expires_idx ON location USING btree (expires);


--
-- Name: missed_calls_callid_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX missed_calls_callid_idx ON missed_calls USING btree (callid);


--
-- Name: presentity_account_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX presentity_account_idx ON presentity USING btree (username, domain, event);


--
-- Name: presentity_presentity_expires; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX presentity_presentity_expires ON presentity USING btree (expires);


--
-- Name: pua_dialog1_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX pua_dialog1_idx ON pua USING btree (pres_id, pres_uri);


--
-- Name: pua_dialog2_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX pua_dialog2_idx ON pua USING btree (call_id, from_tag);


--
-- Name: pua_expires_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX pua_expires_idx ON pua USING btree (expires);


--
-- Name: pua_record_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX pua_record_idx ON pua USING btree (pres_id);


--
-- Name: re_grp_group_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX re_grp_group_idx ON re_grp USING btree (group_id);


--
-- Name: rls_presentity_expires_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX rls_presentity_expires_idx ON rls_presentity USING btree (expires);


--
-- Name: rls_presentity_rlsubs_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX rls_presentity_rlsubs_idx ON rls_presentity USING btree (rlsubs_did);


--
-- Name: rls_presentity_updated_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX rls_presentity_updated_idx ON rls_presentity USING btree (updated);


--
-- Name: rls_watchers_rls_watchers_expires; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX rls_watchers_rls_watchers_expires ON rls_watchers USING btree (expires);


--
-- Name: rls_watchers_rls_watchers_update; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX rls_watchers_rls_watchers_update ON rls_watchers USING btree (watcher_username, watcher_domain, event);


--
-- Name: rls_watchers_updated_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX rls_watchers_updated_idx ON rls_watchers USING btree (updated);


--
-- Name: sca_subscriptions_sca_expires_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX sca_subscriptions_sca_expires_idx ON sca_subscriptions USING btree (expires);


--
-- Name: sca_subscriptions_sca_subscribers_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX sca_subscriptions_sca_subscribers_idx ON sca_subscriptions USING btree (subscriber, event);


--
-- Name: silo_account_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX silo_account_idx ON silo USING btree (username, domain);


--
-- Name: sip_trace_callid_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX sip_trace_callid_idx ON sip_trace USING btree (callid);


--
-- Name: sip_trace_date_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX sip_trace_date_idx ON sip_trace USING btree (time_stamp);


--
-- Name: sip_trace_fromip_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX sip_trace_fromip_idx ON sip_trace USING btree (fromip);


--
-- Name: sip_trace_traced_user_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX sip_trace_traced_user_idx ON sip_trace USING btree (traced_user);


--
-- Name: subscriber_username_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX subscriber_username_idx ON subscriber USING btree (username);


--
-- Name: trusted_peer_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX trusted_peer_idx ON trusted USING btree (src_ip);


--
-- Name: userblacklist_userblacklist_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX userblacklist_userblacklist_idx ON userblacklist USING btree (username, domain, prefix);


--
-- Name: usr_preferences_ua_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX usr_preferences_ua_idx ON usr_preferences USING btree (uuid, attribute);


--
-- Name: usr_preferences_uda_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX usr_preferences_uda_idx ON usr_preferences USING btree (username, domain, attribute);


--
-- Name: xcap_account_doc_type_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX xcap_account_doc_type_idx ON xcap USING btree (username, domain, doc_type);


--
-- Name: xcap_account_doc_type_uri_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX xcap_account_doc_type_uri_idx ON xcap USING btree (username, domain, doc_type, doc_uri);


--
-- Name: xcap_account_doc_uri_idx; Type: INDEX; Schema: public; Owner: kamailio
--

CREATE INDEX xcap_account_doc_uri_idx ON xcap USING btree (username, domain, doc_uri);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: acc; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE acc FROM PUBLIC;
REVOKE ALL ON TABLE acc FROM kamailio;
GRANT ALL ON TABLE acc TO kamailio;
GRANT SELECT ON TABLE acc TO kamailioro;


--
-- Name: acc_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE acc_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE acc_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE acc_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE acc_id_seq TO kamailioro;


--
-- Name: active_watchers; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE active_watchers FROM PUBLIC;
REVOKE ALL ON TABLE active_watchers FROM kamailio;
GRANT ALL ON TABLE active_watchers TO kamailio;
GRANT SELECT ON TABLE active_watchers TO kamailioro;


--
-- Name: active_watchers_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE active_watchers_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE active_watchers_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE active_watchers_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE active_watchers_id_seq TO kamailioro;


--
-- Name: carrier_name; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE carrier_name FROM PUBLIC;
REVOKE ALL ON TABLE carrier_name FROM kamailio;
GRANT ALL ON TABLE carrier_name TO kamailio;
GRANT SELECT ON TABLE carrier_name TO kamailioro;


--
-- Name: carrier_name_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE carrier_name_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE carrier_name_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE carrier_name_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE carrier_name_id_seq TO kamailioro;


--
-- Name: carrierfailureroute; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE carrierfailureroute FROM PUBLIC;
REVOKE ALL ON TABLE carrierfailureroute FROM kamailio;
GRANT ALL ON TABLE carrierfailureroute TO kamailio;
GRANT SELECT ON TABLE carrierfailureroute TO kamailioro;


--
-- Name: carrierfailureroute_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE carrierfailureroute_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE carrierfailureroute_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE carrierfailureroute_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE carrierfailureroute_id_seq TO kamailioro;


--
-- Name: carrierroute; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE carrierroute FROM PUBLIC;
REVOKE ALL ON TABLE carrierroute FROM kamailio;
GRANT ALL ON TABLE carrierroute TO kamailio;
GRANT SELECT ON TABLE carrierroute TO kamailioro;


--
-- Name: carrierroute_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE carrierroute_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE carrierroute_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE carrierroute_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE carrierroute_id_seq TO kamailioro;


--
-- Name: cpl; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE cpl FROM PUBLIC;
REVOKE ALL ON TABLE cpl FROM kamailio;
GRANT ALL ON TABLE cpl TO kamailio;
GRANT SELECT ON TABLE cpl TO kamailioro;


--
-- Name: cpl_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE cpl_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE cpl_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE cpl_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE cpl_id_seq TO kamailioro;


--
-- Name: dbaliases; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE dbaliases FROM PUBLIC;
REVOKE ALL ON TABLE dbaliases FROM kamailio;
GRANT ALL ON TABLE dbaliases TO kamailio;
GRANT SELECT ON TABLE dbaliases TO kamailioro;


--
-- Name: dbaliases_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE dbaliases_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE dbaliases_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE dbaliases_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE dbaliases_id_seq TO kamailioro;


--
-- Name: domain; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE domain FROM PUBLIC;
REVOKE ALL ON TABLE domain FROM kamailio;
GRANT ALL ON TABLE domain TO kamailio;
GRANT SELECT ON TABLE domain TO kamailioro;


--
-- Name: domain_attrs; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE domain_attrs FROM PUBLIC;
REVOKE ALL ON TABLE domain_attrs FROM kamailio;
GRANT ALL ON TABLE domain_attrs TO kamailio;
GRANT SELECT ON TABLE domain_attrs TO kamailioro;


--
-- Name: domain_attrs_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE domain_attrs_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE domain_attrs_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE domain_attrs_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE domain_attrs_id_seq TO kamailioro;


--
-- Name: domain_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE domain_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE domain_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE domain_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE domain_id_seq TO kamailioro;


--
-- Name: domain_name; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE domain_name FROM PUBLIC;
REVOKE ALL ON TABLE domain_name FROM kamailio;
GRANT ALL ON TABLE domain_name TO kamailio;
GRANT SELECT ON TABLE domain_name TO kamailioro;


--
-- Name: domain_name_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE domain_name_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE domain_name_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE domain_name_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE domain_name_id_seq TO kamailioro;


--
-- Name: domainpolicy; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE domainpolicy FROM PUBLIC;
REVOKE ALL ON TABLE domainpolicy FROM kamailio;
GRANT ALL ON TABLE domainpolicy TO kamailio;
GRANT SELECT ON TABLE domainpolicy TO kamailioro;


--
-- Name: domainpolicy_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE domainpolicy_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE domainpolicy_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE domainpolicy_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE domainpolicy_id_seq TO kamailioro;


--
-- Name: globalblacklist; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE globalblacklist FROM PUBLIC;
REVOKE ALL ON TABLE globalblacklist FROM kamailio;
GRANT ALL ON TABLE globalblacklist TO kamailio;
GRANT SELECT ON TABLE globalblacklist TO kamailioro;


--
-- Name: globalblacklist_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE globalblacklist_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE globalblacklist_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE globalblacklist_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE globalblacklist_id_seq TO kamailioro;


--
-- Name: grp; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE grp FROM PUBLIC;
REVOKE ALL ON TABLE grp FROM kamailio;
GRANT ALL ON TABLE grp TO kamailio;
GRANT SELECT ON TABLE grp TO kamailioro;


--
-- Name: grp_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE grp_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE grp_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE grp_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE grp_id_seq TO kamailioro;


--
-- Name: htable; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE htable FROM PUBLIC;
REVOKE ALL ON TABLE htable FROM kamailio;
GRANT ALL ON TABLE htable TO kamailio;
GRANT SELECT ON TABLE htable TO kamailioro;


--
-- Name: htable_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE htable_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE htable_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE htable_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE htable_id_seq TO kamailioro;


--
-- Name: imc_members; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE imc_members FROM PUBLIC;
REVOKE ALL ON TABLE imc_members FROM kamailio;
GRANT ALL ON TABLE imc_members TO kamailio;
GRANT SELECT ON TABLE imc_members TO kamailioro;


--
-- Name: imc_members_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE imc_members_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE imc_members_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE imc_members_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE imc_members_id_seq TO kamailioro;


--
-- Name: imc_rooms; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE imc_rooms FROM PUBLIC;
REVOKE ALL ON TABLE imc_rooms FROM kamailio;
GRANT ALL ON TABLE imc_rooms TO kamailio;
GRANT SELECT ON TABLE imc_rooms TO kamailioro;


--
-- Name: imc_rooms_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE imc_rooms_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE imc_rooms_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE imc_rooms_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE imc_rooms_id_seq TO kamailioro;


--
-- Name: lcr_gw; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE lcr_gw FROM PUBLIC;
REVOKE ALL ON TABLE lcr_gw FROM kamailio;
GRANT ALL ON TABLE lcr_gw TO kamailio;
GRANT SELECT ON TABLE lcr_gw TO kamailioro;


--
-- Name: lcr_gw_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE lcr_gw_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE lcr_gw_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE lcr_gw_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE lcr_gw_id_seq TO kamailioro;


--
-- Name: lcr_rule; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE lcr_rule FROM PUBLIC;
REVOKE ALL ON TABLE lcr_rule FROM kamailio;
GRANT ALL ON TABLE lcr_rule TO kamailio;
GRANT SELECT ON TABLE lcr_rule TO kamailioro;


--
-- Name: lcr_rule_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE lcr_rule_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE lcr_rule_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE lcr_rule_id_seq TO kamailio;


--
-- Name: mohqcalls; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE mohqcalls FROM PUBLIC;
REVOKE ALL ON TABLE mohqcalls FROM kamailio;
GRANT ALL ON TABLE mohqcalls TO kamailio;
GRANT SELECT ON TABLE mohqcalls TO kamailioro;


--
-- Name: mohqcalls_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE mohqcalls_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE mohqcalls_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE mohqcalls_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE mohqcalls_id_seq TO kamailioro;


--
-- Name: mohqueues; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE mohqueues FROM PUBLIC;
REVOKE ALL ON TABLE mohqueues FROM kamailio;
GRANT ALL ON TABLE mohqueues TO kamailio;
GRANT SELECT ON TABLE mohqueues TO kamailioro;


--
-- Name: mohqueues_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE mohqueues_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE mohqueues_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE mohqueues_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE mohqueues_id_seq TO kamailioro;


--
-- Name: mtree; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE mtree FROM PUBLIC;
REVOKE ALL ON TABLE mtree FROM kamailio;
GRANT ALL ON TABLE mtree TO kamailio;
GRANT SELECT ON TABLE mtree TO kamailioro;


--
-- Name: mtree_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE mtree_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE mtree_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE mtree_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE mtree_id_seq TO kamailioro;


--
-- Name: mtrees; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE mtrees FROM PUBLIC;
REVOKE ALL ON TABLE mtrees FROM kamailio;
GRANT ALL ON TABLE mtrees TO kamailio;
GRANT SELECT ON TABLE mtrees TO kamailioro;


--
-- Name: mtrees_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE mtrees_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE mtrees_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE mtrees_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE mtrees_id_seq TO kamailioro;


--
-- Name: pl_pipes; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE pl_pipes FROM PUBLIC;
REVOKE ALL ON TABLE pl_pipes FROM kamailio;
GRANT ALL ON TABLE pl_pipes TO kamailio;
GRANT SELECT ON TABLE pl_pipes TO kamailioro;


--
-- Name: pl_pipes_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE pl_pipes_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE pl_pipes_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE pl_pipes_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE pl_pipes_id_seq TO kamailioro;


--
-- Name: presentity; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE presentity FROM PUBLIC;
REVOKE ALL ON TABLE presentity FROM kamailio;
GRANT ALL ON TABLE presentity TO kamailio;


--
-- Name: presentity_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE presentity_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE presentity_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE presentity_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE presentity_id_seq TO kamailioro;


--
-- Name: pua; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE pua FROM PUBLIC;
REVOKE ALL ON TABLE pua FROM kamailio;
GRANT ALL ON TABLE pua TO kamailio;
GRANT SELECT ON TABLE pua TO kamailioro;


--
-- Name: pua_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE pua_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE pua_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE pua_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE pua_id_seq TO kamailioro;


--
-- Name: purplemap; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE purplemap FROM PUBLIC;
REVOKE ALL ON TABLE purplemap FROM kamailio;
GRANT ALL ON TABLE purplemap TO kamailio;
GRANT SELECT ON TABLE purplemap TO kamailioro;


--
-- Name: purplemap_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE purplemap_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE purplemap_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE purplemap_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE purplemap_id_seq TO kamailioro;


--
-- Name: rls_presentity; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE rls_presentity FROM PUBLIC;
REVOKE ALL ON TABLE rls_presentity FROM kamailio;
GRANT ALL ON TABLE rls_presentity TO kamailio;
GRANT SELECT ON TABLE rls_presentity TO kamailioro;


--
-- Name: rls_presentity_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE rls_presentity_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE rls_presentity_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE rls_presentity_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE rls_presentity_id_seq TO kamailioro;


--
-- Name: rls_watchers; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE rls_watchers FROM PUBLIC;
REVOKE ALL ON TABLE rls_watchers FROM kamailio;
GRANT ALL ON TABLE rls_watchers TO kamailio;
GRANT SELECT ON TABLE rls_watchers TO kamailioro;


--
-- Name: rls_watchers_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE rls_watchers_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE rls_watchers_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE rls_watchers_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE rls_watchers_id_seq TO kamailioro;


--
-- Name: rtpproxy; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE rtpproxy FROM PUBLIC;
REVOKE ALL ON TABLE rtpproxy FROM kamailio;
GRANT ALL ON TABLE rtpproxy TO kamailio;
GRANT SELECT ON TABLE rtpproxy TO kamailioro;


--
-- Name: rtpproxy_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE rtpproxy_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE rtpproxy_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE rtpproxy_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE rtpproxy_id_seq TO kamailioro;


--
-- Name: sca_subscriptions; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE sca_subscriptions FROM PUBLIC;
REVOKE ALL ON TABLE sca_subscriptions FROM kamailio;
GRANT ALL ON TABLE sca_subscriptions TO kamailio;
GRANT SELECT ON TABLE sca_subscriptions TO kamailioro;


--
-- Name: sca_subscriptions_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE sca_subscriptions_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE sca_subscriptions_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE sca_subscriptions_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE sca_subscriptions_id_seq TO kamailioro;


--
-- Name: sip_trace; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE sip_trace FROM PUBLIC;
REVOKE ALL ON TABLE sip_trace FROM kamailio;
GRANT ALL ON TABLE sip_trace TO kamailio;
GRANT SELECT ON TABLE sip_trace TO kamailioro;


--
-- Name: sip_trace_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE sip_trace_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE sip_trace_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE sip_trace_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE sip_trace_id_seq TO kamailioro;


--
-- Name: speed_dial; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE speed_dial FROM PUBLIC;
REVOKE ALL ON TABLE speed_dial FROM kamailio;
GRANT ALL ON TABLE speed_dial TO kamailio;
GRANT SELECT ON TABLE speed_dial TO kamailioro;


--
-- Name: speed_dial_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE speed_dial_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE speed_dial_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE speed_dial_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE speed_dial_id_seq TO kamailioro;


--
-- Name: uacreg; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE uacreg FROM PUBLIC;
REVOKE ALL ON TABLE uacreg FROM kamailio;
GRANT ALL ON TABLE uacreg TO kamailio;
GRANT SELECT ON TABLE uacreg TO kamailioro;


--
-- Name: uacreg_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE uacreg_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE uacreg_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE uacreg_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE uacreg_id_seq TO kamailioro;


--
-- Name: uri; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE uri FROM PUBLIC;
REVOKE ALL ON TABLE uri FROM kamailio;
GRANT ALL ON TABLE uri TO kamailio;
GRANT SELECT ON TABLE uri TO kamailioro;


--
-- Name: uri_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE uri_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE uri_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE uri_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE uri_id_seq TO kamailioro;


--
-- Name: userblacklist; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE userblacklist FROM PUBLIC;
REVOKE ALL ON TABLE userblacklist FROM kamailio;
GRANT ALL ON TABLE userblacklist TO kamailio;
GRANT SELECT ON TABLE userblacklist TO kamailioro;


--
-- Name: userblacklist_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE userblacklist_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE userblacklist_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE userblacklist_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE userblacklist_id_seq TO kamailioro;


--
-- Name: version; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE version FROM PUBLIC;
REVOKE ALL ON TABLE version FROM kamailio;
GRANT ALL ON TABLE version TO kamailio;
GRANT SELECT ON TABLE version TO kamailioro;


--
-- Name: watchers; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE watchers FROM PUBLIC;
REVOKE ALL ON TABLE watchers FROM kamailio;
GRANT ALL ON TABLE watchers TO kamailio;
GRANT SELECT ON TABLE watchers TO kamailioro;


--
-- Name: watchers_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE watchers_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE watchers_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE watchers_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE watchers_id_seq TO kamailioro;


--
-- Name: xcap; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE xcap FROM PUBLIC;
REVOKE ALL ON TABLE xcap FROM kamailio;
GRANT ALL ON TABLE xcap TO kamailio;
GRANT SELECT ON TABLE xcap TO kamailioro;


--
-- Name: xcap_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE xcap_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE xcap_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE xcap_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE xcap_id_seq TO kamailioro;


--
-- PostgreSQL database dump complete
--

