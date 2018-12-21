--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.10
-- Dumped by pg_dump version 9.6.10

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
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


--
-- Name: plpythonu; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpythonu WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpythonu; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpythonu IS 'PL/PythonU untrusted procedural language';


--
-- Name: concat(text, text); Type: FUNCTION; Schema: public; Owner: omnileads
--

CREATE FUNCTION public.concat(text, text) RETURNS text
    LANGUAGE sql
    AS $_$SELECT $1 || $2;$_$;


ALTER FUNCTION public.concat(text, text) OWNER TO omnileads;

--
-- Name: rand(); Type: FUNCTION; Schema: public; Owner: omnileads
--

CREATE FUNCTION public.rand() RETURNS double precision
    LANGUAGE sql
    AS $$SELECT random();$$;


ALTER FUNCTION public.rand() OWNER TO omnileads;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: acc; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.acc (
    id integer NOT NULL,
    method character varying(16) DEFAULT ''::character varying NOT NULL,
    from_tag character varying(64) DEFAULT ''::character varying NOT NULL,
    to_tag character varying(64) DEFAULT ''::character varying NOT NULL,
    callid character varying(255) DEFAULT ''::character varying NOT NULL,
    sip_code character varying(3) DEFAULT ''::character varying NOT NULL,
    sip_reason character varying(128) DEFAULT ''::character varying NOT NULL,
    "time" timestamp without time zone NOT NULL
);


ALTER TABLE public.acc OWNER TO omnileads;

--
-- Name: acc_cdrs; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.acc_cdrs (
    id integer NOT NULL,
    start_time timestamp without time zone DEFAULT '2000-01-01 00:00:00'::timestamp without time zone NOT NULL,
    end_time timestamp without time zone DEFAULT '2000-01-01 00:00:00'::timestamp without time zone NOT NULL,
    duration real DEFAULT 0 NOT NULL
);


ALTER TABLE public.acc_cdrs OWNER TO omnileads;

--
-- Name: acc_cdrs_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.acc_cdrs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.acc_cdrs_id_seq OWNER TO omnileads;

--
-- Name: acc_cdrs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.acc_cdrs_id_seq OWNED BY public.acc_cdrs.id;


--
-- Name: acc_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.acc_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.acc_id_seq OWNER TO omnileads;

--
-- Name: acc_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.acc_id_seq OWNED BY public.acc.id;


--
-- Name: active_watchers; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.active_watchers (
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
    updated_winfo integer NOT NULL,
    flags integer DEFAULT 0 NOT NULL,
    user_agent character varying(255) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.active_watchers OWNER TO omnileads;

--
-- Name: active_watchers_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.active_watchers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.active_watchers_id_seq OWNER TO omnileads;

--
-- Name: active_watchers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.active_watchers_id_seq OWNED BY public.active_watchers.id;


--
-- Name: address; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.address (
    id integer NOT NULL,
    grp integer DEFAULT 1 NOT NULL,
    ip_addr character varying(50) NOT NULL,
    mask integer DEFAULT 32 NOT NULL,
    port smallint DEFAULT 0 NOT NULL,
    tag character varying(64)
);


ALTER TABLE public.address OWNER TO omnileads;

--
-- Name: address_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.address_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.address_id_seq OWNER TO omnileads;

--
-- Name: address_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.address_id_seq OWNED BY public.address.id;


--
-- Name: aliases; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.aliases (
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
    last_modified timestamp without time zone DEFAULT '2000-01-01 00:00:01'::timestamp without time zone NOT NULL,
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


ALTER TABLE public.aliases OWNER TO omnileads;

--
-- Name: aliases_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.aliases_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.aliases_id_seq OWNER TO omnileads;

--
-- Name: aliases_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.aliases_id_seq OWNED BY public.aliases.id;


--
-- Name: carrier_name; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.carrier_name (
    id integer NOT NULL,
    carrier character varying(64) DEFAULT NULL::character varying
);


ALTER TABLE public.carrier_name OWNER TO omnileads;

--
-- Name: carrier_name_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.carrier_name_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.carrier_name_id_seq OWNER TO omnileads;

--
-- Name: carrier_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.carrier_name_id_seq OWNED BY public.carrier_name.id;


--
-- Name: carrierfailureroute; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.carrierfailureroute (
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


ALTER TABLE public.carrierfailureroute OWNER TO omnileads;

--
-- Name: carrierfailureroute_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.carrierfailureroute_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.carrierfailureroute_id_seq OWNER TO omnileads;

--
-- Name: carrierfailureroute_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.carrierfailureroute_id_seq OWNED BY public.carrierfailureroute.id;


--
-- Name: carrierroute; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.carrierroute (
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


ALTER TABLE public.carrierroute OWNER TO omnileads;

--
-- Name: carrierroute_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.carrierroute_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.carrierroute_id_seq OWNER TO omnileads;

--
-- Name: carrierroute_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.carrierroute_id_seq OWNED BY public.carrierroute.id;


--
-- Name: cpl; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.cpl (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    domain character varying(64) DEFAULT ''::character varying NOT NULL,
    cpl_xml text,
    cpl_bin text
);


ALTER TABLE public.cpl OWNER TO omnileads;

--
-- Name: cpl_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.cpl_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cpl_id_seq OWNER TO omnileads;

--
-- Name: cpl_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.cpl_id_seq OWNED BY public.cpl.id;


--
-- Name: dbaliases; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.dbaliases (
    id integer NOT NULL,
    alias_username character varying(64) DEFAULT ''::character varying NOT NULL,
    alias_domain character varying(64) DEFAULT ''::character varying NOT NULL,
    username character varying(64) DEFAULT ''::character varying NOT NULL,
    domain character varying(64) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.dbaliases OWNER TO omnileads;

--
-- Name: dbaliases_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.dbaliases_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dbaliases_id_seq OWNER TO omnileads;

--
-- Name: dbaliases_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.dbaliases_id_seq OWNED BY public.dbaliases.id;


--
-- Name: dialog; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.dialog (
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


ALTER TABLE public.dialog OWNER TO omnileads;

--
-- Name: dialog_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.dialog_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dialog_id_seq OWNER TO omnileads;

--
-- Name: dialog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.dialog_id_seq OWNED BY public.dialog.id;


--
-- Name: dialog_vars; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.dialog_vars (
    id integer NOT NULL,
    hash_entry integer NOT NULL,
    hash_id integer NOT NULL,
    dialog_key character varying(128) NOT NULL,
    dialog_value character varying(512) NOT NULL
);


ALTER TABLE public.dialog_vars OWNER TO omnileads;

--
-- Name: dialog_vars_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.dialog_vars_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dialog_vars_id_seq OWNER TO omnileads;

--
-- Name: dialog_vars_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.dialog_vars_id_seq OWNED BY public.dialog_vars.id;


--
-- Name: dialplan; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.dialplan (
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


ALTER TABLE public.dialplan OWNER TO omnileads;

--
-- Name: dialplan_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.dialplan_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dialplan_id_seq OWNER TO omnileads;

--
-- Name: dialplan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.dialplan_id_seq OWNED BY public.dialplan.id;


--
-- Name: dispatcher; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.dispatcher (
    id integer NOT NULL,
    setid integer DEFAULT 0 NOT NULL,
    destination character varying(192) DEFAULT ''::character varying NOT NULL,
    flags integer DEFAULT 0 NOT NULL,
    priority integer DEFAULT 0 NOT NULL,
    attrs character varying(128) DEFAULT ''::character varying NOT NULL,
    description character varying(64) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.dispatcher OWNER TO omnileads;

--
-- Name: dispatcher_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.dispatcher_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dispatcher_id_seq OWNER TO omnileads;

--
-- Name: dispatcher_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.dispatcher_id_seq OWNED BY public.dispatcher.id;


--
-- Name: domain; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.domain (
    id integer NOT NULL,
    domain character varying(64) NOT NULL,
    did character varying(64) DEFAULT NULL::character varying,
    last_modified timestamp without time zone DEFAULT '2000-01-01 00:00:01'::timestamp without time zone NOT NULL
);


ALTER TABLE public.domain OWNER TO omnileads;

--
-- Name: domain_attrs; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.domain_attrs (
    id integer NOT NULL,
    did character varying(64) NOT NULL,
    name character varying(32) NOT NULL,
    type integer NOT NULL,
    value character varying(255) NOT NULL,
    last_modified timestamp without time zone DEFAULT '2000-01-01 00:00:01'::timestamp without time zone NOT NULL
);


ALTER TABLE public.domain_attrs OWNER TO omnileads;

--
-- Name: domain_attrs_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.domain_attrs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.domain_attrs_id_seq OWNER TO omnileads;

--
-- Name: domain_attrs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.domain_attrs_id_seq OWNED BY public.domain_attrs.id;


--
-- Name: domain_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.domain_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.domain_id_seq OWNER TO omnileads;

--
-- Name: domain_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.domain_id_seq OWNED BY public.domain.id;


--
-- Name: domain_name; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.domain_name (
    id integer NOT NULL,
    domain character varying(64) DEFAULT NULL::character varying
);


ALTER TABLE public.domain_name OWNER TO omnileads;

--
-- Name: domain_name_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.domain_name_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.domain_name_id_seq OWNER TO omnileads;

--
-- Name: domain_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.domain_name_id_seq OWNED BY public.domain_name.id;


--
-- Name: domainpolicy; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.domainpolicy (
    id integer NOT NULL,
    rule character varying(255) NOT NULL,
    type character varying(255) NOT NULL,
    att character varying(255),
    val character varying(128),
    description character varying(255) NOT NULL
);


ALTER TABLE public.domainpolicy OWNER TO omnileads;

--
-- Name: domainpolicy_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.domainpolicy_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.domainpolicy_id_seq OWNER TO omnileads;

--
-- Name: domainpolicy_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.domainpolicy_id_seq OWNED BY public.domainpolicy.id;


--
-- Name: dr_gateways; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.dr_gateways (
    gwid integer NOT NULL,
    type integer DEFAULT 0 NOT NULL,
    address character varying(128) NOT NULL,
    strip integer DEFAULT 0 NOT NULL,
    pri_prefix character varying(64) DEFAULT NULL::character varying,
    attrs character varying(255) DEFAULT NULL::character varying,
    description character varying(128) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.dr_gateways OWNER TO omnileads;

--
-- Name: dr_gateways_gwid_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.dr_gateways_gwid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dr_gateways_gwid_seq OWNER TO omnileads;

--
-- Name: dr_gateways_gwid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.dr_gateways_gwid_seq OWNED BY public.dr_gateways.gwid;


--
-- Name: dr_groups; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.dr_groups (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    domain character varying(128) DEFAULT ''::character varying NOT NULL,
    groupid integer DEFAULT 0 NOT NULL,
    description character varying(128) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.dr_groups OWNER TO omnileads;

--
-- Name: dr_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.dr_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dr_groups_id_seq OWNER TO omnileads;

--
-- Name: dr_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.dr_groups_id_seq OWNED BY public.dr_groups.id;


--
-- Name: dr_gw_lists; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.dr_gw_lists (
    id integer NOT NULL,
    gwlist character varying(255) NOT NULL,
    description character varying(128) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.dr_gw_lists OWNER TO omnileads;

--
-- Name: dr_gw_lists_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.dr_gw_lists_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dr_gw_lists_id_seq OWNER TO omnileads;

--
-- Name: dr_gw_lists_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.dr_gw_lists_id_seq OWNED BY public.dr_gw_lists.id;


--
-- Name: dr_rules; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.dr_rules (
    ruleid integer NOT NULL,
    groupid character varying(255) NOT NULL,
    prefix character varying(64) NOT NULL,
    timerec character varying(255) NOT NULL,
    priority integer DEFAULT 0 NOT NULL,
    routeid character varying(64) NOT NULL,
    gwlist character varying(255) NOT NULL,
    description character varying(128) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.dr_rules OWNER TO omnileads;

--
-- Name: dr_rules_ruleid_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.dr_rules_ruleid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dr_rules_ruleid_seq OWNER TO omnileads;

--
-- Name: dr_rules_ruleid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.dr_rules_ruleid_seq OWNED BY public.dr_rules.ruleid;


--
-- Name: globalblacklist; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.globalblacklist (
    id integer NOT NULL,
    prefix character varying(64) DEFAULT ''::character varying NOT NULL,
    whitelist smallint DEFAULT 0 NOT NULL,
    description character varying(255) DEFAULT NULL::character varying
);


ALTER TABLE public.globalblacklist OWNER TO omnileads;

--
-- Name: globalblacklist_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.globalblacklist_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.globalblacklist_id_seq OWNER TO omnileads;

--
-- Name: globalblacklist_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.globalblacklist_id_seq OWNED BY public.globalblacklist.id;


--
-- Name: grp; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.grp (
    id integer NOT NULL,
    username character varying(64) DEFAULT ''::character varying NOT NULL,
    domain character varying(64) DEFAULT ''::character varying NOT NULL,
    grp character varying(64) DEFAULT ''::character varying NOT NULL,
    last_modified timestamp without time zone DEFAULT '2000-01-01 00:00:01'::timestamp without time zone NOT NULL
);


ALTER TABLE public.grp OWNER TO omnileads;

--
-- Name: grp_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.grp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.grp_id_seq OWNER TO omnileads;

--
-- Name: grp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.grp_id_seq OWNED BY public.grp.id;


--
-- Name: htable; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.htable (
    id integer NOT NULL,
    key_name character varying(64) DEFAULT ''::character varying NOT NULL,
    key_type integer DEFAULT 0 NOT NULL,
    value_type integer DEFAULT 0 NOT NULL,
    key_value character varying(128) DEFAULT ''::character varying NOT NULL,
    expires integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.htable OWNER TO omnileads;

--
-- Name: htable_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.htable_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.htable_id_seq OWNER TO omnileads;

--
-- Name: htable_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.htable_id_seq OWNED BY public.htable.id;


--
-- Name: imc_members; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.imc_members (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    domain character varying(64) NOT NULL,
    room character varying(64) NOT NULL,
    flag integer NOT NULL
);


ALTER TABLE public.imc_members OWNER TO omnileads;

--
-- Name: imc_members_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.imc_members_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.imc_members_id_seq OWNER TO omnileads;

--
-- Name: imc_members_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.imc_members_id_seq OWNED BY public.imc_members.id;


--
-- Name: imc_rooms; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.imc_rooms (
    id integer NOT NULL,
    name character varying(64) NOT NULL,
    domain character varying(64) NOT NULL,
    flag integer NOT NULL
);


ALTER TABLE public.imc_rooms OWNER TO omnileads;

--
-- Name: imc_rooms_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.imc_rooms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.imc_rooms_id_seq OWNER TO omnileads;

--
-- Name: imc_rooms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.imc_rooms_id_seq OWNED BY public.imc_rooms.id;


--
-- Name: lcr_gw; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.lcr_gw (
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


ALTER TABLE public.lcr_gw OWNER TO omnileads;

--
-- Name: lcr_gw_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.lcr_gw_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lcr_gw_id_seq OWNER TO omnileads;

--
-- Name: lcr_gw_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.lcr_gw_id_seq OWNED BY public.lcr_gw.id;


--
-- Name: lcr_rule; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.lcr_rule (
    id integer NOT NULL,
    lcr_id smallint NOT NULL,
    prefix character varying(16) DEFAULT NULL::character varying,
    from_uri character varying(64) DEFAULT NULL::character varying,
    request_uri character varying(64) DEFAULT NULL::character varying,
    stopper integer DEFAULT 0 NOT NULL,
    enabled integer DEFAULT 1 NOT NULL
);


ALTER TABLE public.lcr_rule OWNER TO omnileads;

--
-- Name: lcr_rule_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.lcr_rule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lcr_rule_id_seq OWNER TO omnileads;

--
-- Name: lcr_rule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.lcr_rule_id_seq OWNED BY public.lcr_rule.id;


--
-- Name: lcr_rule_target; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.lcr_rule_target (
    id integer NOT NULL,
    lcr_id smallint NOT NULL,
    rule_id integer NOT NULL,
    gw_id integer NOT NULL,
    priority smallint NOT NULL,
    weight integer DEFAULT 1 NOT NULL
);


ALTER TABLE public.lcr_rule_target OWNER TO omnileads;

--
-- Name: lcr_rule_target_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.lcr_rule_target_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lcr_rule_target_id_seq OWNER TO omnileads;

--
-- Name: lcr_rule_target_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.lcr_rule_target_id_seq OWNED BY public.lcr_rule_target.id;


--
-- Name: location; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.location (
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
    last_modified timestamp without time zone DEFAULT '2000-01-01 00:00:01'::timestamp without time zone NOT NULL,
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


ALTER TABLE public.location OWNER TO omnileads;

--
-- Name: location_attrs; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.location_attrs (
    id integer NOT NULL,
    ruid character varying(64) DEFAULT ''::character varying NOT NULL,
    username character varying(64) DEFAULT ''::character varying NOT NULL,
    domain character varying(64) DEFAULT NULL::character varying,
    aname character varying(64) DEFAULT ''::character varying NOT NULL,
    atype integer DEFAULT 0 NOT NULL,
    avalue character varying(255) DEFAULT ''::character varying NOT NULL,
    last_modified timestamp without time zone DEFAULT '2000-01-01 00:00:01'::timestamp without time zone NOT NULL
);


ALTER TABLE public.location_attrs OWNER TO omnileads;

--
-- Name: location_attrs_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.location_attrs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.location_attrs_id_seq OWNER TO omnileads;

--
-- Name: location_attrs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.location_attrs_id_seq OWNED BY public.location_attrs.id;


--
-- Name: location_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.location_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.location_id_seq OWNER TO omnileads;

--
-- Name: location_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.location_id_seq OWNED BY public.location.id;


--
-- Name: missed_calls; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.missed_calls (
    id integer NOT NULL,
    method character varying(16) DEFAULT ''::character varying NOT NULL,
    from_tag character varying(64) DEFAULT ''::character varying NOT NULL,
    to_tag character varying(64) DEFAULT ''::character varying NOT NULL,
    callid character varying(255) DEFAULT ''::character varying NOT NULL,
    sip_code character varying(3) DEFAULT ''::character varying NOT NULL,
    sip_reason character varying(128) DEFAULT ''::character varying NOT NULL,
    "time" timestamp without time zone NOT NULL
);


ALTER TABLE public.missed_calls OWNER TO omnileads;

--
-- Name: missed_calls_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.missed_calls_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.missed_calls_id_seq OWNER TO omnileads;

--
-- Name: missed_calls_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.missed_calls_id_seq OWNED BY public.missed_calls.id;


--
-- Name: mohqcalls; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.mohqcalls (
    id integer NOT NULL,
    mohq_id integer NOT NULL,
    call_id character varying(100) NOT NULL,
    call_status integer NOT NULL,
    call_from character varying(100) NOT NULL,
    call_contact character varying(100),
    call_time timestamp without time zone NOT NULL
);


ALTER TABLE public.mohqcalls OWNER TO omnileads;

--
-- Name: mohqcalls_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.mohqcalls_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mohqcalls_id_seq OWNER TO omnileads;

--
-- Name: mohqcalls_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.mohqcalls_id_seq OWNED BY public.mohqcalls.id;


--
-- Name: mohqueues; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.mohqueues (
    id integer NOT NULL,
    name character varying(25) NOT NULL,
    uri character varying(100) NOT NULL,
    mohdir character varying(100),
    mohfile character varying(100) NOT NULL,
    debug integer NOT NULL
);


ALTER TABLE public.mohqueues OWNER TO omnileads;

--
-- Name: mohqueues_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.mohqueues_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mohqueues_id_seq OWNER TO omnileads;

--
-- Name: mohqueues_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.mohqueues_id_seq OWNED BY public.mohqueues.id;


--
-- Name: mtree; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.mtree (
    id integer NOT NULL,
    tprefix character varying(32) DEFAULT ''::character varying NOT NULL,
    tvalue character varying(128) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.mtree OWNER TO omnileads;

--
-- Name: mtree_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.mtree_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mtree_id_seq OWNER TO omnileads;

--
-- Name: mtree_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.mtree_id_seq OWNED BY public.mtree.id;


--
-- Name: mtrees; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.mtrees (
    id integer NOT NULL,
    tname character varying(128) DEFAULT ''::character varying NOT NULL,
    tprefix character varying(32) DEFAULT ''::character varying NOT NULL,
    tvalue character varying(128) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.mtrees OWNER TO omnileads;

--
-- Name: mtrees_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.mtrees_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mtrees_id_seq OWNER TO omnileads;

--
-- Name: mtrees_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.mtrees_id_seq OWNED BY public.mtrees.id;


--
-- Name: pdt; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.pdt (
    id integer NOT NULL,
    sdomain character varying(128) NOT NULL,
    prefix character varying(32) NOT NULL,
    domain character varying(128) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.pdt OWNER TO omnileads;

--
-- Name: pdt_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.pdt_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pdt_id_seq OWNER TO omnileads;

--
-- Name: pdt_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.pdt_id_seq OWNED BY public.pdt.id;


--
-- Name: pl_pipes; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.pl_pipes (
    id integer NOT NULL,
    pipeid character varying(64) DEFAULT ''::character varying NOT NULL,
    algorithm character varying(32) DEFAULT ''::character varying NOT NULL,
    plimit integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.pl_pipes OWNER TO omnileads;

--
-- Name: pl_pipes_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.pl_pipes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pl_pipes_id_seq OWNER TO omnileads;

--
-- Name: pl_pipes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.pl_pipes_id_seq OWNED BY public.pl_pipes.id;


--
-- Name: presentity; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.presentity (
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


ALTER TABLE public.presentity OWNER TO omnileads;

--
-- Name: presentity_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.presentity_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.presentity_id_seq OWNER TO omnileads;

--
-- Name: presentity_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.presentity_id_seq OWNED BY public.presentity.id;


--
-- Name: pua; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.pua (
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


ALTER TABLE public.pua OWNER TO omnileads;

--
-- Name: pua_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.pua_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pua_id_seq OWNER TO omnileads;

--
-- Name: pua_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.pua_id_seq OWNED BY public.pua.id;


--
-- Name: purplemap; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.purplemap (
    id integer NOT NULL,
    sip_user character varying(128) NOT NULL,
    ext_user character varying(128) NOT NULL,
    ext_prot character varying(16) NOT NULL,
    ext_pass character varying(64)
);


ALTER TABLE public.purplemap OWNER TO omnileads;

--
-- Name: purplemap_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.purplemap_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.purplemap_id_seq OWNER TO omnileads;

--
-- Name: purplemap_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.purplemap_id_seq OWNED BY public.purplemap.id;


--
-- Name: re_grp; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.re_grp (
    id integer NOT NULL,
    reg_exp character varying(128) DEFAULT ''::character varying NOT NULL,
    group_id integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.re_grp OWNER TO omnileads;

--
-- Name: re_grp_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.re_grp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.re_grp_id_seq OWNER TO omnileads;

--
-- Name: re_grp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.re_grp_id_seq OWNED BY public.re_grp.id;


--
-- Name: rls_presentity; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.rls_presentity (
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


ALTER TABLE public.rls_presentity OWNER TO omnileads;

--
-- Name: rls_presentity_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.rls_presentity_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rls_presentity_id_seq OWNER TO omnileads;

--
-- Name: rls_presentity_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.rls_presentity_id_seq OWNED BY public.rls_presentity.id;


--
-- Name: rls_watchers; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.rls_watchers (
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


ALTER TABLE public.rls_watchers OWNER TO omnileads;

--
-- Name: rls_watchers_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.rls_watchers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rls_watchers_id_seq OWNER TO omnileads;

--
-- Name: rls_watchers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.rls_watchers_id_seq OWNED BY public.rls_watchers.id;


--
-- Name: rtpproxy; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.rtpproxy (
    id integer NOT NULL,
    setid character varying(32) DEFAULT 0 NOT NULL,
    url character varying(64) DEFAULT ''::character varying NOT NULL,
    flags integer DEFAULT 0 NOT NULL,
    weight integer DEFAULT 1 NOT NULL,
    description character varying(64) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.rtpproxy OWNER TO omnileads;

--
-- Name: rtpproxy_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.rtpproxy_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rtpproxy_id_seq OWNER TO omnileads;

--
-- Name: rtpproxy_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.rtpproxy_id_seq OWNED BY public.rtpproxy.id;


--
-- Name: sca_subscriptions; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.sca_subscriptions (
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


ALTER TABLE public.sca_subscriptions OWNER TO omnileads;

--
-- Name: sca_subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.sca_subscriptions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sca_subscriptions_id_seq OWNER TO omnileads;

--
-- Name: sca_subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.sca_subscriptions_id_seq OWNED BY public.sca_subscriptions.id;


--
-- Name: silo; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.silo (
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


ALTER TABLE public.silo OWNER TO omnileads;

--
-- Name: silo_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.silo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.silo_id_seq OWNER TO omnileads;

--
-- Name: silo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.silo_id_seq OWNED BY public.silo.id;


--
-- Name: sip_trace; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.sip_trace (
    id integer NOT NULL,
    time_stamp timestamp without time zone DEFAULT '2000-01-01 00:00:01'::timestamp without time zone NOT NULL,
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


ALTER TABLE public.sip_trace OWNER TO omnileads;

--
-- Name: sip_trace_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.sip_trace_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sip_trace_id_seq OWNER TO omnileads;

--
-- Name: sip_trace_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.sip_trace_id_seq OWNED BY public.sip_trace.id;


--
-- Name: speed_dial; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.speed_dial (
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


ALTER TABLE public.speed_dial OWNER TO omnileads;

--
-- Name: speed_dial_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.speed_dial_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.speed_dial_id_seq OWNER TO omnileads;

--
-- Name: speed_dial_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.speed_dial_id_seq OWNED BY public.speed_dial.id;


--
-- Name: subscriber; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.subscriber (
    id integer NOT NULL,
    username character varying(64) DEFAULT ''::character varying NOT NULL,
    domain character varying(64) DEFAULT ''::character varying NOT NULL,
    password character varying(25) DEFAULT ''::character varying NOT NULL,
    email_address character varying(64) DEFAULT ''::character varying NOT NULL,
    ha1 character varying(64) DEFAULT ''::character varying NOT NULL,
    ha1b character varying(64) DEFAULT ''::character varying NOT NULL,
    rpid character varying(64) DEFAULT NULL::character varying
);


ALTER TABLE public.subscriber OWNER TO omnileads;

--
-- Name: subscriber_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.subscriber_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.subscriber_id_seq OWNER TO omnileads;

--
-- Name: subscriber_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.subscriber_id_seq OWNED BY public.subscriber.id;


--
-- Name: topos_d; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.topos_d (
    id integer NOT NULL,
    rectime timestamp without time zone NOT NULL,
    s_method character varying(64) DEFAULT ''::character varying NOT NULL,
    s_cseq character varying(64) DEFAULT ''::character varying NOT NULL,
    a_callid character varying(255) DEFAULT ''::character varying NOT NULL,
    a_uuid character varying(255) DEFAULT ''::character varying NOT NULL,
    b_uuid character varying(255) DEFAULT ''::character varying NOT NULL,
    a_contact character varying(128) DEFAULT ''::character varying NOT NULL,
    b_contact character varying(128) DEFAULT ''::character varying NOT NULL,
    as_contact character varying(128) DEFAULT ''::character varying NOT NULL,
    bs_contact character varying(128) DEFAULT ''::character varying NOT NULL,
    a_tag character varying(255) DEFAULT ''::character varying NOT NULL,
    b_tag character varying(255) DEFAULT ''::character varying NOT NULL,
    a_rr text,
    b_rr text,
    s_rr text,
    iflags integer DEFAULT 0 NOT NULL,
    a_uri character varying(128) DEFAULT ''::character varying NOT NULL,
    b_uri character varying(128) DEFAULT ''::character varying NOT NULL,
    r_uri character varying(128) DEFAULT ''::character varying NOT NULL,
    a_srcaddr character varying(128) DEFAULT ''::character varying NOT NULL,
    b_srcaddr character varying(128) DEFAULT ''::character varying NOT NULL,
    a_socket character varying(128) DEFAULT ''::character varying NOT NULL,
    b_socket character varying(128) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.topos_d OWNER TO omnileads;

--
-- Name: topos_d_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.topos_d_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.topos_d_id_seq OWNER TO omnileads;

--
-- Name: topos_d_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.topos_d_id_seq OWNED BY public.topos_d.id;


--
-- Name: topos_t; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.topos_t (
    id integer NOT NULL,
    rectime timestamp without time zone NOT NULL,
    s_method character varying(64) DEFAULT ''::character varying NOT NULL,
    s_cseq character varying(64) DEFAULT ''::character varying NOT NULL,
    a_callid character varying(255) DEFAULT ''::character varying NOT NULL,
    a_uuid character varying(255) DEFAULT ''::character varying NOT NULL,
    b_uuid character varying(255) DEFAULT ''::character varying NOT NULL,
    direction integer DEFAULT 0 NOT NULL,
    x_via text,
    x_vbranch character varying(255) DEFAULT ''::character varying NOT NULL,
    x_rr text,
    y_rr text,
    s_rr text,
    x_uri character varying(128) DEFAULT ''::character varying NOT NULL,
    a_contact character varying(128) DEFAULT ''::character varying NOT NULL,
    b_contact character varying(128) DEFAULT ''::character varying NOT NULL,
    as_contact character varying(128) DEFAULT ''::character varying NOT NULL,
    bs_contact character varying(128) DEFAULT ''::character varying NOT NULL,
    x_tag character varying(255) DEFAULT ''::character varying NOT NULL,
    a_tag character varying(255) DEFAULT ''::character varying NOT NULL,
    b_tag character varying(255) DEFAULT ''::character varying NOT NULL,
    a_srcaddr character varying(128) DEFAULT ''::character varying NOT NULL,
    b_srcaddr character varying(128) DEFAULT ''::character varying NOT NULL,
    a_socket character varying(128) DEFAULT ''::character varying NOT NULL,
    b_socket character varying(128) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.topos_t OWNER TO omnileads;

--
-- Name: topos_t_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.topos_t_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.topos_t_id_seq OWNER TO omnileads;

--
-- Name: topos_t_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.topos_t_id_seq OWNED BY public.topos_t.id;


--
-- Name: trusted; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.trusted (
    id integer NOT NULL,
    src_ip character varying(50) NOT NULL,
    proto character varying(4) NOT NULL,
    from_pattern character varying(64) DEFAULT NULL::character varying,
    ruri_pattern character varying(64) DEFAULT NULL::character varying,
    tag character varying(64),
    priority integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.trusted OWNER TO omnileads;

--
-- Name: trusted_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.trusted_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trusted_id_seq OWNER TO omnileads;

--
-- Name: trusted_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.trusted_id_seq OWNED BY public.trusted.id;


--
-- Name: uacreg; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.uacreg (
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
    expires integer DEFAULT 0 NOT NULL,
    flags integer DEFAULT 0 NOT NULL,
    reg_delay integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.uacreg OWNER TO omnileads;

--
-- Name: uacreg_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.uacreg_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.uacreg_id_seq OWNER TO omnileads;

--
-- Name: uacreg_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.uacreg_id_seq OWNED BY public.uacreg.id;


--
-- Name: uri; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.uri (
    id integer NOT NULL,
    username character varying(64) DEFAULT ''::character varying NOT NULL,
    domain character varying(64) DEFAULT ''::character varying NOT NULL,
    uri_user character varying(64) DEFAULT ''::character varying NOT NULL,
    last_modified timestamp without time zone DEFAULT '2000-01-01 00:00:01'::timestamp without time zone NOT NULL
);


ALTER TABLE public.uri OWNER TO omnileads;

--
-- Name: uri_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.uri_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.uri_id_seq OWNER TO omnileads;

--
-- Name: uri_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.uri_id_seq OWNED BY public.uri.id;


--
-- Name: userblacklist; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.userblacklist (
    id integer NOT NULL,
    username character varying(64) DEFAULT ''::character varying NOT NULL,
    domain character varying(64) DEFAULT ''::character varying NOT NULL,
    prefix character varying(64) DEFAULT ''::character varying NOT NULL,
    whitelist smallint DEFAULT 0 NOT NULL
);


ALTER TABLE public.userblacklist OWNER TO omnileads;

--
-- Name: userblacklist_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.userblacklist_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.userblacklist_id_seq OWNER TO omnileads;

--
-- Name: userblacklist_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.userblacklist_id_seq OWNED BY public.userblacklist.id;


--
-- Name: usr_preferences; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.usr_preferences (
    id integer NOT NULL,
    uuid character varying(64) DEFAULT ''::character varying NOT NULL,
    username character varying(128) DEFAULT 0 NOT NULL,
    domain character varying(64) DEFAULT ''::character varying NOT NULL,
    attribute character varying(32) DEFAULT ''::character varying NOT NULL,
    type integer DEFAULT 0 NOT NULL,
    value character varying(128) DEFAULT ''::character varying NOT NULL,
    last_modified timestamp without time zone DEFAULT '2000-01-01 00:00:01'::timestamp without time zone NOT NULL
);


ALTER TABLE public.usr_preferences OWNER TO omnileads;

--
-- Name: usr_preferences_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.usr_preferences_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.usr_preferences_id_seq OWNER TO omnileads;

--
-- Name: usr_preferences_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.usr_preferences_id_seq OWNED BY public.usr_preferences.id;


--
-- Name: version; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.version (
    table_name character varying(32) NOT NULL,
    table_version integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.version OWNER TO omnileads;

--
-- Name: watchers; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.watchers (
    id integer NOT NULL,
    presentity_uri character varying(128) NOT NULL,
    watcher_username character varying(64) NOT NULL,
    watcher_domain character varying(64) NOT NULL,
    event character varying(64) DEFAULT 'presence'::character varying NOT NULL,
    status integer NOT NULL,
    reason character varying(64),
    inserted_time integer NOT NULL
);


ALTER TABLE public.watchers OWNER TO omnileads;

--
-- Name: watchers_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.watchers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.watchers_id_seq OWNER TO omnileads;

--
-- Name: watchers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.watchers_id_seq OWNED BY public.watchers.id;


--
-- Name: xcap; Type: TABLE; Schema: public; Owner: omnileads
--

CREATE TABLE public.xcap (
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


ALTER TABLE public.xcap OWNER TO omnileads;

--
-- Name: xcap_id_seq; Type: SEQUENCE; Schema: public; Owner: omnileads
--

CREATE SEQUENCE public.xcap_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.xcap_id_seq OWNER TO omnileads;

--
-- Name: xcap_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnileads
--

ALTER SEQUENCE public.xcap_id_seq OWNED BY public.xcap.id;


--
-- Name: acc id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.acc ALTER COLUMN id SET DEFAULT nextval('public.acc_id_seq'::regclass);


--
-- Name: acc_cdrs id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.acc_cdrs ALTER COLUMN id SET DEFAULT nextval('public.acc_cdrs_id_seq'::regclass);


--
-- Name: active_watchers id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.active_watchers ALTER COLUMN id SET DEFAULT nextval('public.active_watchers_id_seq'::regclass);


--
-- Name: address id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.address ALTER COLUMN id SET DEFAULT nextval('public.address_id_seq'::regclass);


--
-- Name: aliases id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.aliases ALTER COLUMN id SET DEFAULT nextval('public.aliases_id_seq'::regclass);


--
-- Name: carrier_name id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.carrier_name ALTER COLUMN id SET DEFAULT nextval('public.carrier_name_id_seq'::regclass);


--
-- Name: carrierfailureroute id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.carrierfailureroute ALTER COLUMN id SET DEFAULT nextval('public.carrierfailureroute_id_seq'::regclass);


--
-- Name: carrierroute id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.carrierroute ALTER COLUMN id SET DEFAULT nextval('public.carrierroute_id_seq'::regclass);


--
-- Name: cpl id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.cpl ALTER COLUMN id SET DEFAULT nextval('public.cpl_id_seq'::regclass);


--
-- Name: dbaliases id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.dbaliases ALTER COLUMN id SET DEFAULT nextval('public.dbaliases_id_seq'::regclass);


--
-- Name: dialog id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.dialog ALTER COLUMN id SET DEFAULT nextval('public.dialog_id_seq'::regclass);


--
-- Name: dialog_vars id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.dialog_vars ALTER COLUMN id SET DEFAULT nextval('public.dialog_vars_id_seq'::regclass);


--
-- Name: dialplan id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.dialplan ALTER COLUMN id SET DEFAULT nextval('public.dialplan_id_seq'::regclass);


--
-- Name: dispatcher id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.dispatcher ALTER COLUMN id SET DEFAULT nextval('public.dispatcher_id_seq'::regclass);


--
-- Name: domain id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.domain ALTER COLUMN id SET DEFAULT nextval('public.domain_id_seq'::regclass);


--
-- Name: domain_attrs id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.domain_attrs ALTER COLUMN id SET DEFAULT nextval('public.domain_attrs_id_seq'::regclass);


--
-- Name: domain_name id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.domain_name ALTER COLUMN id SET DEFAULT nextval('public.domain_name_id_seq'::regclass);


--
-- Name: domainpolicy id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.domainpolicy ALTER COLUMN id SET DEFAULT nextval('public.domainpolicy_id_seq'::regclass);


--
-- Name: dr_gateways gwid; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.dr_gateways ALTER COLUMN gwid SET DEFAULT nextval('public.dr_gateways_gwid_seq'::regclass);


--
-- Name: dr_groups id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.dr_groups ALTER COLUMN id SET DEFAULT nextval('public.dr_groups_id_seq'::regclass);


--
-- Name: dr_gw_lists id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.dr_gw_lists ALTER COLUMN id SET DEFAULT nextval('public.dr_gw_lists_id_seq'::regclass);


--
-- Name: dr_rules ruleid; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.dr_rules ALTER COLUMN ruleid SET DEFAULT nextval('public.dr_rules_ruleid_seq'::regclass);


--
-- Name: globalblacklist id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.globalblacklist ALTER COLUMN id SET DEFAULT nextval('public.globalblacklist_id_seq'::regclass);


--
-- Name: grp id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.grp ALTER COLUMN id SET DEFAULT nextval('public.grp_id_seq'::regclass);


--
-- Name: htable id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.htable ALTER COLUMN id SET DEFAULT nextval('public.htable_id_seq'::regclass);


--
-- Name: imc_members id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.imc_members ALTER COLUMN id SET DEFAULT nextval('public.imc_members_id_seq'::regclass);


--
-- Name: imc_rooms id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.imc_rooms ALTER COLUMN id SET DEFAULT nextval('public.imc_rooms_id_seq'::regclass);


--
-- Name: lcr_gw id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.lcr_gw ALTER COLUMN id SET DEFAULT nextval('public.lcr_gw_id_seq'::regclass);


--
-- Name: lcr_rule id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.lcr_rule ALTER COLUMN id SET DEFAULT nextval('public.lcr_rule_id_seq'::regclass);


--
-- Name: lcr_rule_target id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.lcr_rule_target ALTER COLUMN id SET DEFAULT nextval('public.lcr_rule_target_id_seq'::regclass);


--
-- Name: location id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.location ALTER COLUMN id SET DEFAULT nextval('public.location_id_seq'::regclass);


--
-- Name: location_attrs id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.location_attrs ALTER COLUMN id SET DEFAULT nextval('public.location_attrs_id_seq'::regclass);


--
-- Name: missed_calls id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.missed_calls ALTER COLUMN id SET DEFAULT nextval('public.missed_calls_id_seq'::regclass);


--
-- Name: mohqcalls id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.mohqcalls ALTER COLUMN id SET DEFAULT nextval('public.mohqcalls_id_seq'::regclass);


--
-- Name: mohqueues id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.mohqueues ALTER COLUMN id SET DEFAULT nextval('public.mohqueues_id_seq'::regclass);


--
-- Name: mtree id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.mtree ALTER COLUMN id SET DEFAULT nextval('public.mtree_id_seq'::regclass);


--
-- Name: mtrees id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.mtrees ALTER COLUMN id SET DEFAULT nextval('public.mtrees_id_seq'::regclass);


--
-- Name: pdt id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.pdt ALTER COLUMN id SET DEFAULT nextval('public.pdt_id_seq'::regclass);


--
-- Name: pl_pipes id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.pl_pipes ALTER COLUMN id SET DEFAULT nextval('public.pl_pipes_id_seq'::regclass);


--
-- Name: presentity id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.presentity ALTER COLUMN id SET DEFAULT nextval('public.presentity_id_seq'::regclass);


--
-- Name: pua id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.pua ALTER COLUMN id SET DEFAULT nextval('public.pua_id_seq'::regclass);


--
-- Name: purplemap id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.purplemap ALTER COLUMN id SET DEFAULT nextval('public.purplemap_id_seq'::regclass);


--
-- Name: re_grp id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.re_grp ALTER COLUMN id SET DEFAULT nextval('public.re_grp_id_seq'::regclass);


--
-- Name: rls_presentity id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.rls_presentity ALTER COLUMN id SET DEFAULT nextval('public.rls_presentity_id_seq'::regclass);


--
-- Name: rls_watchers id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.rls_watchers ALTER COLUMN id SET DEFAULT nextval('public.rls_watchers_id_seq'::regclass);


--
-- Name: rtpproxy id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.rtpproxy ALTER COLUMN id SET DEFAULT nextval('public.rtpproxy_id_seq'::regclass);


--
-- Name: sca_subscriptions id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.sca_subscriptions ALTER COLUMN id SET DEFAULT nextval('public.sca_subscriptions_id_seq'::regclass);


--
-- Name: silo id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.silo ALTER COLUMN id SET DEFAULT nextval('public.silo_id_seq'::regclass);


--
-- Name: sip_trace id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.sip_trace ALTER COLUMN id SET DEFAULT nextval('public.sip_trace_id_seq'::regclass);


--
-- Name: speed_dial id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.speed_dial ALTER COLUMN id SET DEFAULT nextval('public.speed_dial_id_seq'::regclass);


--
-- Name: subscriber id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.subscriber ALTER COLUMN id SET DEFAULT nextval('public.subscriber_id_seq'::regclass);


--
-- Name: topos_d id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.topos_d ALTER COLUMN id SET DEFAULT nextval('public.topos_d_id_seq'::regclass);


--
-- Name: topos_t id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.topos_t ALTER COLUMN id SET DEFAULT nextval('public.topos_t_id_seq'::regclass);


--
-- Name: trusted id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.trusted ALTER COLUMN id SET DEFAULT nextval('public.trusted_id_seq'::regclass);


--
-- Name: uacreg id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.uacreg ALTER COLUMN id SET DEFAULT nextval('public.uacreg_id_seq'::regclass);


--
-- Name: uri id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.uri ALTER COLUMN id SET DEFAULT nextval('public.uri_id_seq'::regclass);


--
-- Name: userblacklist id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.userblacklist ALTER COLUMN id SET DEFAULT nextval('public.userblacklist_id_seq'::regclass);


--
-- Name: usr_preferences id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.usr_preferences ALTER COLUMN id SET DEFAULT nextval('public.usr_preferences_id_seq'::regclass);


--
-- Name: watchers id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.watchers ALTER COLUMN id SET DEFAULT nextval('public.watchers_id_seq'::regclass);


--
-- Name: xcap id; Type: DEFAULT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.xcap ALTER COLUMN id SET DEFAULT nextval('public.xcap_id_seq'::regclass);


--
-- Data for Name: acc; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.acc (id, method, from_tag, to_tag, callid, sip_code, sip_reason, "time") FROM stdin;
\.


--
-- Data for Name: acc_cdrs; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.acc_cdrs (id, start_time, end_time, duration) FROM stdin;
\.


--
-- Name: acc_cdrs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.acc_cdrs_id_seq', 1, false);


--
-- Name: acc_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.acc_id_seq', 1, false);


--
-- Data for Name: active_watchers; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.active_watchers (id, presentity_uri, watcher_username, watcher_domain, to_user, to_domain, event, event_id, to_tag, from_tag, callid, local_cseq, remote_cseq, contact, record_route, expires, status, reason, version, socket_info, local_contact, from_user, from_domain, updated, updated_winfo, flags, user_agent) FROM stdin;
\.


--
-- Name: active_watchers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.active_watchers_id_seq', 1, false);


--
-- Data for Name: address; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.address (id, grp, ip_addr, mask, port, tag) FROM stdin;
\.


--
-- Name: address_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.address_id_seq', 1, false);


--
-- Data for Name: aliases; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.aliases (id, ruid, username, domain, contact, received, path, expires, q, callid, cseq, last_modified, flags, cflags, user_agent, socket, methods, instance, reg_id, server_id, connection_id, keepalive, partition) FROM stdin;
\.


--
-- Name: aliases_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.aliases_id_seq', 1, false);


--
-- Data for Name: carrier_name; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.carrier_name (id, carrier) FROM stdin;
\.


--
-- Name: carrier_name_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.carrier_name_id_seq', 1, false);


--
-- Data for Name: carrierfailureroute; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.carrierfailureroute (id, carrier, domain, scan_prefix, host_name, reply_code, flags, mask, next_domain, description) FROM stdin;
\.


--
-- Name: carrierfailureroute_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.carrierfailureroute_id_seq', 1, false);


--
-- Data for Name: carrierroute; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.carrierroute (id, carrier, domain, scan_prefix, flags, mask, prob, strip, rewrite_host, rewrite_prefix, rewrite_suffix, description) FROM stdin;
\.


--
-- Name: carrierroute_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.carrierroute_id_seq', 1, false);


--
-- Data for Name: cpl; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.cpl (id, username, domain, cpl_xml, cpl_bin) FROM stdin;
\.


--
-- Name: cpl_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.cpl_id_seq', 1, false);


--
-- Data for Name: dbaliases; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.dbaliases (id, alias_username, alias_domain, username, domain) FROM stdin;
\.


--
-- Name: dbaliases_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.dbaliases_id_seq', 1, false);


--
-- Data for Name: dialog; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.dialog (id, hash_entry, hash_id, callid, from_uri, from_tag, to_uri, to_tag, caller_cseq, callee_cseq, caller_route_set, callee_route_set, caller_contact, callee_contact, caller_sock, callee_sock, state, start_time, timeout, sflags, iflags, toroute_name, req_uri, xdata) FROM stdin;
\.


--
-- Name: dialog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.dialog_id_seq', 1, false);


--
-- Data for Name: dialog_vars; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.dialog_vars (id, hash_entry, hash_id, dialog_key, dialog_value) FROM stdin;
\.


--
-- Name: dialog_vars_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.dialog_vars_id_seq', 1, false);


--
-- Data for Name: dialplan; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.dialplan (id, dpid, pr, match_op, match_exp, match_len, subst_exp, repl_exp, attrs) FROM stdin;
\.


--
-- Name: dialplan_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.dialplan_id_seq', 1, false);


--
-- Data for Name: dispatcher; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.dispatcher (id, setid, destination, flags, priority, attrs, description) FROM stdin;
\.


--
-- Name: dispatcher_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.dispatcher_id_seq', 1, false);


--
-- Data for Name: domain; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.domain (id, domain, did, last_modified) FROM stdin;
\.


--
-- Data for Name: domain_attrs; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.domain_attrs (id, did, name, type, value, last_modified) FROM stdin;
\.


--
-- Name: domain_attrs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.domain_attrs_id_seq', 1, false);


--
-- Name: domain_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.domain_id_seq', 1, false);


--
-- Data for Name: domain_name; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.domain_name (id, domain) FROM stdin;
\.


--
-- Name: domain_name_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.domain_name_id_seq', 1, false);


--
-- Data for Name: domainpolicy; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.domainpolicy (id, rule, type, att, val, description) FROM stdin;
\.


--
-- Name: domainpolicy_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.domainpolicy_id_seq', 1, false);


--
-- Data for Name: dr_gateways; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.dr_gateways (gwid, type, address, strip, pri_prefix, attrs, description) FROM stdin;
\.


--
-- Name: dr_gateways_gwid_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.dr_gateways_gwid_seq', 1, false);


--
-- Data for Name: dr_groups; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.dr_groups (id, username, domain, groupid, description) FROM stdin;
\.


--
-- Name: dr_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.dr_groups_id_seq', 1, false);


--
-- Data for Name: dr_gw_lists; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.dr_gw_lists (id, gwlist, description) FROM stdin;
\.


--
-- Name: dr_gw_lists_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.dr_gw_lists_id_seq', 1, false);


--
-- Data for Name: dr_rules; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.dr_rules (ruleid, groupid, prefix, timerec, priority, routeid, gwlist, description) FROM stdin;
\.


--
-- Name: dr_rules_ruleid_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.dr_rules_ruleid_seq', 1, false);


--
-- Data for Name: globalblacklist; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.globalblacklist (id, prefix, whitelist, description) FROM stdin;
\.


--
-- Name: globalblacklist_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.globalblacklist_id_seq', 1, false);


--
-- Data for Name: grp; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.grp (id, username, domain, grp, last_modified) FROM stdin;
\.


--
-- Name: grp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.grp_id_seq', 1, false);


--
-- Data for Name: htable; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.htable (id, key_name, key_type, value_type, key_value, expires) FROM stdin;
\.


--
-- Name: htable_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.htable_id_seq', 1, false);


--
-- Data for Name: imc_members; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.imc_members (id, username, domain, room, flag) FROM stdin;
\.


--
-- Name: imc_members_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.imc_members_id_seq', 1, false);


--
-- Data for Name: imc_rooms; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.imc_rooms (id, name, domain, flag) FROM stdin;
\.


--
-- Name: imc_rooms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.imc_rooms_id_seq', 1, false);


--
-- Data for Name: lcr_gw; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.lcr_gw (id, lcr_id, gw_name, ip_addr, hostname, port, params, uri_scheme, transport, strip, prefix, tag, flags, defunct) FROM stdin;
\.


--
-- Name: lcr_gw_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.lcr_gw_id_seq', 1, false);


--
-- Data for Name: lcr_rule; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.lcr_rule (id, lcr_id, prefix, from_uri, request_uri, stopper, enabled) FROM stdin;
\.


--
-- Name: lcr_rule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.lcr_rule_id_seq', 1, false);


--
-- Data for Name: lcr_rule_target; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.lcr_rule_target (id, lcr_id, rule_id, gw_id, priority, weight) FROM stdin;
\.


--
-- Name: lcr_rule_target_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.lcr_rule_target_id_seq', 1, false);


--
-- Data for Name: location; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.location (id, ruid, username, domain, contact, received, path, expires, q, callid, cseq, last_modified, flags, cflags, user_agent, socket, methods, instance, reg_id, server_id, connection_id, keepalive, partition) FROM stdin;
\.


--
-- Data for Name: location_attrs; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.location_attrs (id, ruid, username, domain, aname, atype, avalue, last_modified) FROM stdin;
\.


--
-- Name: location_attrs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.location_attrs_id_seq', 1, false);


--
-- Name: location_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.location_id_seq', 1, false);


--
-- Data for Name: missed_calls; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.missed_calls (id, method, from_tag, to_tag, callid, sip_code, sip_reason, "time") FROM stdin;
\.


--
-- Name: missed_calls_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.missed_calls_id_seq', 1, false);


--
-- Data for Name: mohqcalls; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.mohqcalls (id, mohq_id, call_id, call_status, call_from, call_contact, call_time) FROM stdin;
\.


--
-- Name: mohqcalls_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.mohqcalls_id_seq', 1, false);


--
-- Data for Name: mohqueues; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.mohqueues (id, name, uri, mohdir, mohfile, debug) FROM stdin;
\.


--
-- Name: mohqueues_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.mohqueues_id_seq', 1, false);


--
-- Data for Name: mtree; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.mtree (id, tprefix, tvalue) FROM stdin;
\.


--
-- Name: mtree_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.mtree_id_seq', 1, false);


--
-- Data for Name: mtrees; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.mtrees (id, tname, tprefix, tvalue) FROM stdin;
\.


--
-- Name: mtrees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.mtrees_id_seq', 1, false);


--
-- Data for Name: pdt; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.pdt (id, sdomain, prefix, domain) FROM stdin;
\.


--
-- Name: pdt_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.pdt_id_seq', 1, false);


--
-- Data for Name: pl_pipes; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.pl_pipes (id, pipeid, algorithm, plimit) FROM stdin;
\.


--
-- Name: pl_pipes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.pl_pipes_id_seq', 1, false);


--
-- Data for Name: presentity; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.presentity (id, username, domain, event, etag, expires, received_time, body, sender, priority) FROM stdin;
\.


--
-- Name: presentity_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.presentity_id_seq', 1, false);


--
-- Data for Name: pua; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.pua (id, pres_uri, pres_id, event, expires, desired_expires, flag, etag, tuple_id, watcher_uri, call_id, to_tag, from_tag, cseq, record_route, contact, remote_contact, version, extra_headers) FROM stdin;
\.


--
-- Name: pua_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.pua_id_seq', 1, false);


--
-- Data for Name: purplemap; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.purplemap (id, sip_user, ext_user, ext_prot, ext_pass) FROM stdin;
\.


--
-- Name: purplemap_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.purplemap_id_seq', 1, false);


--
-- Data for Name: re_grp; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.re_grp (id, reg_exp, group_id) FROM stdin;
\.


--
-- Name: re_grp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.re_grp_id_seq', 1, false);


--
-- Data for Name: rls_presentity; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.rls_presentity (id, rlsubs_did, resource_uri, content_type, presence_state, expires, updated, auth_state, reason) FROM stdin;
\.


--
-- Name: rls_presentity_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.rls_presentity_id_seq', 1, false);


--
-- Data for Name: rls_watchers; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.rls_watchers (id, presentity_uri, to_user, to_domain, watcher_username, watcher_domain, event, event_id, to_tag, from_tag, callid, local_cseq, remote_cseq, contact, record_route, expires, status, reason, version, socket_info, local_contact, from_user, from_domain, updated) FROM stdin;
\.


--
-- Name: rls_watchers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.rls_watchers_id_seq', 1, false);


--
-- Data for Name: rtpproxy; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.rtpproxy (id, setid, url, flags, weight, description) FROM stdin;
\.


--
-- Name: rtpproxy_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.rtpproxy_id_seq', 1, false);


--
-- Data for Name: sca_subscriptions; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.sca_subscriptions (id, subscriber, aor, event, expires, state, app_idx, call_id, from_tag, to_tag, record_route, notify_cseq, subscribe_cseq) FROM stdin;
\.


--
-- Name: sca_subscriptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.sca_subscriptions_id_seq', 1, false);


--
-- Data for Name: silo; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.silo (id, src_addr, dst_addr, username, domain, inc_time, exp_time, snd_time, ctype, body, extra_hdrs, callid, status) FROM stdin;
\.


--
-- Name: silo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.silo_id_seq', 1, false);


--
-- Data for Name: sip_trace; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.sip_trace (id, time_stamp, time_us, callid, traced_user, msg, method, status, fromip, toip, fromtag, totag, direction) FROM stdin;
\.


--
-- Name: sip_trace_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.sip_trace_id_seq', 1, false);


--
-- Data for Name: speed_dial; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.speed_dial (id, username, domain, sd_username, sd_domain, new_uri, fname, lname, description) FROM stdin;
\.


--
-- Name: speed_dial_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.speed_dial_id_seq', 1, false);


--
-- Data for Name: subscriber; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.subscriber (id, username, domain, password, email_address, ha1, ha1b, rpid) FROM stdin;
\.


--
-- Name: subscriber_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.subscriber_id_seq', 1, false);


--
-- Data for Name: topos_d; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.topos_d (id, rectime, s_method, s_cseq, a_callid, a_uuid, b_uuid, a_contact, b_contact, as_contact, bs_contact, a_tag, b_tag, a_rr, b_rr, s_rr, iflags, a_uri, b_uri, r_uri, a_srcaddr, b_srcaddr, a_socket, b_socket) FROM stdin;
\.


--
-- Name: topos_d_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.topos_d_id_seq', 1, false);


--
-- Data for Name: topos_t; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.topos_t (id, rectime, s_method, s_cseq, a_callid, a_uuid, b_uuid, direction, x_via, x_vbranch, x_rr, y_rr, s_rr, x_uri, a_contact, b_contact, as_contact, bs_contact, x_tag, a_tag, b_tag, a_srcaddr, b_srcaddr, a_socket, b_socket) FROM stdin;
\.


--
-- Name: topos_t_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.topos_t_id_seq', 1, false);


--
-- Data for Name: trusted; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.trusted (id, src_ip, proto, from_pattern, ruri_pattern, tag, priority) FROM stdin;
\.


--
-- Name: trusted_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.trusted_id_seq', 1, false);


--
-- Data for Name: uacreg; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.uacreg (id, l_uuid, l_username, l_domain, r_username, r_domain, realm, auth_username, auth_password, auth_proxy, expires, flags, reg_delay) FROM stdin;
\.


--
-- Name: uacreg_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.uacreg_id_seq', 1, false);


--
-- Data for Name: uri; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.uri (id, username, domain, uri_user, last_modified) FROM stdin;
\.


--
-- Name: uri_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.uri_id_seq', 1, false);


--
-- Data for Name: userblacklist; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.userblacklist (id, username, domain, prefix, whitelist) FROM stdin;
\.


--
-- Name: userblacklist_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.userblacklist_id_seq', 1, false);


--
-- Data for Name: usr_preferences; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.usr_preferences (id, uuid, username, domain, attribute, type, value, last_modified) FROM stdin;
\.


--
-- Name: usr_preferences_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.usr_preferences_id_seq', 1, false);


--
-- Data for Name: version; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.version (table_name, table_version) FROM stdin;
version	1
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
trusted	6
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
topos_d	1
topos_t	1
presentity	4
active_watchers	12
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
dr_gateways	3
dr_rules	3
dr_gw_lists	1
dr_groups	2
userblacklist	1
globalblacklist	1
htable	2
purplemap	1
uacreg	2
pl_pipes	1
mtree	1
mtrees	2
sca_subscriptions	1
mohqcalls	1
mohqueues	1
rtpproxy	1
\.


--
-- Data for Name: watchers; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.watchers (id, presentity_uri, watcher_username, watcher_domain, event, status, reason, inserted_time) FROM stdin;
\.


--
-- Name: watchers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.watchers_id_seq', 1, false);


--
-- Data for Name: xcap; Type: TABLE DATA; Schema: public; Owner: omnileads
--

COPY public.xcap (id, username, domain, doc, doc_type, etag, source, doc_uri, port) FROM stdin;
\.


--
-- Name: xcap_id_seq; Type: SEQUENCE SET; Schema: public; Owner: omnileads
--

SELECT pg_catalog.setval('public.xcap_id_seq', 1, false);


--
-- Name: acc_cdrs acc_cdrs_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.acc_cdrs
    ADD CONSTRAINT acc_cdrs_pkey PRIMARY KEY (id);


--
-- Name: acc acc_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.acc
    ADD CONSTRAINT acc_pkey PRIMARY KEY (id);


--
-- Name: active_watchers active_watchers_active_watchers_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.active_watchers
    ADD CONSTRAINT active_watchers_active_watchers_idx UNIQUE (callid, to_tag, from_tag);


--
-- Name: active_watchers active_watchers_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.active_watchers
    ADD CONSTRAINT active_watchers_pkey PRIMARY KEY (id);


--
-- Name: address address_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.address
    ADD CONSTRAINT address_pkey PRIMARY KEY (id);


--
-- Name: aliases aliases_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.aliases
    ADD CONSTRAINT aliases_pkey PRIMARY KEY (id);


--
-- Name: aliases aliases_ruid_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.aliases
    ADD CONSTRAINT aliases_ruid_idx UNIQUE (ruid);


--
-- Name: carrier_name carrier_name_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.carrier_name
    ADD CONSTRAINT carrier_name_pkey PRIMARY KEY (id);


--
-- Name: carrierfailureroute carrierfailureroute_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.carrierfailureroute
    ADD CONSTRAINT carrierfailureroute_pkey PRIMARY KEY (id);


--
-- Name: carrierroute carrierroute_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.carrierroute
    ADD CONSTRAINT carrierroute_pkey PRIMARY KEY (id);


--
-- Name: cpl cpl_account_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.cpl
    ADD CONSTRAINT cpl_account_idx UNIQUE (username, domain);


--
-- Name: cpl cpl_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.cpl
    ADD CONSTRAINT cpl_pkey PRIMARY KEY (id);


--
-- Name: dbaliases dbaliases_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.dbaliases
    ADD CONSTRAINT dbaliases_pkey PRIMARY KEY (id);


--
-- Name: dialog dialog_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.dialog
    ADD CONSTRAINT dialog_pkey PRIMARY KEY (id);


--
-- Name: dialog_vars dialog_vars_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.dialog_vars
    ADD CONSTRAINT dialog_vars_pkey PRIMARY KEY (id);


--
-- Name: dialplan dialplan_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.dialplan
    ADD CONSTRAINT dialplan_pkey PRIMARY KEY (id);


--
-- Name: dispatcher dispatcher_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.dispatcher
    ADD CONSTRAINT dispatcher_pkey PRIMARY KEY (id);


--
-- Name: domain_attrs domain_attrs_domain_attrs_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.domain_attrs
    ADD CONSTRAINT domain_attrs_domain_attrs_idx UNIQUE (did, name, value);


--
-- Name: domain_attrs domain_attrs_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.domain_attrs
    ADD CONSTRAINT domain_attrs_pkey PRIMARY KEY (id);


--
-- Name: domain domain_domain_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.domain
    ADD CONSTRAINT domain_domain_idx UNIQUE (domain);


--
-- Name: domain_name domain_name_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.domain_name
    ADD CONSTRAINT domain_name_pkey PRIMARY KEY (id);


--
-- Name: domain domain_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.domain
    ADD CONSTRAINT domain_pkey PRIMARY KEY (id);


--
-- Name: domainpolicy domainpolicy_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.domainpolicy
    ADD CONSTRAINT domainpolicy_pkey PRIMARY KEY (id);


--
-- Name: domainpolicy domainpolicy_rav_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.domainpolicy
    ADD CONSTRAINT domainpolicy_rav_idx UNIQUE (rule, att, val);


--
-- Name: dr_gateways dr_gateways_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.dr_gateways
    ADD CONSTRAINT dr_gateways_pkey PRIMARY KEY (gwid);


--
-- Name: dr_groups dr_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.dr_groups
    ADD CONSTRAINT dr_groups_pkey PRIMARY KEY (id);


--
-- Name: dr_gw_lists dr_gw_lists_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.dr_gw_lists
    ADD CONSTRAINT dr_gw_lists_pkey PRIMARY KEY (id);


--
-- Name: dr_rules dr_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.dr_rules
    ADD CONSTRAINT dr_rules_pkey PRIMARY KEY (ruleid);


--
-- Name: globalblacklist globalblacklist_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.globalblacklist
    ADD CONSTRAINT globalblacklist_pkey PRIMARY KEY (id);


--
-- Name: grp grp_account_group_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.grp
    ADD CONSTRAINT grp_account_group_idx UNIQUE (username, domain, grp);


--
-- Name: grp grp_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.grp
    ADD CONSTRAINT grp_pkey PRIMARY KEY (id);


--
-- Name: htable htable_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.htable
    ADD CONSTRAINT htable_pkey PRIMARY KEY (id);


--
-- Name: imc_members imc_members_account_room_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.imc_members
    ADD CONSTRAINT imc_members_account_room_idx UNIQUE (username, domain, room);


--
-- Name: imc_members imc_members_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.imc_members
    ADD CONSTRAINT imc_members_pkey PRIMARY KEY (id);


--
-- Name: imc_rooms imc_rooms_name_domain_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.imc_rooms
    ADD CONSTRAINT imc_rooms_name_domain_idx UNIQUE (name, domain);


--
-- Name: imc_rooms imc_rooms_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.imc_rooms
    ADD CONSTRAINT imc_rooms_pkey PRIMARY KEY (id);


--
-- Name: lcr_gw lcr_gw_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.lcr_gw
    ADD CONSTRAINT lcr_gw_pkey PRIMARY KEY (id);


--
-- Name: lcr_rule lcr_rule_lcr_id_prefix_from_uri_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.lcr_rule
    ADD CONSTRAINT lcr_rule_lcr_id_prefix_from_uri_idx UNIQUE (lcr_id, prefix, from_uri);


--
-- Name: lcr_rule lcr_rule_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.lcr_rule
    ADD CONSTRAINT lcr_rule_pkey PRIMARY KEY (id);


--
-- Name: lcr_rule_target lcr_rule_target_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.lcr_rule_target
    ADD CONSTRAINT lcr_rule_target_pkey PRIMARY KEY (id);


--
-- Name: lcr_rule_target lcr_rule_target_rule_id_gw_id_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.lcr_rule_target
    ADD CONSTRAINT lcr_rule_target_rule_id_gw_id_idx UNIQUE (rule_id, gw_id);


--
-- Name: location_attrs location_attrs_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.location_attrs
    ADD CONSTRAINT location_attrs_pkey PRIMARY KEY (id);


--
-- Name: location location_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.location
    ADD CONSTRAINT location_pkey PRIMARY KEY (id);


--
-- Name: location location_ruid_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.location
    ADD CONSTRAINT location_ruid_idx UNIQUE (ruid);


--
-- Name: missed_calls missed_calls_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.missed_calls
    ADD CONSTRAINT missed_calls_pkey PRIMARY KEY (id);


--
-- Name: mohqcalls mohqcalls_mohqcalls_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.mohqcalls
    ADD CONSTRAINT mohqcalls_mohqcalls_idx UNIQUE (call_id);


--
-- Name: mohqcalls mohqcalls_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.mohqcalls
    ADD CONSTRAINT mohqcalls_pkey PRIMARY KEY (id);


--
-- Name: mohqueues mohqueues_mohqueue_name_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.mohqueues
    ADD CONSTRAINT mohqueues_mohqueue_name_idx UNIQUE (name);


--
-- Name: mohqueues mohqueues_mohqueue_uri_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.mohqueues
    ADD CONSTRAINT mohqueues_mohqueue_uri_idx UNIQUE (uri);


--
-- Name: mohqueues mohqueues_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.mohqueues
    ADD CONSTRAINT mohqueues_pkey PRIMARY KEY (id);


--
-- Name: mtree mtree_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.mtree
    ADD CONSTRAINT mtree_pkey PRIMARY KEY (id);


--
-- Name: mtree mtree_tprefix_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.mtree
    ADD CONSTRAINT mtree_tprefix_idx UNIQUE (tprefix);


--
-- Name: mtrees mtrees_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.mtrees
    ADD CONSTRAINT mtrees_pkey PRIMARY KEY (id);


--
-- Name: mtrees mtrees_tname_tprefix_tvalue_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.mtrees
    ADD CONSTRAINT mtrees_tname_tprefix_tvalue_idx UNIQUE (tname, tprefix, tvalue);


--
-- Name: pdt pdt_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.pdt
    ADD CONSTRAINT pdt_pkey PRIMARY KEY (id);


--
-- Name: pdt pdt_sdomain_prefix_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.pdt
    ADD CONSTRAINT pdt_sdomain_prefix_idx UNIQUE (sdomain, prefix);


--
-- Name: pl_pipes pl_pipes_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.pl_pipes
    ADD CONSTRAINT pl_pipes_pkey PRIMARY KEY (id);


--
-- Name: presentity presentity_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.presentity
    ADD CONSTRAINT presentity_pkey PRIMARY KEY (id);


--
-- Name: presentity presentity_presentity_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.presentity
    ADD CONSTRAINT presentity_presentity_idx UNIQUE (username, domain, event, etag);


--
-- Name: pua pua_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.pua
    ADD CONSTRAINT pua_pkey PRIMARY KEY (id);


--
-- Name: pua pua_pua_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.pua
    ADD CONSTRAINT pua_pua_idx UNIQUE (etag, tuple_id, call_id, from_tag);


--
-- Name: purplemap purplemap_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.purplemap
    ADD CONSTRAINT purplemap_pkey PRIMARY KEY (id);


--
-- Name: re_grp re_grp_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.re_grp
    ADD CONSTRAINT re_grp_pkey PRIMARY KEY (id);


--
-- Name: rls_presentity rls_presentity_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.rls_presentity
    ADD CONSTRAINT rls_presentity_pkey PRIMARY KEY (id);


--
-- Name: rls_presentity rls_presentity_rls_presentity_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.rls_presentity
    ADD CONSTRAINT rls_presentity_rls_presentity_idx UNIQUE (rlsubs_did, resource_uri);


--
-- Name: rls_watchers rls_watchers_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.rls_watchers
    ADD CONSTRAINT rls_watchers_pkey PRIMARY KEY (id);


--
-- Name: rls_watchers rls_watchers_rls_watcher_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.rls_watchers
    ADD CONSTRAINT rls_watchers_rls_watcher_idx UNIQUE (callid, to_tag, from_tag);


--
-- Name: rtpproxy rtpproxy_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.rtpproxy
    ADD CONSTRAINT rtpproxy_pkey PRIMARY KEY (id);


--
-- Name: sca_subscriptions sca_subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.sca_subscriptions
    ADD CONSTRAINT sca_subscriptions_pkey PRIMARY KEY (id);


--
-- Name: sca_subscriptions sca_subscriptions_sca_subscriptions_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.sca_subscriptions
    ADD CONSTRAINT sca_subscriptions_sca_subscriptions_idx UNIQUE (subscriber, call_id, from_tag, to_tag);


--
-- Name: silo silo_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.silo
    ADD CONSTRAINT silo_pkey PRIMARY KEY (id);


--
-- Name: sip_trace sip_trace_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.sip_trace
    ADD CONSTRAINT sip_trace_pkey PRIMARY KEY (id);


--
-- Name: speed_dial speed_dial_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.speed_dial
    ADD CONSTRAINT speed_dial_pkey PRIMARY KEY (id);


--
-- Name: speed_dial speed_dial_speed_dial_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.speed_dial
    ADD CONSTRAINT speed_dial_speed_dial_idx UNIQUE (username, domain, sd_domain, sd_username);


--
-- Name: subscriber subscriber_account_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.subscriber
    ADD CONSTRAINT subscriber_account_idx UNIQUE (username, domain);


--
-- Name: subscriber subscriber_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.subscriber
    ADD CONSTRAINT subscriber_pkey PRIMARY KEY (id);


--
-- Name: topos_d topos_d_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.topos_d
    ADD CONSTRAINT topos_d_pkey PRIMARY KEY (id);


--
-- Name: topos_t topos_t_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.topos_t
    ADD CONSTRAINT topos_t_pkey PRIMARY KEY (id);


--
-- Name: trusted trusted_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.trusted
    ADD CONSTRAINT trusted_pkey PRIMARY KEY (id);


--
-- Name: uacreg uacreg_l_uuid_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.uacreg
    ADD CONSTRAINT uacreg_l_uuid_idx UNIQUE (l_uuid);


--
-- Name: uacreg uacreg_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.uacreg
    ADD CONSTRAINT uacreg_pkey PRIMARY KEY (id);


--
-- Name: uri uri_account_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.uri
    ADD CONSTRAINT uri_account_idx UNIQUE (username, domain, uri_user);


--
-- Name: uri uri_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.uri
    ADD CONSTRAINT uri_pkey PRIMARY KEY (id);


--
-- Name: userblacklist userblacklist_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.userblacklist
    ADD CONSTRAINT userblacklist_pkey PRIMARY KEY (id);


--
-- Name: usr_preferences usr_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.usr_preferences
    ADD CONSTRAINT usr_preferences_pkey PRIMARY KEY (id);


--
-- Name: version version_table_name_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.version
    ADD CONSTRAINT version_table_name_idx UNIQUE (table_name);


--
-- Name: watchers watchers_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.watchers
    ADD CONSTRAINT watchers_pkey PRIMARY KEY (id);


--
-- Name: watchers watchers_watcher_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.watchers
    ADD CONSTRAINT watchers_watcher_idx UNIQUE (presentity_uri, watcher_username, watcher_domain, event);


--
-- Name: xcap xcap_doc_uri_idx; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.xcap
    ADD CONSTRAINT xcap_doc_uri_idx UNIQUE (doc_uri);


--
-- Name: xcap xcap_pkey; Type: CONSTRAINT; Schema: public; Owner: omnileads
--

ALTER TABLE ONLY public.xcap
    ADD CONSTRAINT xcap_pkey PRIMARY KEY (id);


--
-- Name: acc_callid_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX acc_callid_idx ON public.acc USING btree (callid);


--
-- Name: acc_cdrs_start_time_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX acc_cdrs_start_time_idx ON public.acc_cdrs USING btree (start_time);


--
-- Name: active_watchers_active_watchers_expires; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX active_watchers_active_watchers_expires ON public.active_watchers USING btree (expires);


--
-- Name: active_watchers_active_watchers_pres; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX active_watchers_active_watchers_pres ON public.active_watchers USING btree (presentity_uri, event);


--
-- Name: active_watchers_updated_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX active_watchers_updated_idx ON public.active_watchers USING btree (updated);


--
-- Name: active_watchers_updated_winfo_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX active_watchers_updated_winfo_idx ON public.active_watchers USING btree (updated_winfo, presentity_uri);


--
-- Name: aliases_account_contact_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX aliases_account_contact_idx ON public.aliases USING btree (username, domain, contact);


--
-- Name: aliases_expires_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX aliases_expires_idx ON public.aliases USING btree (expires);


--
-- Name: dbaliases_alias_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX dbaliases_alias_idx ON public.dbaliases USING btree (alias_username, alias_domain);


--
-- Name: dbaliases_alias_user_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX dbaliases_alias_user_idx ON public.dbaliases USING btree (alias_username);


--
-- Name: dbaliases_target_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX dbaliases_target_idx ON public.dbaliases USING btree (username, domain);


--
-- Name: dialog_hash_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX dialog_hash_idx ON public.dialog USING btree (hash_entry, hash_id);


--
-- Name: dialog_vars_hash_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX dialog_vars_hash_idx ON public.dialog_vars USING btree (hash_entry, hash_id);


--
-- Name: domainpolicy_rule_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX domainpolicy_rule_idx ON public.domainpolicy USING btree (rule);


--
-- Name: globalblacklist_globalblacklist_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX globalblacklist_globalblacklist_idx ON public.globalblacklist USING btree (prefix);


--
-- Name: lcr_gw_lcr_id_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX lcr_gw_lcr_id_idx ON public.lcr_gw USING btree (lcr_id);


--
-- Name: lcr_rule_target_lcr_id_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX lcr_rule_target_lcr_id_idx ON public.lcr_rule_target USING btree (lcr_id);


--
-- Name: location_account_contact_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX location_account_contact_idx ON public.location USING btree (username, domain, contact);


--
-- Name: location_attrs_account_record_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX location_attrs_account_record_idx ON public.location_attrs USING btree (username, domain, ruid);


--
-- Name: location_attrs_last_modified_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX location_attrs_last_modified_idx ON public.location_attrs USING btree (last_modified);


--
-- Name: location_connection_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX location_connection_idx ON public.location USING btree (server_id, connection_id);


--
-- Name: location_expires_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX location_expires_idx ON public.location USING btree (expires);


--
-- Name: missed_calls_callid_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX missed_calls_callid_idx ON public.missed_calls USING btree (callid);


--
-- Name: presentity_account_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX presentity_account_idx ON public.presentity USING btree (username, domain, event);


--
-- Name: presentity_presentity_expires; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX presentity_presentity_expires ON public.presentity USING btree (expires);


--
-- Name: pua_dialog1_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX pua_dialog1_idx ON public.pua USING btree (pres_id, pres_uri);


--
-- Name: pua_dialog2_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX pua_dialog2_idx ON public.pua USING btree (call_id, from_tag);


--
-- Name: pua_expires_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX pua_expires_idx ON public.pua USING btree (expires);


--
-- Name: pua_record_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX pua_record_idx ON public.pua USING btree (pres_id);


--
-- Name: re_grp_group_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX re_grp_group_idx ON public.re_grp USING btree (group_id);


--
-- Name: rls_presentity_expires_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX rls_presentity_expires_idx ON public.rls_presentity USING btree (expires);


--
-- Name: rls_presentity_rlsubs_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX rls_presentity_rlsubs_idx ON public.rls_presentity USING btree (rlsubs_did);


--
-- Name: rls_presentity_updated_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX rls_presentity_updated_idx ON public.rls_presentity USING btree (updated);


--
-- Name: rls_watchers_rls_watchers_expires; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX rls_watchers_rls_watchers_expires ON public.rls_watchers USING btree (expires);


--
-- Name: rls_watchers_rls_watchers_update; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX rls_watchers_rls_watchers_update ON public.rls_watchers USING btree (watcher_username, watcher_domain, event);


--
-- Name: rls_watchers_updated_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX rls_watchers_updated_idx ON public.rls_watchers USING btree (updated);


--
-- Name: sca_subscriptions_sca_expires_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX sca_subscriptions_sca_expires_idx ON public.sca_subscriptions USING btree (expires);


--
-- Name: sca_subscriptions_sca_subscribers_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX sca_subscriptions_sca_subscribers_idx ON public.sca_subscriptions USING btree (subscriber, event);


--
-- Name: silo_account_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX silo_account_idx ON public.silo USING btree (username, domain);


--
-- Name: sip_trace_callid_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX sip_trace_callid_idx ON public.sip_trace USING btree (callid);


--
-- Name: sip_trace_date_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX sip_trace_date_idx ON public.sip_trace USING btree (time_stamp);


--
-- Name: sip_trace_fromip_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX sip_trace_fromip_idx ON public.sip_trace USING btree (fromip);


--
-- Name: sip_trace_traced_user_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX sip_trace_traced_user_idx ON public.sip_trace USING btree (traced_user);


--
-- Name: subscriber_username_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX subscriber_username_idx ON public.subscriber USING btree (username);


--
-- Name: topos_d_a_callid_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX topos_d_a_callid_idx ON public.topos_d USING btree (a_callid);


--
-- Name: topos_d_rectime_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX topos_d_rectime_idx ON public.topos_d USING btree (rectime);


--
-- Name: topos_t_a_callid_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX topos_t_a_callid_idx ON public.topos_t USING btree (a_callid);


--
-- Name: topos_t_rectime_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX topos_t_rectime_idx ON public.topos_t USING btree (rectime);


--
-- Name: trusted_peer_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX trusted_peer_idx ON public.trusted USING btree (src_ip);


--
-- Name: userblacklist_userblacklist_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX userblacklist_userblacklist_idx ON public.userblacklist USING btree (username, domain, prefix);


--
-- Name: usr_preferences_ua_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX usr_preferences_ua_idx ON public.usr_preferences USING btree (uuid, attribute);


--
-- Name: usr_preferences_uda_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX usr_preferences_uda_idx ON public.usr_preferences USING btree (username, domain, attribute);


--
-- Name: xcap_account_doc_type_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX xcap_account_doc_type_idx ON public.xcap USING btree (username, domain, doc_type);


--
-- Name: xcap_account_doc_type_uri_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX xcap_account_doc_type_uri_idx ON public.xcap USING btree (username, domain, doc_type, doc_uri);


--
-- Name: xcap_account_doc_uri_idx; Type: INDEX; Schema: public; Owner: omnileads
--

CREATE INDEX xcap_account_doc_uri_idx ON public.xcap USING btree (username, domain, doc_uri);


--
-- Name: TABLE acc; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.acc TO kamailioro;


--
-- Name: TABLE acc_cdrs; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.acc_cdrs TO kamailioro;


--
-- Name: SEQUENCE acc_cdrs_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.acc_cdrs_id_seq TO kamailioro;


--
-- Name: SEQUENCE acc_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.acc_id_seq TO kamailioro;


--
-- Name: TABLE active_watchers; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.active_watchers TO kamailioro;


--
-- Name: SEQUENCE active_watchers_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.active_watchers_id_seq TO kamailioro;


--
-- Name: TABLE address; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.address TO kamailioro;


--
-- Name: SEQUENCE address_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.address_id_seq TO kamailioro;


--
-- Name: TABLE aliases; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.aliases TO kamailioro;


--
-- Name: SEQUENCE aliases_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.aliases_id_seq TO kamailioro;


--
-- Name: TABLE carrier_name; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.carrier_name TO kamailioro;


--
-- Name: SEQUENCE carrier_name_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.carrier_name_id_seq TO kamailioro;


--
-- Name: TABLE carrierfailureroute; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.carrierfailureroute TO kamailioro;


--
-- Name: SEQUENCE carrierfailureroute_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.carrierfailureroute_id_seq TO kamailioro;


--
-- Name: TABLE carrierroute; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.carrierroute TO kamailioro;


--
-- Name: SEQUENCE carrierroute_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.carrierroute_id_seq TO kamailioro;


--
-- Name: TABLE cpl; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.cpl TO kamailioro;


--
-- Name: SEQUENCE cpl_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.cpl_id_seq TO kamailioro;


--
-- Name: TABLE dbaliases; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.dbaliases TO kamailioro;


--
-- Name: SEQUENCE dbaliases_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.dbaliases_id_seq TO kamailioro;


--
-- Name: TABLE dialog; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.dialog TO kamailioro;


--
-- Name: SEQUENCE dialog_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.dialog_id_seq TO kamailioro;


--
-- Name: TABLE dialog_vars; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.dialog_vars TO kamailioro;


--
-- Name: SEQUENCE dialog_vars_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.dialog_vars_id_seq TO kamailioro;


--
-- Name: TABLE dialplan; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.dialplan TO kamailioro;


--
-- Name: SEQUENCE dialplan_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.dialplan_id_seq TO kamailioro;


--
-- Name: TABLE dispatcher; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.dispatcher TO kamailioro;


--
-- Name: SEQUENCE dispatcher_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.dispatcher_id_seq TO kamailioro;


--
-- Name: TABLE domain; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.domain TO kamailioro;


--
-- Name: TABLE domain_attrs; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.domain_attrs TO kamailioro;


--
-- Name: SEQUENCE domain_attrs_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.domain_attrs_id_seq TO kamailioro;


--
-- Name: SEQUENCE domain_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.domain_id_seq TO kamailioro;


--
-- Name: TABLE domain_name; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.domain_name TO kamailioro;


--
-- Name: SEQUENCE domain_name_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.domain_name_id_seq TO kamailioro;


--
-- Name: TABLE domainpolicy; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.domainpolicy TO kamailioro;


--
-- Name: SEQUENCE domainpolicy_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.domainpolicy_id_seq TO kamailioro;


--
-- Name: TABLE dr_gateways; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.dr_gateways TO kamailioro;


--
-- Name: TABLE globalblacklist; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.globalblacklist TO kamailioro;


--
-- Name: SEQUENCE globalblacklist_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.globalblacklist_id_seq TO kamailioro;


--
-- Name: TABLE grp; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.grp TO kamailioro;


--
-- Name: SEQUENCE grp_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.grp_id_seq TO kamailioro;


--
-- Name: TABLE htable; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.htable TO kamailioro;


--
-- Name: SEQUENCE htable_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.htable_id_seq TO kamailioro;


--
-- Name: TABLE imc_members; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.imc_members TO kamailioro;


--
-- Name: SEQUENCE imc_members_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.imc_members_id_seq TO kamailioro;


--
-- Name: TABLE imc_rooms; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.imc_rooms TO kamailioro;


--
-- Name: SEQUENCE imc_rooms_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.imc_rooms_id_seq TO kamailioro;


--
-- Name: TABLE lcr_gw; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.lcr_gw TO kamailioro;


--
-- Name: SEQUENCE lcr_gw_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.lcr_gw_id_seq TO kamailioro;


--
-- Name: TABLE lcr_rule; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.lcr_rule TO kamailioro;


--
-- Name: SEQUENCE lcr_rule_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.lcr_rule_id_seq TO kamailioro;


--
-- Name: TABLE lcr_rule_target; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.lcr_rule_target TO kamailioro;


--
-- Name: SEQUENCE lcr_rule_target_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.lcr_rule_target_id_seq TO kamailioro;


--
-- Name: TABLE location; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.location TO kamailioro;


--
-- Name: TABLE location_attrs; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.location_attrs TO kamailioro;


--
-- Name: SEQUENCE location_attrs_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.location_attrs_id_seq TO kamailioro;


--
-- Name: SEQUENCE location_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.location_id_seq TO kamailioro;


--
-- Name: TABLE missed_calls; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.missed_calls TO kamailioro;


--
-- Name: SEQUENCE missed_calls_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.missed_calls_id_seq TO kamailioro;


--
-- Name: TABLE mohqcalls; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.mohqcalls TO kamailioro;


--
-- Name: SEQUENCE mohqcalls_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.mohqcalls_id_seq TO kamailioro;


--
-- Name: TABLE mohqueues; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.mohqueues TO kamailioro;


--
-- Name: SEQUENCE mohqueues_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.mohqueues_id_seq TO kamailioro;


--
-- Name: TABLE mtree; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.mtree TO kamailioro;


--
-- Name: SEQUENCE mtree_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.mtree_id_seq TO kamailioro;


--
-- Name: TABLE mtrees; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.mtrees TO kamailioro;


--
-- Name: SEQUENCE mtrees_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.mtrees_id_seq TO kamailioro;


--
-- Name: TABLE pdt; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.pdt TO kamailioro;


--
-- Name: SEQUENCE pdt_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.pdt_id_seq TO kamailioro;


--
-- Name: TABLE pl_pipes; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.pl_pipes TO kamailioro;


--
-- Name: SEQUENCE pl_pipes_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.pl_pipes_id_seq TO kamailioro;


--
-- Name: TABLE presentity; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.presentity TO kamailioro;


--
-- Name: SEQUENCE presentity_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.presentity_id_seq TO kamailioro;


--
-- Name: TABLE pua; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.pua TO kamailioro;


--
-- Name: SEQUENCE pua_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.pua_id_seq TO kamailioro;


--
-- Name: TABLE purplemap; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.purplemap TO kamailioro;


--
-- Name: SEQUENCE purplemap_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.purplemap_id_seq TO kamailioro;


--
-- Name: TABLE re_grp; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.re_grp TO kamailioro;


--
-- Name: SEQUENCE re_grp_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.re_grp_id_seq TO kamailioro;


--
-- Name: TABLE rls_presentity; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.rls_presentity TO kamailioro;


--
-- Name: SEQUENCE rls_presentity_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.rls_presentity_id_seq TO kamailioro;


--
-- Name: TABLE rls_watchers; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.rls_watchers TO kamailioro;


--
-- Name: SEQUENCE rls_watchers_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.rls_watchers_id_seq TO kamailioro;


--
-- Name: TABLE rtpproxy; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.rtpproxy TO kamailioro;


--
-- Name: SEQUENCE rtpproxy_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.rtpproxy_id_seq TO kamailioro;


--
-- Name: TABLE sca_subscriptions; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.sca_subscriptions TO kamailioro;


--
-- Name: SEQUENCE sca_subscriptions_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.sca_subscriptions_id_seq TO kamailioro;


--
-- Name: TABLE silo; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.silo TO kamailioro;


--
-- Name: SEQUENCE silo_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.silo_id_seq TO kamailioro;


--
-- Name: TABLE sip_trace; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.sip_trace TO kamailioro;


--
-- Name: SEQUENCE sip_trace_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.sip_trace_id_seq TO kamailioro;


--
-- Name: TABLE speed_dial; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.speed_dial TO kamailioro;


--
-- Name: SEQUENCE speed_dial_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.speed_dial_id_seq TO kamailioro;


--
-- Name: TABLE subscriber; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.subscriber TO kamailioro;


--
-- Name: SEQUENCE subscriber_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.subscriber_id_seq TO kamailioro;


--
-- Name: TABLE topos_d; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.topos_d TO kamailioro;


--
-- Name: SEQUENCE topos_d_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.topos_d_id_seq TO kamailioro;


--
-- Name: TABLE topos_t; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.topos_t TO kamailioro;


--
-- Name: SEQUENCE topos_t_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.topos_t_id_seq TO kamailioro;


--
-- Name: TABLE trusted; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.trusted TO kamailioro;


--
-- Name: SEQUENCE trusted_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.trusted_id_seq TO kamailioro;


--
-- Name: TABLE uacreg; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.uacreg TO kamailioro;


--
-- Name: SEQUENCE uacreg_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.uacreg_id_seq TO kamailioro;


--
-- Name: TABLE uri; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.uri TO kamailioro;


--
-- Name: SEQUENCE uri_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.uri_id_seq TO kamailioro;


--
-- Name: TABLE userblacklist; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.userblacklist TO kamailioro;


--
-- Name: SEQUENCE userblacklist_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.userblacklist_id_seq TO kamailioro;


--
-- Name: TABLE usr_preferences; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.usr_preferences TO kamailioro;


--
-- Name: SEQUENCE usr_preferences_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.usr_preferences_id_seq TO kamailioro;


--
-- Name: TABLE version; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.version TO kamailioro;


--
-- Name: TABLE watchers; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.watchers TO kamailioro;


--
-- Name: SEQUENCE watchers_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.watchers_id_seq TO kamailioro;


--
-- Name: TABLE xcap; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON TABLE public.xcap TO kamailioro;


--
-- Name: SEQUENCE xcap_id_seq; Type: ACL; Schema: public; Owner: omnileads
--

GRANT SELECT ON SEQUENCE public.xcap_id_seq TO kamailioro;


--
-- PostgreSQL database dump complete
--

