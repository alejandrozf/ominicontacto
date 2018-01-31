--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

ALTER TABLE ONLY public.queue_table DROP CONSTRAINT queue_table_campana_id_be72b1c4_fk_ominicontacto_app_campana_id;
ALTER TABLE ONLY public.queue_member_table DROP CONSTRAINT queue_member_table_queue_name_cc6b888a_fk_queue_table_name;
ALTER TABLE ONLY public.queue_member_table DROP CONSTRAINT queue__member_id_0e6c0aa5_fk_ominicontacto_app_agenteprofile_id;
ALTER TABLE ONLY public.ominicontacto_app_agenteprofile_modulos DROP CONSTRAINT ominicontacto_modulo_id_adce0149_fk_ominicontacto_app_modulo_id;
ALTER TABLE ONLY public.ominicontacto_app_user_groups DROP CONSTRAINT ominicontacto_app_user_id_9520c89f_fk_ominicontacto_app_user_id;
ALTER TABLE ONLY public.ominicontacto_app_chat DROP CONSTRAINT ominicontacto_app_user_id_7e593d05_fk_ominicontacto_app_user_id;
ALTER TABLE ONLY public.ominicontacto_app_user_user_permissions DROP CONSTRAINT ominicontacto_app_user_id_4412e21b_fk_ominicontacto_app_user_id;
ALTER TABLE ONLY public.ominicontacto_app_agenteprofile DROP CONSTRAINT ominicontacto_app_user_id_0e446b03_fk_ominicontacto_app_user_id;
ALTER TABLE ONLY public.ominicontacto_app_user_groups DROP CONSTRAINT ominicontacto_app_user_group_group_id_f47e61a0_fk_auth_group_id;
ALTER TABLE ONLY public.ominicontacto_app_mensajechat DROP CONSTRAINT ominicontacto_app_m_to_id_a5f7aa2c_fk_ominicontacto_app_user_id;
ALTER TABLE ONLY public.ominicontacto_app_mensajechat DROP CONSTRAINT ominicontacto_app_chat_id_3845da5b_fk_ominicontacto_app_chat_id;
ALTER TABLE ONLY public.ominicontacto_app_user_user_permissions DROP CONSTRAINT ominicontacto_app__permission_id_43f9ab68_fk_auth_permission_id;
ALTER TABLE ONLY public.ominicontacto_app_mensajechat DROP CONSTRAINT ominicontacto_a_sender_id_49a6c90d_fk_ominicontacto_app_user_id;
ALTER TABLE ONLY public.ominicontacto_app_agenteprofile DROP CONSTRAINT ominicontacto_a_grupo_id_474dfc5a_fk_ominicontacto_app_grupo_id;
ALTER TABLE ONLY public.ominicontacto_app_grabacion DROP CONSTRAINT ominicontac_campana_id_fdebc53b_fk_ominicontacto_app_campana_id;
ALTER TABLE ONLY public.ominicontacto_app_metadatacliente DROP CONSTRAINT ominicontac_campana_id_cbd5c9f1_fk_ominicontacto_app_campana_id;
ALTER TABLE ONLY public.ominicontacto_app_wombatlog DROP CONSTRAINT ominicontac_campana_id_a6c9c717_fk_ominicontacto_app_campana_id;
ALTER TABLE ONLY public.ominicontacto_app_calificacioncliente DROP CONSTRAINT ominicontac_campana_id_0392f548_fk_ominicontacto_app_campana_id;
ALTER TABLE ONLY public.ominicontacto_app_calificacioncliente DROP CONSTRAINT ominicont_contacto_id_e5df4663_fk_ominicontacto_app_contacto_id;
ALTER TABLE ONLY public.ominicontacto_app_metadatacliente DROP CONSTRAINT ominicont_contacto_id_8edc7340_fk_ominicontacto_app_contacto_id;
ALTER TABLE ONLY public.ominicontacto_app_wombatlog DROP CONSTRAINT ominicont_contacto_id_7b0281c2_fk_ominicontacto_app_contacto_id;
ALTER TABLE ONLY public.ominicontacto_app_chat DROP CONSTRAINT ominic_agente_id_b0b74e82_fk_ominicontacto_app_agenteprofile_id;
ALTER TABLE ONLY public.ominicontacto_app_agenda DROP CONSTRAINT ominic_agente_id_6baadc27_fk_ominicontacto_app_agenteprofile_id;
ALTER TABLE ONLY public.ominicontacto_app_duraciondellamada DROP CONSTRAINT ominic_agente_id_341aa330_fk_ominicontacto_app_agenteprofile_id;
ALTER TABLE ONLY public.ominicontacto_app_metadatacliente DROP CONSTRAINT ominic_agente_id_32c1d2d4_fk_ominicontacto_app_agenteprofile_id;
ALTER TABLE ONLY public.ominicontacto_app_wombatlog DROP CONSTRAINT ominic_agente_id_15e63fce_fk_ominicontacto_app_agenteprofile_id;
ALTER TABLE ONLY public.ominicontacto_app_calificacioncliente DROP CONSTRAINT ominic_agente_id_1070b434_fk_ominicontacto_app_agenteprofile_id;
ALTER TABLE ONLY public.ominicontacto_app_fieldformulario DROP CONSTRAINT omini_formulario_id_b5355e5d_fk_ominicontacto_app_formulario_id;
ALTER TABLE ONLY public.ominicontacto_app_campana DROP CONSTRAINT omini_formulario_id_0184bc8d_fk_ominicontacto_app_formulario_id;
ALTER TABLE ONLY public.ominicontacto_app_calificacioncampana_calificacion DROP CONSTRAINT o_calificacion_id_e56288ab_fk_ominicontacto_app_calificacion_id;
ALTER TABLE ONLY public.ominicontacto_app_calificacioncliente DROP CONSTRAINT o_calificacion_id_73b5d2c5_fk_ominicontacto_app_calificacion_id;
ALTER TABLE ONLY public.mensaje_enviado DROP CONSTRAINT mensaj_agente_id_de9cfeb5_fk_ominicontacto_app_agenteprofile_id;
ALTER TABLE ONLY public.ominicontacto_app_calificacioncampana_calificacion DROP CONSTRAINT e81ed6bab1cb48461414d88108216e55;
ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT django_admin_log_user_id_c564eba6_fk_ominicontacto_app_user_id;
ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT django_admin_content_type_id_c4bce8eb_fk_django_content_type_id;
ALTER TABLE ONLY public.ominicontacto_app_campana DROP CONSTRAINT ca685487dc3a9bf18d5e9e0fd006bf67;
ALTER TABLE ONLY public.auth_permission DROP CONSTRAINT auth_permiss_content_type_id_2f476e4b_fk_django_content_type_id;
ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id;
ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permiss_permission_id_84c5c92e_fk_auth_permission_id;
ALTER TABLE ONLY public.ominicontacto_app_agenteprofile_modulos DROP CONSTRAINT "D8da2b3b45492920f6ec709e3b513e07";
ALTER TABLE ONLY public.ominicontacto_app_campana DROP CONSTRAINT "D790090bf77bd6ae57bbcd278f80b4bf";
ALTER TABLE ONLY public.ominicontacto_app_contacto DROP CONSTRAINT "D6d2e47c11d2fb8d7243f5dbb136c9e3";
DROP INDEX public.xcap_account_doc_uri_idx;
DROP INDEX public.xcap_account_doc_type_uri_idx;
DROP INDEX public.xcap_account_doc_type_idx;
DROP INDEX public.usr_preferences_uda_idx;
DROP INDEX public.usr_preferences_ua_idx;
DROP INDEX public.userblacklist_userblacklist_idx;
DROP INDEX public.trusted_peer_idx;
DROP INDEX public.topos_t_rectime_idx;
DROP INDEX public.topos_t_a_callid_idx;
DROP INDEX public.topos_d_rectime_idx;
DROP INDEX public.topos_d_a_callid_idx;
DROP INDEX public.subscriber_username_idx;
DROP INDEX public.sip_trace_traced_user_idx;
DROP INDEX public.sip_trace_fromip_idx;
DROP INDEX public.sip_trace_date_idx;
DROP INDEX public.sip_trace_callid_idx;
DROP INDEX public.silo_account_idx;
DROP INDEX public.sca_subscriptions_sca_subscribers_idx;
DROP INDEX public.sca_subscriptions_sca_expires_idx;
DROP INDEX public.rls_watchers_updated_idx;
DROP INDEX public.rls_watchers_rls_watchers_update;
DROP INDEX public.rls_watchers_rls_watchers_expires;
DROP INDEX public.rls_presentity_updated_idx;
DROP INDEX public.rls_presentity_rlsubs_idx;
DROP INDEX public.rls_presentity_expires_idx;
DROP INDEX public.re_grp_group_idx;
DROP INDEX public.queue_table_name_495baf91_like;
DROP INDEX public.queue_member_table_queue_id_996b3794_like;
DROP INDEX public.queue_member_table_b5c3e75b;
DROP INDEX public.queue_member_table_75249aa1;
DROP INDEX public.pua_record_idx;
DROP INDEX public.pua_expires_idx;
DROP INDEX public.pua_dialog2_idx;
DROP INDEX public.pua_dialog1_idx;
DROP INDEX public.presentity_presentity_expires;
DROP INDEX public.presentity_account_idx;
DROP INDEX public.ominicontacto_app_wombatlog_debcd608;
DROP INDEX public.ominicontacto_app_wombatlog_66683d76;
DROP INDEX public.ominicontacto_app_wombatlog_32400660;
DROP INDEX public.ominicontacto_app_user_username_3223b7ba_like;
DROP INDEX public.ominicontacto_app_user_user_permissions_e8701ad4;
DROP INDEX public.ominicontacto_app_user_user_permissions_8373b171;
DROP INDEX public.ominicontacto_app_user_groups_e8701ad4;
DROP INDEX public.ominicontacto_app_user_groups_0e939a4f;
DROP INDEX public.ominicontacto_app_metadatacliente_66683d76;
DROP INDEX public.ominicontacto_app_metadatacliente_32400660;
DROP INDEX public.ominicontacto_app_mensajechat_f4b39993;
DROP INDEX public.ominicontacto_app_mensajechat_b79bfa8f;
DROP INDEX public.ominicontacto_app_mensajechat_924b1846;
DROP INDEX public.ominicontacto_app_grabacion_campana_id_fdebc53b_uniq;
DROP INDEX public.ominicontacto_app_fieldformulario_3fe51010;
DROP INDEX public.ominicontacto_app_duraciondellamada_32400660;
DROP INDEX public.ominicontacto_app_contacto_368d6ace;
DROP INDEX public.ominicontacto_app_chat_e8701ad4;
DROP INDEX public.ominicontacto_app_chat_32400660;
DROP INDEX public.ominicontacto_app_campana_60530197;
DROP INDEX public.ominicontacto_app_campana_3fe51010;
DROP INDEX public.ominicontacto_app_campana_368d6ace;
DROP INDEX public.ominicontacto_app_calificacioncliente_66683d76;
DROP INDEX public.ominicontacto_app_calificacioncliente_36aa9691;
DROP INDEX public.ominicontacto_app_calificacioncliente_32400660;
DROP INDEX public.ominicontacto_app_calificacioncampana_calificacion_7f1db41a;
DROP INDEX public.ominicontacto_app_calificacioncampana_calificacion_36aa9691;
DROP INDEX public.ominicontacto_app_agenteprofile_modulos_bfd9a2cb;
DROP INDEX public.ominicontacto_app_agenteprofile_modulos_7ba91c57;
DROP INDEX public.ominicontacto_app_agenteprofile_acaeb2d6;
DROP INDEX public.ominicontacto_app_agenda_32400660;
DROP INDEX public.missed_calls_callid_idx;
DROP INDEX public.mensaje_enviado_32400660;
DROP INDEX public.location_expires_idx;
DROP INDEX public.location_connection_idx;
DROP INDEX public.location_attrs_last_modified_idx;
DROP INDEX public.location_attrs_account_record_idx;
DROP INDEX public.location_account_contact_idx;
DROP INDEX public.lcr_rule_target_lcr_id_idx;
DROP INDEX public.lcr_gw_lcr_id_idx;
DROP INDEX public.globalblacklist_globalblacklist_idx;
DROP INDEX public.domainpolicy_rule_idx;
DROP INDEX public.django_admin_log_e8701ad4;
DROP INDEX public.django_admin_log_417f1b1c;
DROP INDEX public.dialog_vars_hash_idx;
DROP INDEX public.dialog_hash_idx;
DROP INDEX public.dbaliases_target_idx;
DROP INDEX public.dbaliases_alias_user_idx;
DROP INDEX public.dbaliases_alias_idx;
DROP INDEX public.auth_permission_417f1b1c;
DROP INDEX public.auth_group_permissions_8373b171;
DROP INDEX public.auth_group_permissions_0e939a4f;
DROP INDEX public.auth_group_name_a6ea08ec_like;
DROP INDEX public.aliases_expires_idx;
DROP INDEX public.aliases_account_contact_idx;
DROP INDEX public.active_watchers_updated_winfo_idx;
DROP INDEX public.active_watchers_updated_idx;
DROP INDEX public.active_watchers_active_watchers_pres;
DROP INDEX public.active_watchers_active_watchers_expires;
DROP INDEX public.acc_cdrs_start_time_idx;
DROP INDEX public.acc_callid_idx;
ALTER TABLE ONLY public.xcap DROP CONSTRAINT xcap_pkey;
ALTER TABLE ONLY public.xcap DROP CONSTRAINT xcap_doc_uri_idx;
ALTER TABLE ONLY public.watchers DROP CONSTRAINT watchers_watcher_idx;
ALTER TABLE ONLY public.watchers DROP CONSTRAINT watchers_pkey;
ALTER TABLE ONLY public.version DROP CONSTRAINT version_table_name_idx;
ALTER TABLE ONLY public.usr_preferences DROP CONSTRAINT usr_preferences_pkey;
ALTER TABLE ONLY public.userblacklist DROP CONSTRAINT userblacklist_pkey;
ALTER TABLE ONLY public.uri DROP CONSTRAINT uri_pkey;
ALTER TABLE ONLY public.uri DROP CONSTRAINT uri_account_idx;
ALTER TABLE ONLY public.uacreg DROP CONSTRAINT uacreg_pkey;
ALTER TABLE ONLY public.uacreg DROP CONSTRAINT uacreg_l_uuid_idx;
ALTER TABLE ONLY public.trusted DROP CONSTRAINT trusted_pkey;
ALTER TABLE ONLY public.topos_t DROP CONSTRAINT topos_t_pkey;
ALTER TABLE ONLY public.topos_d DROP CONSTRAINT topos_d_pkey;
ALTER TABLE ONLY public.subscriber DROP CONSTRAINT subscriber_pkey;
ALTER TABLE ONLY public.subscriber DROP CONSTRAINT subscriber_account_idx;
ALTER TABLE ONLY public.speed_dial DROP CONSTRAINT speed_dial_speed_dial_idx;
ALTER TABLE ONLY public.speed_dial DROP CONSTRAINT speed_dial_pkey;
ALTER TABLE ONLY public.sip_trace DROP CONSTRAINT sip_trace_pkey;
ALTER TABLE ONLY public.silo DROP CONSTRAINT silo_pkey;
ALTER TABLE ONLY public.sca_subscriptions DROP CONSTRAINT sca_subscriptions_sca_subscriptions_idx;
ALTER TABLE ONLY public.sca_subscriptions DROP CONSTRAINT sca_subscriptions_pkey;
ALTER TABLE ONLY public.rtpproxy DROP CONSTRAINT rtpproxy_pkey;
ALTER TABLE ONLY public.rls_watchers DROP CONSTRAINT rls_watchers_rls_watcher_idx;
ALTER TABLE ONLY public.rls_watchers DROP CONSTRAINT rls_watchers_pkey;
ALTER TABLE ONLY public.rls_presentity DROP CONSTRAINT rls_presentity_rls_presentity_idx;
ALTER TABLE ONLY public.rls_presentity DROP CONSTRAINT rls_presentity_pkey;
ALTER TABLE ONLY public.re_grp DROP CONSTRAINT re_grp_pkey;
ALTER TABLE ONLY public.queue_table DROP CONSTRAINT queue_table_queue_asterisk_key;
ALTER TABLE ONLY public.queue_table DROP CONSTRAINT queue_table_pkey;
ALTER TABLE ONLY public.queue_table DROP CONSTRAINT queue_table_campana_id_key;
ALTER TABLE ONLY public.queue_member_table DROP CONSTRAINT queue_member_table_queue_name_1e319083_uniq;
ALTER TABLE ONLY public.queue_member_table DROP CONSTRAINT queue_member_table_pkey;
ALTER TABLE ONLY public.purplemap DROP CONSTRAINT purplemap_pkey;
ALTER TABLE ONLY public.pua DROP CONSTRAINT pua_pua_idx;
ALTER TABLE ONLY public.pua DROP CONSTRAINT pua_pkey;
ALTER TABLE ONLY public.presentity DROP CONSTRAINT presentity_presentity_idx;
ALTER TABLE ONLY public.presentity DROP CONSTRAINT presentity_pkey;
ALTER TABLE ONLY public.pl_pipes DROP CONSTRAINT pl_pipes_pkey;
ALTER TABLE ONLY public.pdt DROP CONSTRAINT pdt_sdomain_prefix_idx;
ALTER TABLE ONLY public.pdt DROP CONSTRAINT pdt_pkey;
ALTER TABLE ONLY public.ominicontacto_app_wombatlog DROP CONSTRAINT ominicontacto_app_wombatlog_pkey;
ALTER TABLE ONLY public.ominicontacto_app_user DROP CONSTRAINT ominicontacto_app_user_username_key;
ALTER TABLE ONLY public.ominicontacto_app_user_user_permissions DROP CONSTRAINT ominicontacto_app_user_user_permissions_user_id_c7a8cf96_uniq;
ALTER TABLE ONLY public.ominicontacto_app_user_user_permissions DROP CONSTRAINT ominicontacto_app_user_user_permissions_pkey;
ALTER TABLE ONLY public.ominicontacto_app_user DROP CONSTRAINT ominicontacto_app_user_pkey;
ALTER TABLE ONLY public.ominicontacto_app_user_groups DROP CONSTRAINT ominicontacto_app_user_groups_user_id_9ea58fa3_uniq;
ALTER TABLE ONLY public.ominicontacto_app_user_groups DROP CONSTRAINT ominicontacto_app_user_groups_pkey;
ALTER TABLE ONLY public.ominicontacto_app_queuelog DROP CONSTRAINT ominicontacto_app_queuelog_pkey;
ALTER TABLE ONLY public.ominicontacto_app_pausa DROP CONSTRAINT ominicontacto_app_pausa_pkey;
ALTER TABLE ONLY public.ominicontacto_app_modulo DROP CONSTRAINT ominicontacto_app_modulo_pkey;
ALTER TABLE ONLY public.ominicontacto_app_metadatacliente DROP CONSTRAINT ominicontacto_app_metadatacliente_pkey;
ALTER TABLE ONLY public.ominicontacto_app_mensajechat DROP CONSTRAINT ominicontacto_app_mensajechat_pkey;
ALTER TABLE ONLY public.ominicontacto_app_grupo DROP CONSTRAINT ominicontacto_app_grupo_pkey;
ALTER TABLE ONLY public.ominicontacto_app_grabacion DROP CONSTRAINT ominicontacto_app_grabacion_pkey;
ALTER TABLE ONLY public.ominicontacto_app_formulario DROP CONSTRAINT ominicontacto_app_formulario_pkey;
ALTER TABLE ONLY public.ominicontacto_app_fieldformulario DROP CONSTRAINT ominicontacto_app_fieldformulario_pkey;
ALTER TABLE ONLY public.ominicontacto_app_fieldformulario DROP CONSTRAINT ominicontacto_app_fieldformulario_orden_6218007e_uniq;
ALTER TABLE ONLY public.ominicontacto_app_duraciondellamada DROP CONSTRAINT ominicontacto_app_duraciondellamada_pkey;
ALTER TABLE ONLY public.ominicontacto_app_contacto DROP CONSTRAINT ominicontacto_app_contacto_pkey;
ALTER TABLE ONLY public.ominicontacto_app_chat DROP CONSTRAINT ominicontacto_app_chat_pkey;
ALTER TABLE ONLY public.ominicontacto_app_campana DROP CONSTRAINT ominicontacto_app_campana_pkey;
ALTER TABLE ONLY public.ominicontacto_app_calificacioncliente DROP CONSTRAINT ominicontacto_app_calificacioncliente_pkey;
ALTER TABLE ONLY public.ominicontacto_app_calificacioncliente DROP CONSTRAINT ominicontacto_app_calificacioncliente_contacto_id_key;
ALTER TABLE ONLY public.ominicontacto_app_calificacioncampana DROP CONSTRAINT ominicontacto_app_calificacioncampana_pkey;
ALTER TABLE ONLY public.ominicontacto_app_calificacioncampana_calificacion DROP CONSTRAINT ominicontacto_app_calificacioncampana_calificacion_pkey;
ALTER TABLE ONLY public.ominicontacto_app_calificacion DROP CONSTRAINT ominicontacto_app_calificacion_pkey;
ALTER TABLE ONLY public.ominicontacto_app_calificacioncampana_calificacion DROP CONSTRAINT ominicontacto_app_califica_calificacioncampana_id_8a83ac71_uniq;
ALTER TABLE ONLY public.ominicontacto_app_basedatoscontacto DROP CONSTRAINT ominicontacto_app_basedatoscontacto_pkey;
ALTER TABLE ONLY public.ominicontacto_app_agenteprofile DROP CONSTRAINT ominicontacto_app_agenteprofile_user_id_key;
ALTER TABLE ONLY public.ominicontacto_app_agenteprofile DROP CONSTRAINT ominicontacto_app_agenteprofile_sip_extension_key;
ALTER TABLE ONLY public.ominicontacto_app_agenteprofile DROP CONSTRAINT ominicontacto_app_agenteprofile_pkey;
ALTER TABLE ONLY public.ominicontacto_app_agenteprofile_modulos DROP CONSTRAINT ominicontacto_app_agenteprofile_modulos_pkey;
ALTER TABLE ONLY public.ominicontacto_app_agenteprofile_modulos DROP CONSTRAINT ominicontacto_app_agenteprofile__agenteprofile_id_acebf09b_uniq;
ALTER TABLE ONLY public.ominicontacto_app_agenda DROP CONSTRAINT ominicontacto_app_agenda_pkey;
ALTER TABLE ONLY public.mtrees DROP CONSTRAINT mtrees_tname_tprefix_tvalue_idx;
ALTER TABLE ONLY public.mtrees DROP CONSTRAINT mtrees_pkey;
ALTER TABLE ONLY public.mtree DROP CONSTRAINT mtree_tprefix_idx;
ALTER TABLE ONLY public.mtree DROP CONSTRAINT mtree_pkey;
ALTER TABLE ONLY public.mohqueues DROP CONSTRAINT mohqueues_pkey;
ALTER TABLE ONLY public.mohqueues DROP CONSTRAINT mohqueues_mohqueue_uri_idx;
ALTER TABLE ONLY public.mohqueues DROP CONSTRAINT mohqueues_mohqueue_name_idx;
ALTER TABLE ONLY public.mohqcalls DROP CONSTRAINT mohqcalls_pkey;
ALTER TABLE ONLY public.mohqcalls DROP CONSTRAINT mohqcalls_mohqcalls_idx;
ALTER TABLE ONLY public.missed_calls DROP CONSTRAINT missed_calls_pkey;
ALTER TABLE ONLY public.mensaje_recibido DROP CONSTRAINT mensaje_recibido_pkey;
ALTER TABLE ONLY public.mensaje_enviado DROP CONSTRAINT mensaje_enviado_pkey;
ALTER TABLE ONLY public.location DROP CONSTRAINT location_ruid_idx;
ALTER TABLE ONLY public.location DROP CONSTRAINT location_pkey;
ALTER TABLE ONLY public.location_attrs DROP CONSTRAINT location_attrs_pkey;
ALTER TABLE ONLY public.lcr_rule_target DROP CONSTRAINT lcr_rule_target_rule_id_gw_id_idx;
ALTER TABLE ONLY public.lcr_rule_target DROP CONSTRAINT lcr_rule_target_pkey;
ALTER TABLE ONLY public.lcr_rule DROP CONSTRAINT lcr_rule_pkey;
ALTER TABLE ONLY public.lcr_rule DROP CONSTRAINT lcr_rule_lcr_id_prefix_from_uri_idx;
ALTER TABLE ONLY public.lcr_gw DROP CONSTRAINT lcr_gw_pkey;
ALTER TABLE ONLY public.imc_rooms DROP CONSTRAINT imc_rooms_pkey;
ALTER TABLE ONLY public.imc_rooms DROP CONSTRAINT imc_rooms_name_domain_idx;
ALTER TABLE ONLY public.imc_members DROP CONSTRAINT imc_members_pkey;
ALTER TABLE ONLY public.imc_members DROP CONSTRAINT imc_members_account_room_idx;
ALTER TABLE ONLY public.htable DROP CONSTRAINT htable_pkey;
ALTER TABLE ONLY public.grp DROP CONSTRAINT grp_pkey;
ALTER TABLE ONLY public.grp DROP CONSTRAINT grp_account_group_idx;
ALTER TABLE ONLY public.globalblacklist DROP CONSTRAINT globalblacklist_pkey;
ALTER TABLE ONLY public.dr_rules DROP CONSTRAINT dr_rules_pkey;
ALTER TABLE ONLY public.dr_gw_lists DROP CONSTRAINT dr_gw_lists_pkey;
ALTER TABLE ONLY public.dr_groups DROP CONSTRAINT dr_groups_pkey;
ALTER TABLE ONLY public.dr_gateways DROP CONSTRAINT dr_gateways_pkey;
ALTER TABLE ONLY public.domainpolicy DROP CONSTRAINT domainpolicy_rav_idx;
ALTER TABLE ONLY public.domainpolicy DROP CONSTRAINT domainpolicy_pkey;
ALTER TABLE ONLY public.domain DROP CONSTRAINT domain_pkey;
ALTER TABLE ONLY public.domain_name DROP CONSTRAINT domain_name_pkey;
ALTER TABLE ONLY public.domain DROP CONSTRAINT domain_domain_idx;
ALTER TABLE ONLY public.domain_attrs DROP CONSTRAINT domain_attrs_pkey;
ALTER TABLE ONLY public.domain_attrs DROP CONSTRAINT domain_attrs_domain_attrs_idx;
ALTER TABLE ONLY public.django_migrations DROP CONSTRAINT django_migrations_pkey;
ALTER TABLE ONLY public.django_content_type DROP CONSTRAINT django_content_type_pkey;
ALTER TABLE ONLY public.django_content_type DROP CONSTRAINT django_content_type_app_label_76bd3d3b_uniq;
ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT django_admin_log_pkey;
ALTER TABLE ONLY public.dispatcher DROP CONSTRAINT dispatcher_pkey;
ALTER TABLE ONLY public.dialplan DROP CONSTRAINT dialplan_pkey;
ALTER TABLE ONLY public.dialog_vars DROP CONSTRAINT dialog_vars_pkey;
ALTER TABLE ONLY public.dialog DROP CONSTRAINT dialog_pkey;
ALTER TABLE ONLY public.dbaliases DROP CONSTRAINT dbaliases_pkey;
ALTER TABLE ONLY public.cpl DROP CONSTRAINT cpl_pkey;
ALTER TABLE ONLY public.cpl DROP CONSTRAINT cpl_account_idx;
ALTER TABLE ONLY public.carrierroute DROP CONSTRAINT carrierroute_pkey;
ALTER TABLE ONLY public.carrierfailureroute DROP CONSTRAINT carrierfailureroute_pkey;
ALTER TABLE ONLY public.carrier_name DROP CONSTRAINT carrier_name_pkey;
ALTER TABLE ONLY public.auth_permission DROP CONSTRAINT auth_permission_pkey;
ALTER TABLE ONLY public.auth_permission DROP CONSTRAINT auth_permission_content_type_id_01ab375a_uniq;
ALTER TABLE ONLY public.auth_group DROP CONSTRAINT auth_group_pkey;
ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_pkey;
ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_group_id_0cd325b0_uniq;
ALTER TABLE ONLY public.auth_group DROP CONSTRAINT auth_group_name_key;
ALTER TABLE ONLY public.aliases DROP CONSTRAINT aliases_ruid_idx;
ALTER TABLE ONLY public.aliases DROP CONSTRAINT aliases_pkey;
ALTER TABLE ONLY public.address DROP CONSTRAINT address_pkey;
ALTER TABLE ONLY public.active_watchers DROP CONSTRAINT active_watchers_pkey;
ALTER TABLE ONLY public.active_watchers DROP CONSTRAINT active_watchers_active_watchers_idx;
ALTER TABLE ONLY public.acc DROP CONSTRAINT acc_pkey;
ALTER TABLE ONLY public.acc_cdrs DROP CONSTRAINT acc_cdrs_pkey;
ALTER TABLE public.xcap ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.watchers ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.usr_preferences ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.userblacklist ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.uri ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.uacreg ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.trusted ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.topos_t ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.topos_d ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.subscriber ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.speed_dial ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.sip_trace ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.silo ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.sca_subscriptions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.rtpproxy ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.rls_watchers ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.rls_presentity ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.re_grp ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.queue_member_table ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.purplemap ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.pua ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.presentity ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.pl_pipes ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.pdt ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_wombatlog ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_user_user_permissions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_user_groups ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_user ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_queuelog ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_pausa ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_modulo ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_metadatacliente ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_mensajechat ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_grupo ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_grabacion ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_formulario ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_fieldformulario ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_duraciondellamada ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_contacto ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_chat ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_campana ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_calificacioncliente ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_calificacioncampana_calificacion ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_calificacioncampana ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_calificacion ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_basedatoscontacto ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_agenteprofile_modulos ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_agenteprofile ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ominicontacto_app_agenda ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.mtrees ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.mtree ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.mohqueues ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.mohqcalls ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.missed_calls ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.mensaje_recibido ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.mensaje_enviado ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.location_attrs ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.location ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.lcr_rule_target ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.lcr_rule ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.lcr_gw ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.imc_rooms ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.imc_members ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.htable ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.grp ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.globalblacklist ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.dr_rules ALTER COLUMN ruleid DROP DEFAULT;
ALTER TABLE public.dr_gw_lists ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.dr_groups ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.dr_gateways ALTER COLUMN gwid DROP DEFAULT;
ALTER TABLE public.domainpolicy ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.domain_name ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.domain_attrs ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.domain ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.django_migrations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.django_content_type ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.django_admin_log ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.dispatcher ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.dialplan ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.dialog_vars ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.dialog ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.dbaliases ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.cpl ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.carrierroute ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.carrierfailureroute ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.carrier_name ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.auth_permission ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.auth_group_permissions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.auth_group ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.aliases ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.address ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.active_watchers ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.acc_cdrs ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.acc ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE public.xcap_id_seq;
DROP TABLE public.xcap;
DROP SEQUENCE public.watchers_id_seq;
DROP TABLE public.watchers;
DROP TABLE public.version;
DROP SEQUENCE public.usr_preferences_id_seq;
DROP TABLE public.usr_preferences;
DROP SEQUENCE public.userblacklist_id_seq;
DROP TABLE public.userblacklist;
DROP SEQUENCE public.uri_id_seq;
DROP TABLE public.uri;
DROP SEQUENCE public.uacreg_id_seq;
DROP TABLE public.uacreg;
DROP SEQUENCE public.trusted_id_seq;
DROP TABLE public.trusted;
DROP SEQUENCE public.topos_t_id_seq;
DROP TABLE public.topos_t;
DROP SEQUENCE public.topos_d_id_seq;
DROP TABLE public.topos_d;
DROP SEQUENCE public.subscriber_id_seq;
DROP TABLE public.subscriber;
DROP SEQUENCE public.speed_dial_id_seq;
DROP TABLE public.speed_dial;
DROP SEQUENCE public.sip_trace_id_seq;
DROP TABLE public.sip_trace;
DROP SEQUENCE public.silo_id_seq;
DROP TABLE public.silo;
DROP SEQUENCE public.sca_subscriptions_id_seq;
DROP TABLE public.sca_subscriptions;
DROP SEQUENCE public.rtpproxy_id_seq;
DROP TABLE public.rtpproxy;
DROP SEQUENCE public.rls_watchers_id_seq;
DROP TABLE public.rls_watchers;
DROP SEQUENCE public.rls_presentity_id_seq;
DROP TABLE public.rls_presentity;
DROP SEQUENCE public.re_grp_id_seq;
DROP TABLE public.re_grp;
DROP TABLE public.queue_table;
DROP SEQUENCE public.queue_member_table_id_seq;
DROP TABLE public.queue_member_table;
DROP SEQUENCE public.purplemap_id_seq;
DROP TABLE public.purplemap;
DROP SEQUENCE public.pua_id_seq;
DROP TABLE public.pua;
DROP SEQUENCE public.presentity_id_seq;
DROP TABLE public.presentity;
DROP SEQUENCE public.pl_pipes_id_seq;
DROP TABLE public.pl_pipes;
DROP SEQUENCE public.pdt_id_seq;
DROP TABLE public.pdt;
DROP SEQUENCE public.ominicontacto_app_wombatlog_id_seq;
DROP TABLE public.ominicontacto_app_wombatlog;
DROP SEQUENCE public.ominicontacto_app_user_user_permissions_id_seq;
DROP TABLE public.ominicontacto_app_user_user_permissions;
DROP SEQUENCE public.ominicontacto_app_user_id_seq;
DROP SEQUENCE public.ominicontacto_app_user_groups_id_seq;
DROP TABLE public.ominicontacto_app_user_groups;
DROP TABLE public.ominicontacto_app_user;
DROP SEQUENCE public.ominicontacto_app_queuelog_id_seq;
DROP TABLE public.ominicontacto_app_queuelog;
DROP SEQUENCE public.ominicontacto_app_pausa_id_seq;
DROP TABLE public.ominicontacto_app_pausa;
DROP SEQUENCE public.ominicontacto_app_modulo_id_seq;
DROP TABLE public.ominicontacto_app_modulo;
DROP SEQUENCE public.ominicontacto_app_metadatacliente_id_seq;
DROP TABLE public.ominicontacto_app_metadatacliente;
DROP SEQUENCE public.ominicontacto_app_mensajechat_id_seq;
DROP TABLE public.ominicontacto_app_mensajechat;
DROP SEQUENCE public.ominicontacto_app_grupo_id_seq;
DROP TABLE public.ominicontacto_app_grupo;
DROP SEQUENCE public.ominicontacto_app_grabacion_id_seq;
DROP TABLE public.ominicontacto_app_grabacion;
DROP SEQUENCE public.ominicontacto_app_formulario_id_seq;
DROP TABLE public.ominicontacto_app_formulario;
DROP SEQUENCE public.ominicontacto_app_fieldformulario_id_seq;
DROP TABLE public.ominicontacto_app_fieldformulario;
DROP SEQUENCE public.ominicontacto_app_duraciondellamada_id_seq;
DROP TABLE public.ominicontacto_app_duraciondellamada;
DROP SEQUENCE public.ominicontacto_app_contacto_id_seq;
DROP TABLE public.ominicontacto_app_contacto;
DROP SEQUENCE public.ominicontacto_app_chat_id_seq;
DROP TABLE public.ominicontacto_app_chat;
DROP SEQUENCE public.ominicontacto_app_campana_id_seq;
DROP TABLE public.ominicontacto_app_campana;
DROP SEQUENCE public.ominicontacto_app_calificacioncliente_id_seq;
DROP TABLE public.ominicontacto_app_calificacioncliente;
DROP SEQUENCE public.ominicontacto_app_calificacioncampana_id_seq;
DROP SEQUENCE public.ominicontacto_app_calificacioncampana_calificacion_id_seq;
DROP TABLE public.ominicontacto_app_calificacioncampana_calificacion;
DROP TABLE public.ominicontacto_app_calificacioncampana;
DROP SEQUENCE public.ominicontacto_app_calificacion_id_seq;
DROP TABLE public.ominicontacto_app_calificacion;
DROP SEQUENCE public.ominicontacto_app_basedatoscontacto_id_seq;
DROP TABLE public.ominicontacto_app_basedatoscontacto;
DROP SEQUENCE public.ominicontacto_app_agenteprofile_modulos_id_seq;
DROP TABLE public.ominicontacto_app_agenteprofile_modulos;
DROP SEQUENCE public.ominicontacto_app_agenteprofile_id_seq;
DROP TABLE public.ominicontacto_app_agenteprofile;
DROP SEQUENCE public.ominicontacto_app_agenda_id_seq;
DROP TABLE public.ominicontacto_app_agenda;
DROP SEQUENCE public.mtrees_id_seq;
DROP TABLE public.mtrees;
DROP SEQUENCE public.mtree_id_seq;
DROP TABLE public.mtree;
DROP SEQUENCE public.mohqueues_id_seq;
DROP TABLE public.mohqueues;
DROP SEQUENCE public.mohqcalls_id_seq;
DROP TABLE public.mohqcalls;
DROP SEQUENCE public.missed_calls_id_seq;
DROP TABLE public.missed_calls;
DROP SEQUENCE public.mensaje_recibido_id_seq;
DROP TABLE public.mensaje_recibido;
DROP SEQUENCE public.mensaje_enviado_id_seq;
DROP TABLE public.mensaje_enviado;
DROP SEQUENCE public.location_id_seq;
DROP SEQUENCE public.location_attrs_id_seq;
DROP TABLE public.location_attrs;
DROP TABLE public.location;
DROP SEQUENCE public.lcr_rule_target_id_seq;
DROP TABLE public.lcr_rule_target;
DROP SEQUENCE public.lcr_rule_id_seq;
DROP TABLE public.lcr_rule;
DROP SEQUENCE public.lcr_gw_id_seq;
DROP TABLE public.lcr_gw;
DROP SEQUENCE public.imc_rooms_id_seq;
DROP TABLE public.imc_rooms;
DROP SEQUENCE public.imc_members_id_seq;
DROP TABLE public.imc_members;
DROP SEQUENCE public.htable_id_seq;
DROP TABLE public.htable;
DROP SEQUENCE public.grp_id_seq;
DROP TABLE public.grp;
DROP SEQUENCE public.globalblacklist_id_seq;
DROP TABLE public.globalblacklist;
DROP SEQUENCE public.dr_rules_ruleid_seq;
DROP TABLE public.dr_rules;
DROP SEQUENCE public.dr_gw_lists_id_seq;
DROP TABLE public.dr_gw_lists;
DROP SEQUENCE public.dr_groups_id_seq;
DROP TABLE public.dr_groups;
DROP SEQUENCE public.dr_gateways_gwid_seq;
DROP TABLE public.dr_gateways;
DROP SEQUENCE public.domainpolicy_id_seq;
DROP TABLE public.domainpolicy;
DROP SEQUENCE public.domain_name_id_seq;
DROP TABLE public.domain_name;
DROP SEQUENCE public.domain_id_seq;
DROP SEQUENCE public.domain_attrs_id_seq;
DROP TABLE public.domain_attrs;
DROP TABLE public.domain;
DROP SEQUENCE public.django_migrations_id_seq;
DROP TABLE public.django_migrations;
DROP SEQUENCE public.django_content_type_id_seq;
DROP TABLE public.django_content_type;
DROP SEQUENCE public.django_admin_log_id_seq;
DROP TABLE public.django_admin_log;
DROP SEQUENCE public.dispatcher_id_seq;
DROP TABLE public.dispatcher;
DROP SEQUENCE public.dialplan_id_seq;
DROP TABLE public.dialplan;
DROP SEQUENCE public.dialog_vars_id_seq;
DROP TABLE public.dialog_vars;
DROP SEQUENCE public.dialog_id_seq;
DROP TABLE public.dialog;
DROP SEQUENCE public.dbaliases_id_seq;
DROP TABLE public.dbaliases;
DROP SEQUENCE public.cpl_id_seq;
DROP TABLE public.cpl;
DROP SEQUENCE public.carrierroute_id_seq;
DROP TABLE public.carrierroute;
DROP SEQUENCE public.carrierfailureroute_id_seq;
DROP TABLE public.carrierfailureroute;
DROP SEQUENCE public.carrier_name_id_seq;
DROP TABLE public.carrier_name;
DROP SEQUENCE public.auth_permission_id_seq;
DROP TABLE public.auth_permission;
DROP SEQUENCE public.auth_group_permissions_id_seq;
DROP TABLE public.auth_group_permissions;
DROP SEQUENCE public.auth_group_id_seq;
DROP TABLE public.auth_group;
DROP SEQUENCE public.aliases_id_seq;
DROP TABLE public.aliases;
DROP SEQUENCE public.address_id_seq;
DROP TABLE public.address;
DROP SEQUENCE public.active_watchers_id_seq;
DROP TABLE public.active_watchers;
DROP SEQUENCE public.acc_id_seq;
DROP SEQUENCE public.acc_cdrs_id_seq;
DROP TABLE public.acc_cdrs;
DROP TABLE public.acc;
DROP FUNCTION public.rand();
DROP FUNCTION public.concat(text, text);
DROP EXTENSION plpythonu;
DROP EXTENSION plpgsql;
DROP SCHEMA public;
--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO postgres;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'standard public schema';


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
-- Name: acc; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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


ALTER TABLE public.acc OWNER TO kamailio;

--
-- Name: acc_cdrs; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE acc_cdrs (
    id integer NOT NULL,
    start_time timestamp without time zone DEFAULT '2000-01-01 00:00:00'::timestamp without time zone NOT NULL,
    end_time timestamp without time zone DEFAULT '2000-01-01 00:00:00'::timestamp without time zone NOT NULL,
    duration real DEFAULT 0 NOT NULL
);


ALTER TABLE public.acc_cdrs OWNER TO kamailio;

--
-- Name: acc_cdrs_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE acc_cdrs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.acc_cdrs_id_seq OWNER TO kamailio;

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


ALTER TABLE public.acc_id_seq OWNER TO kamailio;

--
-- Name: acc_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE acc_id_seq OWNED BY acc.id;


--
-- Name: active_watchers; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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
    updated_winfo integer NOT NULL,
    flags integer DEFAULT 0 NOT NULL,
    user_agent character varying(255) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.active_watchers OWNER TO kamailio;

--
-- Name: active_watchers_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE active_watchers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.active_watchers_id_seq OWNER TO kamailio;

--
-- Name: active_watchers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE active_watchers_id_seq OWNED BY active_watchers.id;


--
-- Name: address; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE address (
    id integer NOT NULL,
    grp integer DEFAULT 1 NOT NULL,
    ip_addr character varying(50) NOT NULL,
    mask integer DEFAULT 32 NOT NULL,
    port smallint DEFAULT 0 NOT NULL,
    tag character varying(64)
);


ALTER TABLE public.address OWNER TO kamailio;

--
-- Name: address_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE address_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.address_id_seq OWNER TO kamailio;

--
-- Name: address_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE address_id_seq OWNED BY address.id;


--
-- Name: aliases; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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


ALTER TABLE public.aliases OWNER TO kamailio;

--
-- Name: aliases_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE aliases_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.aliases_id_seq OWNER TO kamailio;

--
-- Name: aliases_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE aliases_id_seq OWNED BY aliases.id;


--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE auth_group (
    id integer NOT NULL,
    name character varying(80) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO kamailio;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_id_seq OWNER TO kamailio;

--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE auth_group_id_seq OWNED BY auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO kamailio;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_permissions_id_seq OWNER TO kamailio;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE auth_group_permissions_id_seq OWNED BY auth_group_permissions.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO kamailio;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_permission_id_seq OWNER TO kamailio;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE auth_permission_id_seq OWNED BY auth_permission.id;


--
-- Name: carrier_name; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE carrier_name (
    id integer NOT NULL,
    carrier character varying(64) DEFAULT NULL::character varying
);


ALTER TABLE public.carrier_name OWNER TO kamailio;

--
-- Name: carrier_name_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE carrier_name_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.carrier_name_id_seq OWNER TO kamailio;

--
-- Name: carrier_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE carrier_name_id_seq OWNED BY carrier_name.id;


--
-- Name: carrierfailureroute; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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


ALTER TABLE public.carrierfailureroute OWNER TO kamailio;

--
-- Name: carrierfailureroute_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE carrierfailureroute_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.carrierfailureroute_id_seq OWNER TO kamailio;

--
-- Name: carrierfailureroute_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE carrierfailureroute_id_seq OWNED BY carrierfailureroute.id;


--
-- Name: carrierroute; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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


ALTER TABLE public.carrierroute OWNER TO kamailio;

--
-- Name: carrierroute_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE carrierroute_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.carrierroute_id_seq OWNER TO kamailio;

--
-- Name: carrierroute_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE carrierroute_id_seq OWNED BY carrierroute.id;


--
-- Name: cpl; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE cpl (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    domain character varying(64) DEFAULT ''::character varying NOT NULL,
    cpl_xml text,
    cpl_bin text
);


ALTER TABLE public.cpl OWNER TO kamailio;

--
-- Name: cpl_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE cpl_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cpl_id_seq OWNER TO kamailio;

--
-- Name: cpl_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE cpl_id_seq OWNED BY cpl.id;


--
-- Name: dbaliases; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE dbaliases (
    id integer NOT NULL,
    alias_username character varying(64) DEFAULT ''::character varying NOT NULL,
    alias_domain character varying(64) DEFAULT ''::character varying NOT NULL,
    username character varying(64) DEFAULT ''::character varying NOT NULL,
    domain character varying(64) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.dbaliases OWNER TO kamailio;

--
-- Name: dbaliases_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE dbaliases_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dbaliases_id_seq OWNER TO kamailio;

--
-- Name: dbaliases_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE dbaliases_id_seq OWNED BY dbaliases.id;


--
-- Name: dialog; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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


ALTER TABLE public.dialog OWNER TO kamailio;

--
-- Name: dialog_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE dialog_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dialog_id_seq OWNER TO kamailio;

--
-- Name: dialog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE dialog_id_seq OWNED BY dialog.id;


--
-- Name: dialog_vars; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE dialog_vars (
    id integer NOT NULL,
    hash_entry integer NOT NULL,
    hash_id integer NOT NULL,
    dialog_key character varying(128) NOT NULL,
    dialog_value character varying(512) NOT NULL
);


ALTER TABLE public.dialog_vars OWNER TO kamailio;

--
-- Name: dialog_vars_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE dialog_vars_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dialog_vars_id_seq OWNER TO kamailio;

--
-- Name: dialog_vars_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE dialog_vars_id_seq OWNED BY dialog_vars.id;


--
-- Name: dialplan; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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


ALTER TABLE public.dialplan OWNER TO kamailio;

--
-- Name: dialplan_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE dialplan_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dialplan_id_seq OWNER TO kamailio;

--
-- Name: dialplan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE dialplan_id_seq OWNED BY dialplan.id;


--
-- Name: dispatcher; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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


ALTER TABLE public.dispatcher OWNER TO kamailio;

--
-- Name: dispatcher_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE dispatcher_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dispatcher_id_seq OWNER TO kamailio;

--
-- Name: dispatcher_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE dispatcher_id_seq OWNED BY dispatcher.id;


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO kamailio;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_admin_log_id_seq OWNER TO kamailio;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE django_admin_log_id_seq OWNED BY django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO kamailio;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_content_type_id_seq OWNER TO kamailio;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE django_content_type_id_seq OWNED BY django_content_type.id;


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO kamailio;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_migrations_id_seq OWNER TO kamailio;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE django_migrations_id_seq OWNED BY django_migrations.id;


--
-- Name: domain; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE domain (
    id integer NOT NULL,
    domain character varying(64) NOT NULL,
    did character varying(64) DEFAULT NULL::character varying,
    last_modified timestamp without time zone DEFAULT '2000-01-01 00:00:01'::timestamp without time zone NOT NULL
);


ALTER TABLE public.domain OWNER TO kamailio;

--
-- Name: domain_attrs; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE domain_attrs (
    id integer NOT NULL,
    did character varying(64) NOT NULL,
    name character varying(32) NOT NULL,
    type integer NOT NULL,
    value character varying(255) NOT NULL,
    last_modified timestamp without time zone DEFAULT '2000-01-01 00:00:01'::timestamp without time zone NOT NULL
);


ALTER TABLE public.domain_attrs OWNER TO kamailio;

--
-- Name: domain_attrs_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE domain_attrs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.domain_attrs_id_seq OWNER TO kamailio;

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


ALTER TABLE public.domain_id_seq OWNER TO kamailio;

--
-- Name: domain_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE domain_id_seq OWNED BY domain.id;


--
-- Name: domain_name; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE domain_name (
    id integer NOT NULL,
    domain character varying(64) DEFAULT NULL::character varying
);


ALTER TABLE public.domain_name OWNER TO kamailio;

--
-- Name: domain_name_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE domain_name_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.domain_name_id_seq OWNER TO kamailio;

--
-- Name: domain_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE domain_name_id_seq OWNED BY domain_name.id;


--
-- Name: domainpolicy; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE domainpolicy (
    id integer NOT NULL,
    rule character varying(255) NOT NULL,
    type character varying(255) NOT NULL,
    att character varying(255),
    val character varying(128),
    description character varying(255) NOT NULL
);


ALTER TABLE public.domainpolicy OWNER TO kamailio;

--
-- Name: domainpolicy_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE domainpolicy_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.domainpolicy_id_seq OWNER TO kamailio;

--
-- Name: domainpolicy_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE domainpolicy_id_seq OWNED BY domainpolicy.id;


--
-- Name: dr_gateways; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE dr_gateways (
    gwid integer NOT NULL,
    type integer DEFAULT 0 NOT NULL,
    address character varying(128) NOT NULL,
    strip integer DEFAULT 0 NOT NULL,
    pri_prefix character varying(64) DEFAULT NULL::character varying,
    attrs character varying(255) DEFAULT NULL::character varying,
    description character varying(128) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.dr_gateways OWNER TO kamailio;

--
-- Name: dr_gateways_gwid_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE dr_gateways_gwid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dr_gateways_gwid_seq OWNER TO kamailio;

--
-- Name: dr_gateways_gwid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE dr_gateways_gwid_seq OWNED BY dr_gateways.gwid;


--
-- Name: dr_groups; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE dr_groups (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    domain character varying(128) DEFAULT ''::character varying NOT NULL,
    groupid integer DEFAULT 0 NOT NULL,
    description character varying(128) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.dr_groups OWNER TO kamailio;

--
-- Name: dr_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE dr_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dr_groups_id_seq OWNER TO kamailio;

--
-- Name: dr_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE dr_groups_id_seq OWNED BY dr_groups.id;


--
-- Name: dr_gw_lists; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE dr_gw_lists (
    id integer NOT NULL,
    gwlist character varying(255) NOT NULL,
    description character varying(128) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.dr_gw_lists OWNER TO kamailio;

--
-- Name: dr_gw_lists_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE dr_gw_lists_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dr_gw_lists_id_seq OWNER TO kamailio;

--
-- Name: dr_gw_lists_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE dr_gw_lists_id_seq OWNED BY dr_gw_lists.id;


--
-- Name: dr_rules; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE dr_rules (
    ruleid integer NOT NULL,
    groupid character varying(255) NOT NULL,
    prefix character varying(64) NOT NULL,
    timerec character varying(255) NOT NULL,
    priority integer DEFAULT 0 NOT NULL,
    routeid character varying(64) NOT NULL,
    gwlist character varying(255) NOT NULL,
    description character varying(128) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.dr_rules OWNER TO kamailio;

--
-- Name: dr_rules_ruleid_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE dr_rules_ruleid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dr_rules_ruleid_seq OWNER TO kamailio;

--
-- Name: dr_rules_ruleid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE dr_rules_ruleid_seq OWNED BY dr_rules.ruleid;


--
-- Name: globalblacklist; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE globalblacklist (
    id integer NOT NULL,
    prefix character varying(64) DEFAULT ''::character varying NOT NULL,
    whitelist smallint DEFAULT 0 NOT NULL,
    description character varying(255) DEFAULT NULL::character varying
);


ALTER TABLE public.globalblacklist OWNER TO kamailio;

--
-- Name: globalblacklist_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE globalblacklist_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.globalblacklist_id_seq OWNER TO kamailio;

--
-- Name: globalblacklist_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE globalblacklist_id_seq OWNED BY globalblacklist.id;


--
-- Name: grp; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE grp (
    id integer NOT NULL,
    username character varying(64) DEFAULT ''::character varying NOT NULL,
    domain character varying(64) DEFAULT ''::character varying NOT NULL,
    grp character varying(64) DEFAULT ''::character varying NOT NULL,
    last_modified timestamp without time zone DEFAULT '2000-01-01 00:00:01'::timestamp without time zone NOT NULL
);


ALTER TABLE public.grp OWNER TO kamailio;

--
-- Name: grp_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE grp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.grp_id_seq OWNER TO kamailio;

--
-- Name: grp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE grp_id_seq OWNED BY grp.id;


--
-- Name: htable; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE htable (
    id integer NOT NULL,
    key_name character varying(64) DEFAULT ''::character varying NOT NULL,
    key_type integer DEFAULT 0 NOT NULL,
    value_type integer DEFAULT 0 NOT NULL,
    key_value character varying(128) DEFAULT ''::character varying NOT NULL,
    expires integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.htable OWNER TO kamailio;

--
-- Name: htable_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE htable_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.htable_id_seq OWNER TO kamailio;

--
-- Name: htable_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE htable_id_seq OWNED BY htable.id;


--
-- Name: imc_members; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE imc_members (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    domain character varying(64) NOT NULL,
    room character varying(64) NOT NULL,
    flag integer NOT NULL
);


ALTER TABLE public.imc_members OWNER TO kamailio;

--
-- Name: imc_members_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE imc_members_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.imc_members_id_seq OWNER TO kamailio;

--
-- Name: imc_members_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE imc_members_id_seq OWNED BY imc_members.id;


--
-- Name: imc_rooms; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE imc_rooms (
    id integer NOT NULL,
    name character varying(64) NOT NULL,
    domain character varying(64) NOT NULL,
    flag integer NOT NULL
);


ALTER TABLE public.imc_rooms OWNER TO kamailio;

--
-- Name: imc_rooms_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE imc_rooms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.imc_rooms_id_seq OWNER TO kamailio;

--
-- Name: imc_rooms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE imc_rooms_id_seq OWNED BY imc_rooms.id;


--
-- Name: lcr_gw; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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


ALTER TABLE public.lcr_gw OWNER TO kamailio;

--
-- Name: lcr_gw_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE lcr_gw_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lcr_gw_id_seq OWNER TO kamailio;

--
-- Name: lcr_gw_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE lcr_gw_id_seq OWNED BY lcr_gw.id;


--
-- Name: lcr_rule; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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


ALTER TABLE public.lcr_rule OWNER TO kamailio;

--
-- Name: lcr_rule_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE lcr_rule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lcr_rule_id_seq OWNER TO kamailio;

--
-- Name: lcr_rule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE lcr_rule_id_seq OWNED BY lcr_rule.id;


--
-- Name: lcr_rule_target; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE lcr_rule_target (
    id integer NOT NULL,
    lcr_id smallint NOT NULL,
    rule_id integer NOT NULL,
    gw_id integer NOT NULL,
    priority smallint NOT NULL,
    weight integer DEFAULT 1 NOT NULL
);


ALTER TABLE public.lcr_rule_target OWNER TO kamailio;

--
-- Name: lcr_rule_target_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE lcr_rule_target_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lcr_rule_target_id_seq OWNER TO kamailio;

--
-- Name: lcr_rule_target_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE lcr_rule_target_id_seq OWNED BY lcr_rule_target.id;


--
-- Name: location; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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


ALTER TABLE public.location OWNER TO kamailio;

--
-- Name: location_attrs; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE location_attrs (
    id integer NOT NULL,
    ruid character varying(64) DEFAULT ''::character varying NOT NULL,
    username character varying(64) DEFAULT ''::character varying NOT NULL,
    domain character varying(64) DEFAULT NULL::character varying,
    aname character varying(64) DEFAULT ''::character varying NOT NULL,
    atype integer DEFAULT 0 NOT NULL,
    avalue character varying(255) DEFAULT ''::character varying NOT NULL,
    last_modified timestamp without time zone DEFAULT '2000-01-01 00:00:01'::timestamp without time zone NOT NULL
);


ALTER TABLE public.location_attrs OWNER TO kamailio;

--
-- Name: location_attrs_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE location_attrs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.location_attrs_id_seq OWNER TO kamailio;

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


ALTER TABLE public.location_id_seq OWNER TO kamailio;

--
-- Name: location_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE location_id_seq OWNED BY location.id;


--
-- Name: mensaje_enviado; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE mensaje_enviado (
    id integer NOT NULL,
    remitente character varying(20) NOT NULL,
    destinatario character varying(20) NOT NULL,
    "timestamp" character varying(255) NOT NULL,
    content text NOT NULL,
    result integer,
    agente_id integer NOT NULL
);


ALTER TABLE public.mensaje_enviado OWNER TO kamailio;

--
-- Name: mensaje_enviado_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE mensaje_enviado_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mensaje_enviado_id_seq OWNER TO kamailio;

--
-- Name: mensaje_enviado_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE mensaje_enviado_id_seq OWNED BY mensaje_enviado.id;


--
-- Name: mensaje_recibido; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE mensaje_recibido (
    id integer NOT NULL,
    remitente character varying(20) NOT NULL,
    destinatario character varying(20) NOT NULL,
    "timestamp" character varying(255) NOT NULL,
    timezone integer NOT NULL,
    encoding integer NOT NULL,
    content text NOT NULL,
    es_leido boolean NOT NULL
);


ALTER TABLE public.mensaje_recibido OWNER TO kamailio;

--
-- Name: mensaje_recibido_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE mensaje_recibido_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mensaje_recibido_id_seq OWNER TO kamailio;

--
-- Name: mensaje_recibido_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE mensaje_recibido_id_seq OWNED BY mensaje_recibido.id;


--
-- Name: missed_calls; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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


ALTER TABLE public.missed_calls OWNER TO kamailio;

--
-- Name: missed_calls_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE missed_calls_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.missed_calls_id_seq OWNER TO kamailio;

--
-- Name: missed_calls_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE missed_calls_id_seq OWNED BY missed_calls.id;


--
-- Name: mohqcalls; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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


ALTER TABLE public.mohqcalls OWNER TO kamailio;

--
-- Name: mohqcalls_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE mohqcalls_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mohqcalls_id_seq OWNER TO kamailio;

--
-- Name: mohqcalls_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE mohqcalls_id_seq OWNED BY mohqcalls.id;


--
-- Name: mohqueues; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE mohqueues (
    id integer NOT NULL,
    name character varying(25) NOT NULL,
    uri character varying(100) NOT NULL,
    mohdir character varying(100),
    mohfile character varying(100) NOT NULL,
    debug integer NOT NULL
);


ALTER TABLE public.mohqueues OWNER TO kamailio;

--
-- Name: mohqueues_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE mohqueues_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mohqueues_id_seq OWNER TO kamailio;

--
-- Name: mohqueues_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE mohqueues_id_seq OWNED BY mohqueues.id;


--
-- Name: mtree; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE mtree (
    id integer NOT NULL,
    tprefix character varying(32) DEFAULT ''::character varying NOT NULL,
    tvalue character varying(128) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.mtree OWNER TO kamailio;

--
-- Name: mtree_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE mtree_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mtree_id_seq OWNER TO kamailio;

--
-- Name: mtree_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE mtree_id_seq OWNED BY mtree.id;


--
-- Name: mtrees; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE mtrees (
    id integer NOT NULL,
    tname character varying(128) DEFAULT ''::character varying NOT NULL,
    tprefix character varying(32) DEFAULT ''::character varying NOT NULL,
    tvalue character varying(128) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.mtrees OWNER TO kamailio;

--
-- Name: mtrees_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE mtrees_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mtrees_id_seq OWNER TO kamailio;

--
-- Name: mtrees_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE mtrees_id_seq OWNED BY mtrees.id;


--
-- Name: ominicontacto_app_agenda; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_agenda (
    id integer NOT NULL,
    es_personal boolean NOT NULL,
    fecha date NOT NULL,
    hora time without time zone NOT NULL,
    es_smart boolean NOT NULL,
    medio_comunicacion integer NOT NULL,
    telefono character varying(128),
    email character varying(128),
    descripcion text NOT NULL,
    agente_id integer,
    CONSTRAINT ominicontacto_app_agenda_medio_comunicacion_check CHECK ((medio_comunicacion >= 0))
);


ALTER TABLE public.ominicontacto_app_agenda OWNER TO kamailio;

--
-- Name: ominicontacto_app_agenda_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_agenda_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_agenda_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_agenda_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_agenda_id_seq OWNED BY ominicontacto_app_agenda.id;


--
-- Name: ominicontacto_app_agenteprofile; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_agenteprofile (
    id integer NOT NULL,
    sip_extension integer NOT NULL,
    sip_password character varying(128),
    grupo_id integer NOT NULL,
    user_id integer NOT NULL,
    estado integer NOT NULL,
    CONSTRAINT ominicontacto_app_agenteprofile_estado_check CHECK ((estado >= 0))
);


ALTER TABLE public.ominicontacto_app_agenteprofile OWNER TO kamailio;

--
-- Name: ominicontacto_app_agenteprofile_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_agenteprofile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_agenteprofile_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_agenteprofile_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_agenteprofile_id_seq OWNED BY ominicontacto_app_agenteprofile.id;


--
-- Name: ominicontacto_app_agenteprofile_modulos; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_agenteprofile_modulos (
    id integer NOT NULL,
    agenteprofile_id integer NOT NULL,
    modulo_id integer NOT NULL
);


ALTER TABLE public.ominicontacto_app_agenteprofile_modulos OWNER TO kamailio;

--
-- Name: ominicontacto_app_agenteprofile_modulos_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_agenteprofile_modulos_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_agenteprofile_modulos_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_agenteprofile_modulos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_agenteprofile_modulos_id_seq OWNED BY ominicontacto_app_agenteprofile_modulos.id;


--
-- Name: ominicontacto_app_basedatoscontacto; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_basedatoscontacto (
    id integer NOT NULL,
    nombre character varying(128) NOT NULL,
    fecha_alta timestamp with time zone NOT NULL,
    archivo_importacion character varying(256) NOT NULL,
    nombre_archivo_importacion character varying(256) NOT NULL,
    metadata text,
    sin_definir boolean NOT NULL,
    cantidad_contactos integer NOT NULL,
    estado integer NOT NULL,
    oculto boolean NOT NULL,
    CONSTRAINT ominicontacto_app_basedatoscontacto_cantidad_contactos_check CHECK ((cantidad_contactos >= 0)),
    CONSTRAINT ominicontacto_app_basedatoscontacto_estado_check CHECK ((estado >= 0))
);


ALTER TABLE public.ominicontacto_app_basedatoscontacto OWNER TO kamailio;

--
-- Name: ominicontacto_app_basedatoscontacto_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_basedatoscontacto_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_basedatoscontacto_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_basedatoscontacto_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_basedatoscontacto_id_seq OWNED BY ominicontacto_app_basedatoscontacto.id;


--
-- Name: ominicontacto_app_calificacion; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_calificacion (
    id integer NOT NULL,
    nombre character varying(50) NOT NULL
);


ALTER TABLE public.ominicontacto_app_calificacion OWNER TO kamailio;

--
-- Name: ominicontacto_app_calificacion_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_calificacion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_calificacion_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_calificacion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_calificacion_id_seq OWNED BY ominicontacto_app_calificacion.id;


--
-- Name: ominicontacto_app_calificacioncampana; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_calificacioncampana (
    id integer NOT NULL,
    nombre character varying(50) NOT NULL
);


ALTER TABLE public.ominicontacto_app_calificacioncampana OWNER TO kamailio;

--
-- Name: ominicontacto_app_calificacioncampana_calificacion; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_calificacioncampana_calificacion (
    id integer NOT NULL,
    calificacioncampana_id integer NOT NULL,
    calificacion_id integer NOT NULL
);


ALTER TABLE public.ominicontacto_app_calificacioncampana_calificacion OWNER TO kamailio;

--
-- Name: ominicontacto_app_calificacioncampana_calificacion_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_calificacioncampana_calificacion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_calificacioncampana_calificacion_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_calificacioncampana_calificacion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_calificacioncampana_calificacion_id_seq OWNED BY ominicontacto_app_calificacioncampana_calificacion.id;


--
-- Name: ominicontacto_app_calificacioncampana_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_calificacioncampana_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_calificacioncampana_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_calificacioncampana_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_calificacioncampana_id_seq OWNED BY ominicontacto_app_calificacioncampana.id;


--
-- Name: ominicontacto_app_calificacioncliente; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_calificacioncliente (
    id integer NOT NULL,
    es_venta boolean NOT NULL,
    calificacion_id integer,
    campana_id integer NOT NULL,
    contacto_id integer NOT NULL,
    fecha timestamp with time zone NOT NULL,
    agente_id integer NOT NULL,
    observaciones text,
    wombat_id integer NOT NULL
);


ALTER TABLE public.ominicontacto_app_calificacioncliente OWNER TO kamailio;

--
-- Name: ominicontacto_app_calificacioncliente_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_calificacioncliente_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_calificacioncliente_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_calificacioncliente_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_calificacioncliente_id_seq OWNED BY ominicontacto_app_calificacioncliente.id;


--
-- Name: ominicontacto_app_campana; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_campana (
    id integer NOT NULL,
    estado integer NOT NULL,
    nombre character varying(128) NOT NULL,
    fecha_inicio date,
    fecha_fin date,
    bd_contacto_id integer,
    calificacion_campana_id integer NOT NULL,
    formulario_id integer NOT NULL,
    campaign_id_wombat integer,
    oculto boolean NOT NULL,
    CONSTRAINT ominicontacto_app_campana_estado_check CHECK ((estado >= 0))
);


ALTER TABLE public.ominicontacto_app_campana OWNER TO kamailio;

--
-- Name: ominicontacto_app_campana_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_campana_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_campana_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_campana_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_campana_id_seq OWNED BY ominicontacto_app_campana.id;


--
-- Name: ominicontacto_app_chat; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_chat (
    id integer NOT NULL,
    fecha_hora_chat timestamp with time zone NOT NULL,
    agente_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.ominicontacto_app_chat OWNER TO kamailio;

--
-- Name: ominicontacto_app_chat_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_chat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_chat_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_chat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_chat_id_seq OWNED BY ominicontacto_app_chat.id;


--
-- Name: ominicontacto_app_contacto; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_contacto (
    id integer NOT NULL,
    datos text NOT NULL,
    bd_contacto_id integer,
    telefono character varying(128) NOT NULL
);


ALTER TABLE public.ominicontacto_app_contacto OWNER TO kamailio;

--
-- Name: ominicontacto_app_contacto_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_contacto_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_contacto_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_contacto_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_contacto_id_seq OWNED BY ominicontacto_app_contacto.id;


--
-- Name: ominicontacto_app_duraciondellamada; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_duraciondellamada (
    id integer NOT NULL,
    numero_telefono character varying(20) NOT NULL,
    fecha_hora_llamada timestamp with time zone NOT NULL,
    tipo_llamada integer NOT NULL,
    duracion time without time zone NOT NULL,
    agente_id integer NOT NULL,
    CONSTRAINT ominicontacto_app_duraciondellamada_tipo_llamada_check CHECK ((tipo_llamada >= 0))
);


ALTER TABLE public.ominicontacto_app_duraciondellamada OWNER TO kamailio;

--
-- Name: ominicontacto_app_duraciondellamada_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_duraciondellamada_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_duraciondellamada_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_duraciondellamada_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_duraciondellamada_id_seq OWNED BY ominicontacto_app_duraciondellamada.id;


--
-- Name: ominicontacto_app_fieldformulario; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_fieldformulario (
    id integer NOT NULL,
    nombre_campo character varying(64) NOT NULL,
    orden integer NOT NULL,
    tipo integer NOT NULL,
    formulario_id integer NOT NULL,
    values_select text,
    is_required boolean NOT NULL,
    CONSTRAINT ominicontacto_app_fieldformulario_orden_check CHECK ((orden >= 0)),
    CONSTRAINT ominicontacto_app_fieldformulario_tipo_check CHECK ((tipo >= 0))
);


ALTER TABLE public.ominicontacto_app_fieldformulario OWNER TO kamailio;

--
-- Name: ominicontacto_app_fieldformulario_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_fieldformulario_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_fieldformulario_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_fieldformulario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_fieldformulario_id_seq OWNED BY ominicontacto_app_fieldformulario.id;


--
-- Name: ominicontacto_app_formulario; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_formulario (
    id integer NOT NULL,
    nombre character varying(64) NOT NULL,
    descripcion text NOT NULL
);


ALTER TABLE public.ominicontacto_app_formulario OWNER TO kamailio;

--
-- Name: ominicontacto_app_formulario_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_formulario_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_formulario_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_formulario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_formulario_id_seq OWNED BY ominicontacto_app_formulario.id;


--
-- Name: ominicontacto_app_grabacion; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_grabacion (
    id integer NOT NULL,
    fecha timestamp with time zone NOT NULL,
    tipo_llamada integer NOT NULL,
    id_cliente character varying(255) NOT NULL,
    tel_cliente character varying(255) NOT NULL,
    grabacion character varying(255) NOT NULL,
    sip_agente integer NOT NULL,
    campana_id integer NOT NULL,
    CONSTRAINT ominicontacto_app_grabacion_tipo_llamada_check CHECK ((tipo_llamada >= 0))
);


ALTER TABLE public.ominicontacto_app_grabacion OWNER TO kamailio;

--
-- Name: ominicontacto_app_grabacion_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_grabacion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_grabacion_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_grabacion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_grabacion_id_seq OWNED BY ominicontacto_app_grabacion.id;


--
-- Name: ominicontacto_app_grupo; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_grupo (
    id integer NOT NULL,
    nombre character varying(20) NOT NULL,
    auto_attend_dialer boolean NOT NULL,
    auto_attend_ics boolean NOT NULL,
    auto_attend_inbound boolean NOT NULL,
    auto_pause boolean NOT NULL
);


ALTER TABLE public.ominicontacto_app_grupo OWNER TO kamailio;

--
-- Name: ominicontacto_app_grupo_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_grupo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_grupo_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_grupo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_grupo_id_seq OWNED BY ominicontacto_app_grupo.id;


--
-- Name: ominicontacto_app_mensajechat; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_mensajechat (
    id integer NOT NULL,
    mensaje text NOT NULL,
    fecha_hora timestamp with time zone NOT NULL,
    chat_id integer NOT NULL,
    sender_id integer NOT NULL,
    to_id integer NOT NULL
);


ALTER TABLE public.ominicontacto_app_mensajechat OWNER TO kamailio;

--
-- Name: ominicontacto_app_mensajechat_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_mensajechat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_mensajechat_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_mensajechat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_mensajechat_id_seq OWNED BY ominicontacto_app_mensajechat.id;


--
-- Name: ominicontacto_app_metadatacliente; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_metadatacliente (
    id integer NOT NULL,
    metadata text NOT NULL,
    agente_id integer NOT NULL,
    campana_id integer NOT NULL,
    contacto_id integer NOT NULL,
    fecha timestamp with time zone NOT NULL
);


ALTER TABLE public.ominicontacto_app_metadatacliente OWNER TO kamailio;

--
-- Name: ominicontacto_app_metadatacliente_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_metadatacliente_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_metadatacliente_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_metadatacliente_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_metadatacliente_id_seq OWNED BY ominicontacto_app_metadatacliente.id;


--
-- Name: ominicontacto_app_modulo; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_modulo (
    id integer NOT NULL,
    nombre character varying(20) NOT NULL
);


ALTER TABLE public.ominicontacto_app_modulo OWNER TO kamailio;

--
-- Name: ominicontacto_app_modulo_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_modulo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_modulo_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_modulo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_modulo_id_seq OWNED BY ominicontacto_app_modulo.id;


--
-- Name: ominicontacto_app_pausa; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_pausa (
    id integer NOT NULL,
    nombre character varying(20) NOT NULL
);


ALTER TABLE public.ominicontacto_app_pausa OWNER TO kamailio;

--
-- Name: ominicontacto_app_pausa_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_pausa_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_pausa_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_pausa_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_pausa_id_seq OWNED BY ominicontacto_app_pausa.id;


--
-- Name: ominicontacto_app_queuelog; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_queuelog (
    id integer NOT NULL,
    "time" timestamp with time zone NOT NULL,
    callid character varying(32),
    queuename character varying(32),
    campana_id integer,
    agent character varying(32),
    agent_id integer,
    event character varying(32),
    data1 character varying(128),
    data2 character varying(128),
    data3 character varying(128),
    data4 character varying(128),
    data5 character varying(128)
);


ALTER TABLE public.ominicontacto_app_queuelog OWNER TO kamailio;

--
-- Name: ominicontacto_app_queuelog_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_queuelog_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_queuelog_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_queuelog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_queuelog_id_seq OWNED BY ominicontacto_app_queuelog.id;


--
-- Name: ominicontacto_app_user; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(30) NOT NULL,
    first_name character varying(30) NOT NULL,
    last_name character varying(30) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL,
    is_agente boolean NOT NULL,
    is_customer boolean NOT NULL,
    is_supervisor boolean NOT NULL
);


ALTER TABLE public.ominicontacto_app_user OWNER TO kamailio;

--
-- Name: ominicontacto_app_user_groups; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_user_groups (
    id integer NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.ominicontacto_app_user_groups OWNER TO kamailio;

--
-- Name: ominicontacto_app_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_user_groups_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_user_groups_id_seq OWNED BY ominicontacto_app_user_groups.id;


--
-- Name: ominicontacto_app_user_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_user_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_user_id_seq OWNED BY ominicontacto_app_user.id;


--
-- Name: ominicontacto_app_user_user_permissions; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_user_user_permissions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.ominicontacto_app_user_user_permissions OWNER TO kamailio;

--
-- Name: ominicontacto_app_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_user_user_permissions_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_user_user_permissions_id_seq OWNED BY ominicontacto_app_user_user_permissions.id;


--
-- Name: ominicontacto_app_wombatlog; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE ominicontacto_app_wombatlog (
    id integer NOT NULL,
    telefono character varying(128) NOT NULL,
    estado character varying(128) NOT NULL,
    calificacion character varying(128) NOT NULL,
    timeout integer NOT NULL,
    metadata text NOT NULL,
    fecha_hora timestamp with time zone NOT NULL,
    agente_id integer,
    campana_id integer NOT NULL,
    contacto_id integer NOT NULL
);


ALTER TABLE public.ominicontacto_app_wombatlog OWNER TO kamailio;

--
-- Name: ominicontacto_app_wombatlog_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE ominicontacto_app_wombatlog_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ominicontacto_app_wombatlog_id_seq OWNER TO kamailio;

--
-- Name: ominicontacto_app_wombatlog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE ominicontacto_app_wombatlog_id_seq OWNED BY ominicontacto_app_wombatlog.id;


--
-- Name: pdt; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE pdt (
    id integer NOT NULL,
    sdomain character varying(128) NOT NULL,
    prefix character varying(32) NOT NULL,
    domain character varying(128) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.pdt OWNER TO kamailio;

--
-- Name: pdt_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE pdt_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pdt_id_seq OWNER TO kamailio;

--
-- Name: pdt_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE pdt_id_seq OWNED BY pdt.id;


--
-- Name: pl_pipes; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE pl_pipes (
    id integer NOT NULL,
    pipeid character varying(64) DEFAULT ''::character varying NOT NULL,
    algorithm character varying(32) DEFAULT ''::character varying NOT NULL,
    plimit integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.pl_pipes OWNER TO kamailio;

--
-- Name: pl_pipes_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE pl_pipes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pl_pipes_id_seq OWNER TO kamailio;

--
-- Name: pl_pipes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE pl_pipes_id_seq OWNED BY pl_pipes.id;


--
-- Name: presentity; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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


ALTER TABLE public.presentity OWNER TO kamailio;

--
-- Name: presentity_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE presentity_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.presentity_id_seq OWNER TO kamailio;

--
-- Name: presentity_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE presentity_id_seq OWNED BY presentity.id;


--
-- Name: pua; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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


ALTER TABLE public.pua OWNER TO kamailio;

--
-- Name: pua_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE pua_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pua_id_seq OWNER TO kamailio;

--
-- Name: pua_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE pua_id_seq OWNED BY pua.id;


--
-- Name: purplemap; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE purplemap (
    id integer NOT NULL,
    sip_user character varying(128) NOT NULL,
    ext_user character varying(128) NOT NULL,
    ext_prot character varying(16) NOT NULL,
    ext_pass character varying(64)
);


ALTER TABLE public.purplemap OWNER TO kamailio;

--
-- Name: purplemap_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE purplemap_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.purplemap_id_seq OWNER TO kamailio;

--
-- Name: purplemap_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE purplemap_id_seq OWNED BY purplemap.id;


--
-- Name: queue_member_table; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE queue_member_table (
    id integer NOT NULL,
    membername character varying(128) NOT NULL,
    interface character varying(128) NOT NULL,
    penalty integer NOT NULL,
    paused integer NOT NULL,
    member_id integer NOT NULL,
    queue_name character varying(128) NOT NULL
);


ALTER TABLE public.queue_member_table OWNER TO kamailio;

--
-- Name: queue_member_table_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE queue_member_table_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.queue_member_table_id_seq OWNER TO kamailio;

--
-- Name: queue_member_table_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE queue_member_table_id_seq OWNED BY queue_member_table.id;


--
-- Name: queue_table; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE queue_table (
    name character varying(128) NOT NULL,
    timeout bigint NOT NULL,
    retry bigint NOT NULL,
    maxlen bigint NOT NULL,
    wrapuptime bigint NOT NULL,
    servicelevel bigint NOT NULL,
    strategy character varying(128) NOT NULL,
    eventmemberstatus boolean NOT NULL,
    eventwhencalled boolean NOT NULL,
    weight bigint NOT NULL,
    ringinuse boolean NOT NULL,
    setinterfacevar boolean NOT NULL,
    musiconhold character varying(128),
    announce character varying(128),
    context character varying(128),
    monitor_join boolean,
    monitor_format character varying(128),
    queue_youarenext character varying(128),
    queue_thereare character varying(128),
    queue_callswaiting character varying(128),
    queue_holdtime character varying(128),
    queue_minutes character varying(128),
    queue_seconds character varying(128),
    queue_lessthan character varying(128),
    queue_thankyou character varying(128),
    queue_reporthold character varying(128),
    announce_frequency bigint,
    announce_round_seconds bigint,
    announce_holdtime character varying(128),
    joinempty character varying(128),
    leavewhenempty character varying(128),
    reportholdtime boolean,
    memberdelay bigint,
    timeoutrestart boolean,
    type integer NOT NULL,
    wait integer NOT NULL,
    queue_asterisk integer NOT NULL,
    auto_grabacion boolean NOT NULL,
    campana_id integer,
    ep_id_wombat integer,
    CONSTRAINT queue_table_queue_asterisk_check CHECK ((queue_asterisk >= 0)),
    CONSTRAINT queue_table_type_check CHECK ((type >= 0)),
    CONSTRAINT queue_table_wait_check CHECK ((wait >= 0))
);


ALTER TABLE public.queue_table OWNER TO kamailio;

--
-- Name: re_grp; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE re_grp (
    id integer NOT NULL,
    reg_exp character varying(128) DEFAULT ''::character varying NOT NULL,
    group_id integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.re_grp OWNER TO kamailio;

--
-- Name: re_grp_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE re_grp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.re_grp_id_seq OWNER TO kamailio;

--
-- Name: re_grp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE re_grp_id_seq OWNED BY re_grp.id;


--
-- Name: rls_presentity; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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


ALTER TABLE public.rls_presentity OWNER TO kamailio;

--
-- Name: rls_presentity_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE rls_presentity_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rls_presentity_id_seq OWNER TO kamailio;

--
-- Name: rls_presentity_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE rls_presentity_id_seq OWNED BY rls_presentity.id;


--
-- Name: rls_watchers; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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


ALTER TABLE public.rls_watchers OWNER TO kamailio;

--
-- Name: rls_watchers_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE rls_watchers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rls_watchers_id_seq OWNER TO kamailio;

--
-- Name: rls_watchers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE rls_watchers_id_seq OWNED BY rls_watchers.id;


--
-- Name: rtpproxy; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE rtpproxy (
    id integer NOT NULL,
    setid character varying(32) DEFAULT 0 NOT NULL,
    url character varying(64) DEFAULT ''::character varying NOT NULL,
    flags integer DEFAULT 0 NOT NULL,
    weight integer DEFAULT 1 NOT NULL,
    description character varying(64) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.rtpproxy OWNER TO kamailio;

--
-- Name: rtpproxy_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE rtpproxy_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rtpproxy_id_seq OWNER TO kamailio;

--
-- Name: rtpproxy_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE rtpproxy_id_seq OWNED BY rtpproxy.id;


--
-- Name: sca_subscriptions; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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


ALTER TABLE public.sca_subscriptions OWNER TO kamailio;

--
-- Name: sca_subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE sca_subscriptions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sca_subscriptions_id_seq OWNER TO kamailio;

--
-- Name: sca_subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE sca_subscriptions_id_seq OWNED BY sca_subscriptions.id;


--
-- Name: silo; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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


ALTER TABLE public.silo OWNER TO kamailio;

--
-- Name: silo_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE silo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.silo_id_seq OWNER TO kamailio;

--
-- Name: silo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE silo_id_seq OWNED BY silo.id;


--
-- Name: sip_trace; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE sip_trace (
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


ALTER TABLE public.sip_trace OWNER TO kamailio;

--
-- Name: sip_trace_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE sip_trace_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sip_trace_id_seq OWNER TO kamailio;

--
-- Name: sip_trace_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE sip_trace_id_seq OWNED BY sip_trace.id;


--
-- Name: speed_dial; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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


ALTER TABLE public.speed_dial OWNER TO kamailio;

--
-- Name: speed_dial_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE speed_dial_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.speed_dial_id_seq OWNER TO kamailio;

--
-- Name: speed_dial_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE speed_dial_id_seq OWNED BY speed_dial.id;


--
-- Name: subscriber; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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


ALTER TABLE public.subscriber OWNER TO kamailio;

--
-- Name: subscriber_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE subscriber_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.subscriber_id_seq OWNER TO kamailio;

--
-- Name: subscriber_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE subscriber_id_seq OWNED BY subscriber.id;


--
-- Name: topos_d; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE topos_d (
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


ALTER TABLE public.topos_d OWNER TO kamailio;

--
-- Name: topos_d_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE topos_d_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.topos_d_id_seq OWNER TO kamailio;

--
-- Name: topos_d_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE topos_d_id_seq OWNED BY topos_d.id;


--
-- Name: topos_t; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE topos_t (
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


ALTER TABLE public.topos_t OWNER TO kamailio;

--
-- Name: topos_t_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE topos_t_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.topos_t_id_seq OWNER TO kamailio;

--
-- Name: topos_t_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE topos_t_id_seq OWNED BY topos_t.id;


--
-- Name: trusted; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE trusted (
    id integer NOT NULL,
    src_ip character varying(50) NOT NULL,
    proto character varying(4) NOT NULL,
    from_pattern character varying(64) DEFAULT NULL::character varying,
    ruri_pattern character varying(64) DEFAULT NULL::character varying,
    tag character varying(64),
    priority integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.trusted OWNER TO kamailio;

--
-- Name: trusted_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE trusted_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trusted_id_seq OWNER TO kamailio;

--
-- Name: trusted_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE trusted_id_seq OWNED BY trusted.id;


--
-- Name: uacreg; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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
    expires integer DEFAULT 0 NOT NULL,
    flags integer DEFAULT 0 NOT NULL,
    reg_delay integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.uacreg OWNER TO kamailio;

--
-- Name: uacreg_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE uacreg_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.uacreg_id_seq OWNER TO kamailio;

--
-- Name: uacreg_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE uacreg_id_seq OWNED BY uacreg.id;


--
-- Name: uri; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE uri (
    id integer NOT NULL,
    username character varying(64) DEFAULT ''::character varying NOT NULL,
    domain character varying(64) DEFAULT ''::character varying NOT NULL,
    uri_user character varying(64) DEFAULT ''::character varying NOT NULL,
    last_modified timestamp without time zone DEFAULT '2000-01-01 00:00:01'::timestamp without time zone NOT NULL
);


ALTER TABLE public.uri OWNER TO kamailio;

--
-- Name: uri_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE uri_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.uri_id_seq OWNER TO kamailio;

--
-- Name: uri_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE uri_id_seq OWNED BY uri.id;


--
-- Name: userblacklist; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE userblacklist (
    id integer NOT NULL,
    username character varying(64) DEFAULT ''::character varying NOT NULL,
    domain character varying(64) DEFAULT ''::character varying NOT NULL,
    prefix character varying(64) DEFAULT ''::character varying NOT NULL,
    whitelist smallint DEFAULT 0 NOT NULL
);


ALTER TABLE public.userblacklist OWNER TO kamailio;

--
-- Name: userblacklist_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE userblacklist_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.userblacklist_id_seq OWNER TO kamailio;

--
-- Name: userblacklist_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE userblacklist_id_seq OWNED BY userblacklist.id;


--
-- Name: usr_preferences; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE usr_preferences (
    id integer NOT NULL,
    uuid character varying(64) DEFAULT ''::character varying NOT NULL,
    username character varying(128) DEFAULT 0 NOT NULL,
    domain character varying(64) DEFAULT ''::character varying NOT NULL,
    attribute character varying(32) DEFAULT ''::character varying NOT NULL,
    type integer DEFAULT 0 NOT NULL,
    value character varying(128) DEFAULT ''::character varying NOT NULL,
    last_modified timestamp without time zone DEFAULT '2000-01-01 00:00:01'::timestamp without time zone NOT NULL
);


ALTER TABLE public.usr_preferences OWNER TO kamailio;

--
-- Name: usr_preferences_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE usr_preferences_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.usr_preferences_id_seq OWNER TO kamailio;

--
-- Name: usr_preferences_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE usr_preferences_id_seq OWNED BY usr_preferences.id;


--
-- Name: version; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE TABLE version (
    table_name character varying(32) NOT NULL,
    table_version integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.version OWNER TO kamailio;

--
-- Name: watchers; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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


ALTER TABLE public.watchers OWNER TO kamailio;

--
-- Name: watchers_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE watchers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.watchers_id_seq OWNER TO kamailio;

--
-- Name: watchers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kamailio
--

ALTER SEQUENCE watchers_id_seq OWNED BY watchers.id;


--
-- Name: xcap; Type: TABLE; Schema: public; Owner: kamailio; Tablespace: 
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


ALTER TABLE public.xcap OWNER TO kamailio;

--
-- Name: xcap_id_seq; Type: SEQUENCE; Schema: public; Owner: kamailio
--

CREATE SEQUENCE xcap_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.xcap_id_seq OWNER TO kamailio;

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

ALTER TABLE ONLY auth_group ALTER COLUMN id SET DEFAULT nextval('auth_group_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('auth_group_permissions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY auth_permission ALTER COLUMN id SET DEFAULT nextval('auth_permission_id_seq'::regclass);


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

ALTER TABLE ONLY django_admin_log ALTER COLUMN id SET DEFAULT nextval('django_admin_log_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY django_content_type ALTER COLUMN id SET DEFAULT nextval('django_content_type_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY django_migrations ALTER COLUMN id SET DEFAULT nextval('django_migrations_id_seq'::regclass);


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
-- Name: gwid; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY dr_gateways ALTER COLUMN gwid SET DEFAULT nextval('dr_gateways_gwid_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY dr_groups ALTER COLUMN id SET DEFAULT nextval('dr_groups_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY dr_gw_lists ALTER COLUMN id SET DEFAULT nextval('dr_gw_lists_id_seq'::regclass);


--
-- Name: ruleid; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY dr_rules ALTER COLUMN ruleid SET DEFAULT nextval('dr_rules_ruleid_seq'::regclass);


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

ALTER TABLE ONLY mensaje_enviado ALTER COLUMN id SET DEFAULT nextval('mensaje_enviado_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY mensaje_recibido ALTER COLUMN id SET DEFAULT nextval('mensaje_recibido_id_seq'::regclass);


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

ALTER TABLE ONLY ominicontacto_app_agenda ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_agenda_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_agenteprofile ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_agenteprofile_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_agenteprofile_modulos ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_agenteprofile_modulos_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_basedatoscontacto ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_basedatoscontacto_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_calificacion ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_calificacion_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_calificacioncampana ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_calificacioncampana_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_calificacioncampana_calificacion ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_calificacioncampana_calificacion_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_calificacioncliente ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_calificacioncliente_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_campana ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_campana_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_chat ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_chat_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_contacto ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_contacto_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_duraciondellamada ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_duraciondellamada_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_fieldformulario ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_fieldformulario_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_formulario ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_formulario_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_grabacion ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_grabacion_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_grupo ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_grupo_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_mensajechat ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_mensajechat_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_metadatacliente ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_metadatacliente_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_modulo ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_modulo_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_pausa ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_pausa_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_queuelog ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_queuelog_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_user ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_user_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_user_groups ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_user_groups_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_user_user_permissions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_wombatlog ALTER COLUMN id SET DEFAULT nextval('ominicontacto_app_wombatlog_id_seq'::regclass);


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

ALTER TABLE ONLY queue_member_table ALTER COLUMN id SET DEFAULT nextval('queue_member_table_id_seq'::regclass);


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

ALTER TABLE ONLY topos_d ALTER COLUMN id SET DEFAULT nextval('topos_d_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY topos_t ALTER COLUMN id SET DEFAULT nextval('topos_t_id_seq'::regclass);


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

COPY active_watchers (id, presentity_uri, watcher_username, watcher_domain, to_user, to_domain, event, event_id, to_tag, from_tag, callid, local_cseq, remote_cseq, contact, record_route, expires, status, reason, version, socket_info, local_contact, from_user, from_domain, updated, updated_winfo, flags, user_agent) FROM stdin;
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
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY auth_group (id, name) FROM stdin;
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('auth_group_id_seq', 1, false);


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('auth_group_permissions_id_seq', 1, false);


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY auth_permission (id, name, content_type_id, codename) FROM stdin;
\.


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('auth_permission_id_seq', 1, false);


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
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
\.


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('django_admin_log_id_seq', 1, false);


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY django_content_type (id, app_label, model) FROM stdin;
\.


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('django_content_type_id_seq', 1, false);


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2017-10-18 21:05:15.256632+00
2	contenttypes	0002_remove_content_type_name	2017-10-18 21:05:15.269462+00
3	auth	0001_initial	2017-10-18 21:05:15.340472+00
4	auth	0002_alter_permission_name_max_length	2017-10-18 21:05:15.350919+00
5	auth	0003_alter_user_email_max_length	2017-10-18 21:05:15.36305+00
6	auth	0004_alter_user_username_opts	2017-10-18 21:05:15.373283+00
7	auth	0005_alter_user_last_login_null	2017-10-18 21:05:15.383944+00
8	auth	0006_require_contenttypes_0002	2017-10-18 21:05:15.388836+00
9	auth	0007_alter_validators_add_error_messages	2017-10-18 21:05:15.407414+00
10	ominicontacto_app	0001_initial	2017-10-18 21:05:15.637735+00
11	admin	0001_initial	2017-10-18 21:05:15.683007+00
12	admin	0002_logentry_remove_auto_add	2017-10-18 21:05:15.722277+00
13	ominicontacto_app	0002_auto_20160628_1553	2017-10-18 21:05:15.83501+00
14	ominicontacto_app	0003_auto_20160628_1600	2017-10-18 21:05:15.878529+00
15	ominicontacto_app	0004_auto_20160629_1917	2017-10-18 21:05:15.982769+00
16	ominicontacto_app	0005_user_node_password	2017-10-18 21:05:16.021404+00
17	ominicontacto_app	0006_mensajeenviado_mensajerecibido	2017-10-18 21:05:16.082706+00
18	ominicontacto_app	0007_remove_user_node_password	2017-10-18 21:05:16.122019+00
19	ominicontacto_app	0005_basedatoscontacto	2017-10-18 21:05:16.142816+00
20	ominicontacto_app	0006_contacto	2017-10-18 21:05:16.166786+00
21	ominicontacto_app	0007_auto_20160713_2040	2017-10-18 21:05:16.202579+00
22	ominicontacto_app	0008_merge	2017-10-18 21:05:16.205866+00
23	ominicontacto_app	0009_auto_20160725_1401	2017-10-18 21:05:16.325788+00
24	ominicontacto_app	0010_grupo_auto_pause	2017-10-18 21:05:16.363939+00
25	ominicontacto_app	0011_auto_20160726_2002	2017-10-18 21:05:16.447483+00
26	ominicontacto_app	0012_auto_20160727_1806	2017-10-18 21:05:16.494337+00
27	ominicontacto_app	0013_auto_20160727_1929	2017-10-18 21:05:16.559497+00
28	ominicontacto_app	0014_auto_20160801_1918	2017-10-18 21:05:16.614028+00
29	ominicontacto_app	0015_queue_auto_grabacion	2017-10-18 21:05:16.664821+00
30	ominicontacto_app	0016_campana	2017-10-18 21:05:16.692847+00
31	ominicontacto_app	0017_queue_campana	2017-10-18 21:05:16.743463+00
32	ominicontacto_app	0018_auto_20160818_1540	2017-10-18 21:05:16.871691+00
33	ominicontacto_app	0019_formulariodemo	2017-10-18 21:05:16.920172+00
34	ominicontacto_app	0020_auto_20160829_1915	2017-10-18 21:05:17.148372+00
35	ominicontacto_app	0021_auto_20160907_1629	2017-10-18 21:05:17.245102+00
36	ominicontacto_app	0022_auto_20160908_1515	2017-10-18 21:05:17.30387+00
37	ominicontacto_app	0023_auto_20160909_1436	2017-10-18 21:05:17.365892+00
38	ominicontacto_app	0024_auto_20160921_1117	2017-10-18 21:05:17.512244+00
39	ominicontacto_app	0025_contacto_telefono	2017-10-18 21:05:17.56254+00
40	ominicontacto_app	0026_formulariodatoventa	2017-10-18 21:05:17.64215+00
41	ominicontacto_app	0027_auto_20160929_1518	2017-10-18 21:05:17.812264+00
42	ominicontacto_app	0028_auto_20160929_1528	2017-10-18 21:05:17.860902+00
43	ominicontacto_app	0029_auto_20161004_1628	2017-10-18 21:05:17.971106+00
44	ominicontacto_app	0030_campana_calificacion_campana	2017-10-18 21:05:18.034682+00
45	ominicontacto_app	0031_calificacioncliente	2017-10-18 21:05:18.11728+00
46	ominicontacto_app	0032_auto_20161104_1417	2017-10-18 21:05:18.714642+00
47	ominicontacto_app	0033_duraciondellamada	2017-10-18 21:05:18.775151+00
48	ominicontacto_app	0033_calificacioncliente_fecha	2017-10-18 21:05:18.854508+00
49	ominicontacto_app	0034_calificacioncliente_agente	2017-10-18 21:05:18.934169+00
50	ominicontacto_app	0035_auto_20161206_1531	2017-10-18 21:05:18.973436+00
51	ominicontacto_app	0036_auto_20161207_1627	2017-10-18 21:05:18.996147+00
52	ominicontacto_app	0035_calificacioncliente_observaciones	2017-10-18 21:05:19.072216+00
53	ominicontacto_app	0037_merge	2017-10-18 21:05:19.076138+00
54	ominicontacto_app	0038_fieldformulario_values_select	2017-10-18 21:05:19.096318+00
55	ominicontacto_app	0039_metadatacliente	2017-10-18 21:05:19.177894+00
56	ominicontacto_app	0040_auto_20170102_1431	2017-10-18 21:05:19.438013+00
57	ominicontacto_app	0041_campana_formulario	2017-10-18 21:05:19.509824+00
58	ominicontacto_app	0042_metadatacliente_fecha	2017-10-18 21:05:19.591544+00
59	ominicontacto_app	0042_chat_mensajechat	2017-10-18 21:05:19.748609+00
60	ominicontacto_app	0043_merge	2017-10-18 21:05:19.752289+00
61	ominicontacto_app	0044_campana_campaign_id_wombat	2017-10-18 21:05:19.82655+00
62	ominicontacto_app	0045_queue_ep_id_wombat	2017-10-18 21:05:19.903077+00
63	ominicontacto_app	0044_auto_20170127_1127	2017-10-18 21:05:20.157143+00
64	ominicontacto_app	0045_calificacioncliente_wombat_id	2017-10-18 21:05:20.2289+00
65	ominicontacto_app	0046_merge	2017-10-18 21:05:20.233479+00
66	ominicontacto_app	0047_auto_20170202_1646	2017-10-18 21:05:20.372231+00
67	ominicontacto_app	0048_auto_20170213_1725	2017-10-18 21:05:20.471757+00
68	ominicontacto_app	0049_campana_oculto	2017-10-18 21:05:20.541825+00
69	ominicontacto_app	0050_basedatoscontacto_oculto	2017-10-18 21:05:20.622286+00
70	ominicontacto_app	0051_wombatlog	2017-10-18 21:05:20.701576+00
71	ominicontacto_app	0052_auto_20170220_1137	2017-10-18 21:05:20.796726+00
72	ominicontacto_app	0053_auto_20170220_1520	2017-10-18 21:05:20.956052+00
73	ominicontacto_app	0054_wombatlog	2017-10-18 21:05:21.044367+00
74	ominicontacto_app	0055_queuelog	2017-10-18 21:05:21.060518+00
75	ominicontacto_app	0055_agenteprofile_estado	2017-10-18 21:05:21.145123+00
76	ominicontacto_app	0056_merge	2017-10-18 21:05:21.14897+00
77	ominicontacto_app	0058_remove_contacto_id_cliente	2017-10-18 21:05:21.230379+00
78	ominicontacto_app	0059_auto_20170412_1035	2017-10-18 21:05:21.473395+00
\.


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('django_migrations_id_seq', 78, true);


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
-- Data for Name: dr_gateways; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY dr_gateways (gwid, type, address, strip, pri_prefix, attrs, description) FROM stdin;
\.


--
-- Name: dr_gateways_gwid_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('dr_gateways_gwid_seq', 1, false);


--
-- Data for Name: dr_groups; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY dr_groups (id, username, domain, groupid, description) FROM stdin;
\.


--
-- Name: dr_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('dr_groups_id_seq', 1, false);


--
-- Data for Name: dr_gw_lists; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY dr_gw_lists (id, gwlist, description) FROM stdin;
\.


--
-- Name: dr_gw_lists_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('dr_gw_lists_id_seq', 1, false);


--
-- Data for Name: dr_rules; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY dr_rules (ruleid, groupid, prefix, timerec, priority, routeid, gwlist, description) FROM stdin;
\.


--
-- Name: dr_rules_ruleid_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('dr_rules_ruleid_seq', 1, false);


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

SELECT pg_catalog.setval('location_id_seq', 1, false);


--
-- Data for Name: mensaje_enviado; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY mensaje_enviado (id, remitente, destinatario, "timestamp", content, result, agente_id) FROM stdin;
\.


--
-- Name: mensaje_enviado_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('mensaje_enviado_id_seq', 1, false);


--
-- Data for Name: mensaje_recibido; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY mensaje_recibido (id, remitente, destinatario, "timestamp", timezone, encoding, content, es_leido) FROM stdin;
\.


--
-- Name: mensaje_recibido_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('mensaje_recibido_id_seq', 1, false);


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
-- Data for Name: ominicontacto_app_agenda; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_agenda (id, es_personal, fecha, hora, es_smart, medio_comunicacion, telefono, email, descripcion, agente_id) FROM stdin;
\.


--
-- Name: ominicontacto_app_agenda_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_agenda_id_seq', 1, false);


--
-- Data for Name: ominicontacto_app_agenteprofile; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_agenteprofile (id, sip_extension, sip_password, grupo_id, user_id, estado) FROM stdin;
\.


--
-- Name: ominicontacto_app_agenteprofile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_agenteprofile_id_seq', 1, false);


--
-- Data for Name: ominicontacto_app_agenteprofile_modulos; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_agenteprofile_modulos (id, agenteprofile_id, modulo_id) FROM stdin;
\.


--
-- Name: ominicontacto_app_agenteprofile_modulos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_agenteprofile_modulos_id_seq', 1, false);


--
-- Data for Name: ominicontacto_app_basedatoscontacto; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_basedatoscontacto (id, nombre, fecha_alta, archivo_importacion, nombre_archivo_importacion, metadata, sin_definir, cantidad_contactos, estado, oculto) FROM stdin;
\.


--
-- Name: ominicontacto_app_basedatoscontacto_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_basedatoscontacto_id_seq', 1, false);


--
-- Data for Name: ominicontacto_app_calificacion; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_calificacion (id, nombre) FROM stdin;
\.


--
-- Name: ominicontacto_app_calificacion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_calificacion_id_seq', 1, false);


--
-- Data for Name: ominicontacto_app_calificacioncampana; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_calificacioncampana (id, nombre) FROM stdin;
\.


--
-- Data for Name: ominicontacto_app_calificacioncampana_calificacion; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_calificacioncampana_calificacion (id, calificacioncampana_id, calificacion_id) FROM stdin;
\.


--
-- Name: ominicontacto_app_calificacioncampana_calificacion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_calificacioncampana_calificacion_id_seq', 1, false);


--
-- Name: ominicontacto_app_calificacioncampana_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_calificacioncampana_id_seq', 1, false);


--
-- Data for Name: ominicontacto_app_calificacioncliente; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_calificacioncliente (id, es_venta, calificacion_id, campana_id, contacto_id, fecha, agente_id, observaciones, wombat_id) FROM stdin;
\.


--
-- Name: ominicontacto_app_calificacioncliente_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_calificacioncliente_id_seq', 1, false);


--
-- Data for Name: ominicontacto_app_campana; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_campana (id, estado, nombre, fecha_inicio, fecha_fin, bd_contacto_id, calificacion_campana_id, formulario_id, campaign_id_wombat, oculto) FROM stdin;
\.


--
-- Name: ominicontacto_app_campana_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_campana_id_seq', 1, false);


--
-- Data for Name: ominicontacto_app_chat; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_chat (id, fecha_hora_chat, agente_id, user_id) FROM stdin;
\.


--
-- Name: ominicontacto_app_chat_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_chat_id_seq', 1, false);


--
-- Data for Name: ominicontacto_app_contacto; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_contacto (id, datos, bd_contacto_id, telefono) FROM stdin;
\.


--
-- Name: ominicontacto_app_contacto_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_contacto_id_seq', 1, false);


--
-- Data for Name: ominicontacto_app_duraciondellamada; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_duraciondellamada (id, numero_telefono, fecha_hora_llamada, tipo_llamada, duracion, agente_id) FROM stdin;
\.


--
-- Name: ominicontacto_app_duraciondellamada_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_duraciondellamada_id_seq', 1, false);


--
-- Data for Name: ominicontacto_app_fieldformulario; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_fieldformulario (id, nombre_campo, orden, tipo, formulario_id, values_select, is_required) FROM stdin;
\.


--
-- Name: ominicontacto_app_fieldformulario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_fieldformulario_id_seq', 1, false);


--
-- Data for Name: ominicontacto_app_formulario; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_formulario (id, nombre, descripcion) FROM stdin;
\.


--
-- Name: ominicontacto_app_formulario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_formulario_id_seq', 1, false);


--
-- Data for Name: ominicontacto_app_grabacion; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_grabacion (id, fecha, tipo_llamada, id_cliente, tel_cliente, grabacion, sip_agente, campana_id) FROM stdin;
\.


--
-- Name: ominicontacto_app_grabacion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_grabacion_id_seq', 1, false);


--
-- Data for Name: ominicontacto_app_grupo; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_grupo (id, nombre, auto_attend_dialer, auto_attend_ics, auto_attend_inbound, auto_pause) FROM stdin;
\.


--
-- Name: ominicontacto_app_grupo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_grupo_id_seq', 1, false);


--
-- Data for Name: ominicontacto_app_mensajechat; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_mensajechat (id, mensaje, fecha_hora, chat_id, sender_id, to_id) FROM stdin;
\.


--
-- Name: ominicontacto_app_mensajechat_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_mensajechat_id_seq', 1, false);


--
-- Data for Name: ominicontacto_app_metadatacliente; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_metadatacliente (id, metadata, agente_id, campana_id, contacto_id, fecha) FROM stdin;
\.


--
-- Name: ominicontacto_app_metadatacliente_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_metadatacliente_id_seq', 1, false);


--
-- Data for Name: ominicontacto_app_modulo; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_modulo (id, nombre) FROM stdin;
\.


--
-- Name: ominicontacto_app_modulo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_modulo_id_seq', 1, false);


--
-- Data for Name: ominicontacto_app_pausa; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_pausa (id, nombre) FROM stdin;
\.


--
-- Name: ominicontacto_app_pausa_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_pausa_id_seq', 1, false);


--
-- Data for Name: ominicontacto_app_queuelog; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_queuelog (id, "time", callid, queuename, campana_id, agent, agent_id, event, data1, data2, data3, data4, data5) FROM stdin;
\.


--
-- Name: ominicontacto_app_queuelog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_queuelog_id_seq', 1, false);


--
-- Data for Name: ominicontacto_app_user; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, is_agente, is_customer, is_supervisor) FROM stdin;
\.


--
-- Data for Name: ominicontacto_app_user_groups; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Name: ominicontacto_app_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_user_groups_id_seq', 1, false);


--
-- Name: ominicontacto_app_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_user_id_seq', 1, false);


--
-- Data for Name: ominicontacto_app_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Name: ominicontacto_app_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_user_user_permissions_id_seq', 1, false);


--
-- Data for Name: ominicontacto_app_wombatlog; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY ominicontacto_app_wombatlog (id, telefono, estado, calificacion, timeout, metadata, fecha_hora, agente_id, campana_id, contacto_id) FROM stdin;
\.


--
-- Name: ominicontacto_app_wombatlog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('ominicontacto_app_wombatlog_id_seq', 1, false);


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
-- Data for Name: queue_member_table; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY queue_member_table (id, membername, interface, penalty, paused, member_id, queue_name) FROM stdin;
\.


--
-- Name: queue_member_table_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('queue_member_table_id_seq', 1, false);


--
-- Data for Name: queue_table; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY queue_table (name, timeout, retry, maxlen, wrapuptime, servicelevel, strategy, eventmemberstatus, eventwhencalled, weight, ringinuse, setinterfacevar, musiconhold, announce, context, monitor_join, monitor_format, queue_youarenext, queue_thereare, queue_callswaiting, queue_holdtime, queue_minutes, queue_seconds, queue_lessthan, queue_thankyou, queue_reporthold, announce_frequency, announce_round_seconds, announce_holdtime, joinempty, leavewhenempty, reportholdtime, memberdelay, timeoutrestart, type, wait, queue_asterisk, auto_grabacion, campana_id, ep_id_wombat) FROM stdin;
\.


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
\.


--
-- Name: subscriber_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('subscriber_id_seq', 1, false);


--
-- Data for Name: topos_d; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY topos_d (id, rectime, s_method, s_cseq, a_callid, a_uuid, b_uuid, a_contact, b_contact, as_contact, bs_contact, a_tag, b_tag, a_rr, b_rr, s_rr, iflags, a_uri, b_uri, r_uri, a_srcaddr, b_srcaddr, a_socket, b_socket) FROM stdin;
\.


--
-- Name: topos_d_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('topos_d_id_seq', 1, false);


--
-- Data for Name: topos_t; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY topos_t (id, rectime, s_method, s_cseq, a_callid, a_uuid, b_uuid, direction, x_via, x_vbranch, x_rr, y_rr, s_rr, x_uri, a_contact, b_contact, as_contact, bs_contact, x_tag, a_tag, b_tag, a_srcaddr, b_srcaddr, a_socket, b_socket) FROM stdin;
\.


--
-- Name: topos_t_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('topos_t_id_seq', 1, false);


--
-- Data for Name: trusted; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY trusted (id, src_ip, proto, from_pattern, ruri_pattern, tag, priority) FROM stdin;
\.


--
-- Name: trusted_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kamailio
--

SELECT pg_catalog.setval('trusted_id_seq', 1, false);


--
-- Data for Name: uacreg; Type: TABLE DATA; Schema: public; Owner: kamailio
--

COPY uacreg (id, l_uuid, l_username, l_domain, r_username, r_domain, realm, auth_username, auth_password, auth_proxy, expires, flags, reg_delay) FROM stdin;
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
-- Name: acc_cdrs_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY acc_cdrs
    ADD CONSTRAINT acc_cdrs_pkey PRIMARY KEY (id);


--
-- Name: acc_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY acc
    ADD CONSTRAINT acc_pkey PRIMARY KEY (id);


--
-- Name: active_watchers_active_watchers_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY active_watchers
    ADD CONSTRAINT active_watchers_active_watchers_idx UNIQUE (callid, to_tag, from_tag);


--
-- Name: active_watchers_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY active_watchers
    ADD CONSTRAINT active_watchers_pkey PRIMARY KEY (id);


--
-- Name: address_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY address
    ADD CONSTRAINT address_pkey PRIMARY KEY (id);


--
-- Name: aliases_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY aliases
    ADD CONSTRAINT aliases_pkey PRIMARY KEY (id);


--
-- Name: aliases_ruid_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY aliases
    ADD CONSTRAINT aliases_ruid_idx UNIQUE (ruid);


--
-- Name: auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions_group_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission_content_type_id_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: carrier_name_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY carrier_name
    ADD CONSTRAINT carrier_name_pkey PRIMARY KEY (id);


--
-- Name: carrierfailureroute_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY carrierfailureroute
    ADD CONSTRAINT carrierfailureroute_pkey PRIMARY KEY (id);


--
-- Name: carrierroute_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY carrierroute
    ADD CONSTRAINT carrierroute_pkey PRIMARY KEY (id);


--
-- Name: cpl_account_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY cpl
    ADD CONSTRAINT cpl_account_idx UNIQUE (username, domain);


--
-- Name: cpl_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY cpl
    ADD CONSTRAINT cpl_pkey PRIMARY KEY (id);


--
-- Name: dbaliases_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY dbaliases
    ADD CONSTRAINT dbaliases_pkey PRIMARY KEY (id);


--
-- Name: dialog_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY dialog
    ADD CONSTRAINT dialog_pkey PRIMARY KEY (id);


--
-- Name: dialog_vars_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY dialog_vars
    ADD CONSTRAINT dialog_vars_pkey PRIMARY KEY (id);


--
-- Name: dialplan_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY dialplan
    ADD CONSTRAINT dialplan_pkey PRIMARY KEY (id);


--
-- Name: dispatcher_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY dispatcher
    ADD CONSTRAINT dispatcher_pkey PRIMARY KEY (id);


--
-- Name: django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type_app_label_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_app_label_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: domain_attrs_domain_attrs_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY domain_attrs
    ADD CONSTRAINT domain_attrs_domain_attrs_idx UNIQUE (did, name, value);


--
-- Name: domain_attrs_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY domain_attrs
    ADD CONSTRAINT domain_attrs_pkey PRIMARY KEY (id);


--
-- Name: domain_domain_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY domain
    ADD CONSTRAINT domain_domain_idx UNIQUE (domain);


--
-- Name: domain_name_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY domain_name
    ADD CONSTRAINT domain_name_pkey PRIMARY KEY (id);


--
-- Name: domain_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY domain
    ADD CONSTRAINT domain_pkey PRIMARY KEY (id);


--
-- Name: domainpolicy_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY domainpolicy
    ADD CONSTRAINT domainpolicy_pkey PRIMARY KEY (id);


--
-- Name: domainpolicy_rav_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY domainpolicy
    ADD CONSTRAINT domainpolicy_rav_idx UNIQUE (rule, att, val);


--
-- Name: dr_gateways_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY dr_gateways
    ADD CONSTRAINT dr_gateways_pkey PRIMARY KEY (gwid);


--
-- Name: dr_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY dr_groups
    ADD CONSTRAINT dr_groups_pkey PRIMARY KEY (id);


--
-- Name: dr_gw_lists_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY dr_gw_lists
    ADD CONSTRAINT dr_gw_lists_pkey PRIMARY KEY (id);


--
-- Name: dr_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY dr_rules
    ADD CONSTRAINT dr_rules_pkey PRIMARY KEY (ruleid);


--
-- Name: globalblacklist_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY globalblacklist
    ADD CONSTRAINT globalblacklist_pkey PRIMARY KEY (id);


--
-- Name: grp_account_group_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY grp
    ADD CONSTRAINT grp_account_group_idx UNIQUE (username, domain, grp);


--
-- Name: grp_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY grp
    ADD CONSTRAINT grp_pkey PRIMARY KEY (id);


--
-- Name: htable_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY htable
    ADD CONSTRAINT htable_pkey PRIMARY KEY (id);


--
-- Name: imc_members_account_room_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY imc_members
    ADD CONSTRAINT imc_members_account_room_idx UNIQUE (username, domain, room);


--
-- Name: imc_members_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY imc_members
    ADD CONSTRAINT imc_members_pkey PRIMARY KEY (id);


--
-- Name: imc_rooms_name_domain_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY imc_rooms
    ADD CONSTRAINT imc_rooms_name_domain_idx UNIQUE (name, domain);


--
-- Name: imc_rooms_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY imc_rooms
    ADD CONSTRAINT imc_rooms_pkey PRIMARY KEY (id);


--
-- Name: lcr_gw_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY lcr_gw
    ADD CONSTRAINT lcr_gw_pkey PRIMARY KEY (id);


--
-- Name: lcr_rule_lcr_id_prefix_from_uri_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY lcr_rule
    ADD CONSTRAINT lcr_rule_lcr_id_prefix_from_uri_idx UNIQUE (lcr_id, prefix, from_uri);


--
-- Name: lcr_rule_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY lcr_rule
    ADD CONSTRAINT lcr_rule_pkey PRIMARY KEY (id);


--
-- Name: lcr_rule_target_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY lcr_rule_target
    ADD CONSTRAINT lcr_rule_target_pkey PRIMARY KEY (id);


--
-- Name: lcr_rule_target_rule_id_gw_id_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY lcr_rule_target
    ADD CONSTRAINT lcr_rule_target_rule_id_gw_id_idx UNIQUE (rule_id, gw_id);


--
-- Name: location_attrs_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY location_attrs
    ADD CONSTRAINT location_attrs_pkey PRIMARY KEY (id);


--
-- Name: location_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY location
    ADD CONSTRAINT location_pkey PRIMARY KEY (id);


--
-- Name: location_ruid_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY location
    ADD CONSTRAINT location_ruid_idx UNIQUE (ruid);


--
-- Name: mensaje_enviado_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY mensaje_enviado
    ADD CONSTRAINT mensaje_enviado_pkey PRIMARY KEY (id);


--
-- Name: mensaje_recibido_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY mensaje_recibido
    ADD CONSTRAINT mensaje_recibido_pkey PRIMARY KEY (id);


--
-- Name: missed_calls_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY missed_calls
    ADD CONSTRAINT missed_calls_pkey PRIMARY KEY (id);


--
-- Name: mohqcalls_mohqcalls_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY mohqcalls
    ADD CONSTRAINT mohqcalls_mohqcalls_idx UNIQUE (call_id);


--
-- Name: mohqcalls_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY mohqcalls
    ADD CONSTRAINT mohqcalls_pkey PRIMARY KEY (id);


--
-- Name: mohqueues_mohqueue_name_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY mohqueues
    ADD CONSTRAINT mohqueues_mohqueue_name_idx UNIQUE (name);


--
-- Name: mohqueues_mohqueue_uri_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY mohqueues
    ADD CONSTRAINT mohqueues_mohqueue_uri_idx UNIQUE (uri);


--
-- Name: mohqueues_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY mohqueues
    ADD CONSTRAINT mohqueues_pkey PRIMARY KEY (id);


--
-- Name: mtree_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY mtree
    ADD CONSTRAINT mtree_pkey PRIMARY KEY (id);


--
-- Name: mtree_tprefix_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY mtree
    ADD CONSTRAINT mtree_tprefix_idx UNIQUE (tprefix);


--
-- Name: mtrees_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY mtrees
    ADD CONSTRAINT mtrees_pkey PRIMARY KEY (id);


--
-- Name: mtrees_tname_tprefix_tvalue_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY mtrees
    ADD CONSTRAINT mtrees_tname_tprefix_tvalue_idx UNIQUE (tname, tprefix, tvalue);


--
-- Name: ominicontacto_app_agenda_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_agenda
    ADD CONSTRAINT ominicontacto_app_agenda_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_agenteprofile__agenteprofile_id_acebf09b_uniq; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_agenteprofile_modulos
    ADD CONSTRAINT ominicontacto_app_agenteprofile__agenteprofile_id_acebf09b_uniq UNIQUE (agenteprofile_id, modulo_id);


--
-- Name: ominicontacto_app_agenteprofile_modulos_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_agenteprofile_modulos
    ADD CONSTRAINT ominicontacto_app_agenteprofile_modulos_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_agenteprofile_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_agenteprofile
    ADD CONSTRAINT ominicontacto_app_agenteprofile_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_agenteprofile_sip_extension_key; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_agenteprofile
    ADD CONSTRAINT ominicontacto_app_agenteprofile_sip_extension_key UNIQUE (sip_extension);


--
-- Name: ominicontacto_app_agenteprofile_user_id_key; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_agenteprofile
    ADD CONSTRAINT ominicontacto_app_agenteprofile_user_id_key UNIQUE (user_id);


--
-- Name: ominicontacto_app_basedatoscontacto_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_basedatoscontacto
    ADD CONSTRAINT ominicontacto_app_basedatoscontacto_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_califica_calificacioncampana_id_8a83ac71_uniq; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_calificacioncampana_calificacion
    ADD CONSTRAINT ominicontacto_app_califica_calificacioncampana_id_8a83ac71_uniq UNIQUE (calificacioncampana_id, calificacion_id);


--
-- Name: ominicontacto_app_calificacion_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_calificacion
    ADD CONSTRAINT ominicontacto_app_calificacion_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_calificacioncampana_calificacion_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_calificacioncampana_calificacion
    ADD CONSTRAINT ominicontacto_app_calificacioncampana_calificacion_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_calificacioncampana_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_calificacioncampana
    ADD CONSTRAINT ominicontacto_app_calificacioncampana_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_calificacioncliente_contacto_id_key; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_calificacioncliente
    ADD CONSTRAINT ominicontacto_app_calificacioncliente_contacto_id_key UNIQUE (contacto_id);


--
-- Name: ominicontacto_app_calificacioncliente_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_calificacioncliente
    ADD CONSTRAINT ominicontacto_app_calificacioncliente_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_campana_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_campana
    ADD CONSTRAINT ominicontacto_app_campana_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_chat_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_chat
    ADD CONSTRAINT ominicontacto_app_chat_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_contacto_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_contacto
    ADD CONSTRAINT ominicontacto_app_contacto_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_duraciondellamada_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_duraciondellamada
    ADD CONSTRAINT ominicontacto_app_duraciondellamada_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_fieldformulario_orden_6218007e_uniq; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_fieldformulario
    ADD CONSTRAINT ominicontacto_app_fieldformulario_orden_6218007e_uniq UNIQUE (orden, formulario_id);


--
-- Name: ominicontacto_app_fieldformulario_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_fieldformulario
    ADD CONSTRAINT ominicontacto_app_fieldformulario_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_formulario_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_formulario
    ADD CONSTRAINT ominicontacto_app_formulario_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_grabacion_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_grabacion
    ADD CONSTRAINT ominicontacto_app_grabacion_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_grupo_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_grupo
    ADD CONSTRAINT ominicontacto_app_grupo_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_mensajechat_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_mensajechat
    ADD CONSTRAINT ominicontacto_app_mensajechat_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_metadatacliente_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_metadatacliente
    ADD CONSTRAINT ominicontacto_app_metadatacliente_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_modulo_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_modulo
    ADD CONSTRAINT ominicontacto_app_modulo_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_pausa_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_pausa
    ADD CONSTRAINT ominicontacto_app_pausa_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_queuelog_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_queuelog
    ADD CONSTRAINT ominicontacto_app_queuelog_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_user_groups
    ADD CONSTRAINT ominicontacto_app_user_groups_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_user_groups_user_id_9ea58fa3_uniq; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_user_groups
    ADD CONSTRAINT ominicontacto_app_user_groups_user_id_9ea58fa3_uniq UNIQUE (user_id, group_id);


--
-- Name: ominicontacto_app_user_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_user
    ADD CONSTRAINT ominicontacto_app_user_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_user_user_permissions
    ADD CONSTRAINT ominicontacto_app_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: ominicontacto_app_user_user_permissions_user_id_c7a8cf96_uniq; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_user_user_permissions
    ADD CONSTRAINT ominicontacto_app_user_user_permissions_user_id_c7a8cf96_uniq UNIQUE (user_id, permission_id);


--
-- Name: ominicontacto_app_user_username_key; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_user
    ADD CONSTRAINT ominicontacto_app_user_username_key UNIQUE (username);


--
-- Name: ominicontacto_app_wombatlog_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY ominicontacto_app_wombatlog
    ADD CONSTRAINT ominicontacto_app_wombatlog_pkey PRIMARY KEY (id);


--
-- Name: pdt_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY pdt
    ADD CONSTRAINT pdt_pkey PRIMARY KEY (id);


--
-- Name: pdt_sdomain_prefix_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY pdt
    ADD CONSTRAINT pdt_sdomain_prefix_idx UNIQUE (sdomain, prefix);


--
-- Name: pl_pipes_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY pl_pipes
    ADD CONSTRAINT pl_pipes_pkey PRIMARY KEY (id);


--
-- Name: presentity_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY presentity
    ADD CONSTRAINT presentity_pkey PRIMARY KEY (id);


--
-- Name: presentity_presentity_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY presentity
    ADD CONSTRAINT presentity_presentity_idx UNIQUE (username, domain, event, etag);


--
-- Name: pua_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY pua
    ADD CONSTRAINT pua_pkey PRIMARY KEY (id);


--
-- Name: pua_pua_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY pua
    ADD CONSTRAINT pua_pua_idx UNIQUE (etag, tuple_id, call_id, from_tag);


--
-- Name: purplemap_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY purplemap
    ADD CONSTRAINT purplemap_pkey PRIMARY KEY (id);


--
-- Name: queue_member_table_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY queue_member_table
    ADD CONSTRAINT queue_member_table_pkey PRIMARY KEY (id);


--
-- Name: queue_member_table_queue_name_1e319083_uniq; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY queue_member_table
    ADD CONSTRAINT queue_member_table_queue_name_1e319083_uniq UNIQUE (queue_name, member_id);


--
-- Name: queue_table_campana_id_key; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY queue_table
    ADD CONSTRAINT queue_table_campana_id_key UNIQUE (campana_id);


--
-- Name: queue_table_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY queue_table
    ADD CONSTRAINT queue_table_pkey PRIMARY KEY (name);


--
-- Name: queue_table_queue_asterisk_key; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY queue_table
    ADD CONSTRAINT queue_table_queue_asterisk_key UNIQUE (queue_asterisk);


--
-- Name: re_grp_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY re_grp
    ADD CONSTRAINT re_grp_pkey PRIMARY KEY (id);


--
-- Name: rls_presentity_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY rls_presentity
    ADD CONSTRAINT rls_presentity_pkey PRIMARY KEY (id);


--
-- Name: rls_presentity_rls_presentity_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY rls_presentity
    ADD CONSTRAINT rls_presentity_rls_presentity_idx UNIQUE (rlsubs_did, resource_uri);


--
-- Name: rls_watchers_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY rls_watchers
    ADD CONSTRAINT rls_watchers_pkey PRIMARY KEY (id);


--
-- Name: rls_watchers_rls_watcher_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY rls_watchers
    ADD CONSTRAINT rls_watchers_rls_watcher_idx UNIQUE (callid, to_tag, from_tag);


--
-- Name: rtpproxy_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY rtpproxy
    ADD CONSTRAINT rtpproxy_pkey PRIMARY KEY (id);


--
-- Name: sca_subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY sca_subscriptions
    ADD CONSTRAINT sca_subscriptions_pkey PRIMARY KEY (id);


--
-- Name: sca_subscriptions_sca_subscriptions_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY sca_subscriptions
    ADD CONSTRAINT sca_subscriptions_sca_subscriptions_idx UNIQUE (subscriber, call_id, from_tag, to_tag);


--
-- Name: silo_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY silo
    ADD CONSTRAINT silo_pkey PRIMARY KEY (id);


--
-- Name: sip_trace_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY sip_trace
    ADD CONSTRAINT sip_trace_pkey PRIMARY KEY (id);


--
-- Name: speed_dial_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY speed_dial
    ADD CONSTRAINT speed_dial_pkey PRIMARY KEY (id);


--
-- Name: speed_dial_speed_dial_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY speed_dial
    ADD CONSTRAINT speed_dial_speed_dial_idx UNIQUE (username, domain, sd_domain, sd_username);


--
-- Name: subscriber_account_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY subscriber
    ADD CONSTRAINT subscriber_account_idx UNIQUE (username, domain);


--
-- Name: subscriber_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY subscriber
    ADD CONSTRAINT subscriber_pkey PRIMARY KEY (id);


--
-- Name: topos_d_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY topos_d
    ADD CONSTRAINT topos_d_pkey PRIMARY KEY (id);


--
-- Name: topos_t_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY topos_t
    ADD CONSTRAINT topos_t_pkey PRIMARY KEY (id);


--
-- Name: trusted_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY trusted
    ADD CONSTRAINT trusted_pkey PRIMARY KEY (id);


--
-- Name: uacreg_l_uuid_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY uacreg
    ADD CONSTRAINT uacreg_l_uuid_idx UNIQUE (l_uuid);


--
-- Name: uacreg_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY uacreg
    ADD CONSTRAINT uacreg_pkey PRIMARY KEY (id);


--
-- Name: uri_account_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY uri
    ADD CONSTRAINT uri_account_idx UNIQUE (username, domain, uri_user);


--
-- Name: uri_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY uri
    ADD CONSTRAINT uri_pkey PRIMARY KEY (id);


--
-- Name: userblacklist_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY userblacklist
    ADD CONSTRAINT userblacklist_pkey PRIMARY KEY (id);


--
-- Name: usr_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY usr_preferences
    ADD CONSTRAINT usr_preferences_pkey PRIMARY KEY (id);


--
-- Name: version_table_name_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY version
    ADD CONSTRAINT version_table_name_idx UNIQUE (table_name);


--
-- Name: watchers_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY watchers
    ADD CONSTRAINT watchers_pkey PRIMARY KEY (id);


--
-- Name: watchers_watcher_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY watchers
    ADD CONSTRAINT watchers_watcher_idx UNIQUE (presentity_uri, watcher_username, watcher_domain, event);


--
-- Name: xcap_doc_uri_idx; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY xcap
    ADD CONSTRAINT xcap_doc_uri_idx UNIQUE (doc_uri);


--
-- Name: xcap_pkey; Type: CONSTRAINT; Schema: public; Owner: kamailio; Tablespace: 
--

ALTER TABLE ONLY xcap
    ADD CONSTRAINT xcap_pkey PRIMARY KEY (id);


--
-- Name: acc_callid_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX acc_callid_idx ON acc USING btree (callid);


--
-- Name: acc_cdrs_start_time_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX acc_cdrs_start_time_idx ON acc_cdrs USING btree (start_time);


--
-- Name: active_watchers_active_watchers_expires; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX active_watchers_active_watchers_expires ON active_watchers USING btree (expires);


--
-- Name: active_watchers_active_watchers_pres; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX active_watchers_active_watchers_pres ON active_watchers USING btree (presentity_uri, event);


--
-- Name: active_watchers_updated_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX active_watchers_updated_idx ON active_watchers USING btree (updated);


--
-- Name: active_watchers_updated_winfo_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX active_watchers_updated_winfo_idx ON active_watchers USING btree (updated_winfo, presentity_uri);


--
-- Name: aliases_account_contact_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX aliases_account_contact_idx ON aliases USING btree (username, domain, contact);


--
-- Name: aliases_expires_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX aliases_expires_idx ON aliases USING btree (expires);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX auth_group_name_a6ea08ec_like ON auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_0e939a4f; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX auth_group_permissions_0e939a4f ON auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_8373b171; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX auth_group_permissions_8373b171 ON auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_417f1b1c; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX auth_permission_417f1b1c ON auth_permission USING btree (content_type_id);


--
-- Name: dbaliases_alias_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX dbaliases_alias_idx ON dbaliases USING btree (alias_username, alias_domain);


--
-- Name: dbaliases_alias_user_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX dbaliases_alias_user_idx ON dbaliases USING btree (alias_username);


--
-- Name: dbaliases_target_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX dbaliases_target_idx ON dbaliases USING btree (username, domain);


--
-- Name: dialog_hash_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX dialog_hash_idx ON dialog USING btree (hash_entry, hash_id);


--
-- Name: dialog_vars_hash_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX dialog_vars_hash_idx ON dialog_vars USING btree (hash_entry, hash_id);


--
-- Name: django_admin_log_417f1b1c; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX django_admin_log_417f1b1c ON django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_e8701ad4; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX django_admin_log_e8701ad4 ON django_admin_log USING btree (user_id);


--
-- Name: domainpolicy_rule_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX domainpolicy_rule_idx ON domainpolicy USING btree (rule);


--
-- Name: globalblacklist_globalblacklist_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX globalblacklist_globalblacklist_idx ON globalblacklist USING btree (prefix);


--
-- Name: lcr_gw_lcr_id_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX lcr_gw_lcr_id_idx ON lcr_gw USING btree (lcr_id);


--
-- Name: lcr_rule_target_lcr_id_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX lcr_rule_target_lcr_id_idx ON lcr_rule_target USING btree (lcr_id);


--
-- Name: location_account_contact_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX location_account_contact_idx ON location USING btree (username, domain, contact);


--
-- Name: location_attrs_account_record_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX location_attrs_account_record_idx ON location_attrs USING btree (username, domain, ruid);


--
-- Name: location_attrs_last_modified_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX location_attrs_last_modified_idx ON location_attrs USING btree (last_modified);


--
-- Name: location_connection_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX location_connection_idx ON location USING btree (server_id, connection_id);


--
-- Name: location_expires_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX location_expires_idx ON location USING btree (expires);


--
-- Name: mensaje_enviado_32400660; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX mensaje_enviado_32400660 ON mensaje_enviado USING btree (agente_id);


--
-- Name: missed_calls_callid_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX missed_calls_callid_idx ON missed_calls USING btree (callid);


--
-- Name: ominicontacto_app_agenda_32400660; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_agenda_32400660 ON ominicontacto_app_agenda USING btree (agente_id);


--
-- Name: ominicontacto_app_agenteprofile_acaeb2d6; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_agenteprofile_acaeb2d6 ON ominicontacto_app_agenteprofile USING btree (grupo_id);


--
-- Name: ominicontacto_app_agenteprofile_modulos_7ba91c57; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_agenteprofile_modulos_7ba91c57 ON ominicontacto_app_agenteprofile_modulos USING btree (modulo_id);


--
-- Name: ominicontacto_app_agenteprofile_modulos_bfd9a2cb; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_agenteprofile_modulos_bfd9a2cb ON ominicontacto_app_agenteprofile_modulos USING btree (agenteprofile_id);


--
-- Name: ominicontacto_app_calificacioncampana_calificacion_36aa9691; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_calificacioncampana_calificacion_36aa9691 ON ominicontacto_app_calificacioncampana_calificacion USING btree (calificacion_id);


--
-- Name: ominicontacto_app_calificacioncampana_calificacion_7f1db41a; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_calificacioncampana_calificacion_7f1db41a ON ominicontacto_app_calificacioncampana_calificacion USING btree (calificacioncampana_id);


--
-- Name: ominicontacto_app_calificacioncliente_32400660; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_calificacioncliente_32400660 ON ominicontacto_app_calificacioncliente USING btree (agente_id);


--
-- Name: ominicontacto_app_calificacioncliente_36aa9691; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_calificacioncliente_36aa9691 ON ominicontacto_app_calificacioncliente USING btree (calificacion_id);


--
-- Name: ominicontacto_app_calificacioncliente_66683d76; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_calificacioncliente_66683d76 ON ominicontacto_app_calificacioncliente USING btree (campana_id);


--
-- Name: ominicontacto_app_campana_368d6ace; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_campana_368d6ace ON ominicontacto_app_campana USING btree (bd_contacto_id);


--
-- Name: ominicontacto_app_campana_3fe51010; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_campana_3fe51010 ON ominicontacto_app_campana USING btree (formulario_id);


--
-- Name: ominicontacto_app_campana_60530197; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_campana_60530197 ON ominicontacto_app_campana USING btree (calificacion_campana_id);


--
-- Name: ominicontacto_app_chat_32400660; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_chat_32400660 ON ominicontacto_app_chat USING btree (agente_id);


--
-- Name: ominicontacto_app_chat_e8701ad4; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_chat_e8701ad4 ON ominicontacto_app_chat USING btree (user_id);


--
-- Name: ominicontacto_app_contacto_368d6ace; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_contacto_368d6ace ON ominicontacto_app_contacto USING btree (bd_contacto_id);


--
-- Name: ominicontacto_app_duraciondellamada_32400660; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_duraciondellamada_32400660 ON ominicontacto_app_duraciondellamada USING btree (agente_id);


--
-- Name: ominicontacto_app_fieldformulario_3fe51010; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_fieldformulario_3fe51010 ON ominicontacto_app_fieldformulario USING btree (formulario_id);


--
-- Name: ominicontacto_app_grabacion_campana_id_fdebc53b_uniq; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_grabacion_campana_id_fdebc53b_uniq ON ominicontacto_app_grabacion USING btree (campana_id);


--
-- Name: ominicontacto_app_mensajechat_924b1846; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_mensajechat_924b1846 ON ominicontacto_app_mensajechat USING btree (sender_id);


--
-- Name: ominicontacto_app_mensajechat_b79bfa8f; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_mensajechat_b79bfa8f ON ominicontacto_app_mensajechat USING btree (chat_id);


--
-- Name: ominicontacto_app_mensajechat_f4b39993; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_mensajechat_f4b39993 ON ominicontacto_app_mensajechat USING btree (to_id);


--
-- Name: ominicontacto_app_metadatacliente_32400660; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_metadatacliente_32400660 ON ominicontacto_app_metadatacliente USING btree (agente_id);


--
-- Name: ominicontacto_app_metadatacliente_66683d76; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_metadatacliente_66683d76 ON ominicontacto_app_metadatacliente USING btree (campana_id);


--
-- Name: ominicontacto_app_user_groups_0e939a4f; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_user_groups_0e939a4f ON ominicontacto_app_user_groups USING btree (group_id);


--
-- Name: ominicontacto_app_user_groups_e8701ad4; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_user_groups_e8701ad4 ON ominicontacto_app_user_groups USING btree (user_id);


--
-- Name: ominicontacto_app_user_user_permissions_8373b171; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_user_user_permissions_8373b171 ON ominicontacto_app_user_user_permissions USING btree (permission_id);


--
-- Name: ominicontacto_app_user_user_permissions_e8701ad4; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_user_user_permissions_e8701ad4 ON ominicontacto_app_user_user_permissions USING btree (user_id);


--
-- Name: ominicontacto_app_user_username_3223b7ba_like; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_user_username_3223b7ba_like ON ominicontacto_app_user USING btree (username varchar_pattern_ops);


--
-- Name: ominicontacto_app_wombatlog_32400660; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_wombatlog_32400660 ON ominicontacto_app_wombatlog USING btree (agente_id);


--
-- Name: ominicontacto_app_wombatlog_66683d76; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_wombatlog_66683d76 ON ominicontacto_app_wombatlog USING btree (campana_id);


--
-- Name: ominicontacto_app_wombatlog_debcd608; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX ominicontacto_app_wombatlog_debcd608 ON ominicontacto_app_wombatlog USING btree (contacto_id);


--
-- Name: presentity_account_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX presentity_account_idx ON presentity USING btree (username, domain, event);


--
-- Name: presentity_presentity_expires; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX presentity_presentity_expires ON presentity USING btree (expires);


--
-- Name: pua_dialog1_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX pua_dialog1_idx ON pua USING btree (pres_id, pres_uri);


--
-- Name: pua_dialog2_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX pua_dialog2_idx ON pua USING btree (call_id, from_tag);


--
-- Name: pua_expires_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX pua_expires_idx ON pua USING btree (expires);


--
-- Name: pua_record_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX pua_record_idx ON pua USING btree (pres_id);


--
-- Name: queue_member_table_75249aa1; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX queue_member_table_75249aa1 ON queue_member_table USING btree (queue_name);


--
-- Name: queue_member_table_b5c3e75b; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX queue_member_table_b5c3e75b ON queue_member_table USING btree (member_id);


--
-- Name: queue_member_table_queue_id_996b3794_like; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX queue_member_table_queue_id_996b3794_like ON queue_member_table USING btree (queue_name varchar_pattern_ops);


--
-- Name: queue_table_name_495baf91_like; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX queue_table_name_495baf91_like ON queue_table USING btree (name varchar_pattern_ops);


--
-- Name: re_grp_group_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX re_grp_group_idx ON re_grp USING btree (group_id);


--
-- Name: rls_presentity_expires_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX rls_presentity_expires_idx ON rls_presentity USING btree (expires);


--
-- Name: rls_presentity_rlsubs_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX rls_presentity_rlsubs_idx ON rls_presentity USING btree (rlsubs_did);


--
-- Name: rls_presentity_updated_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX rls_presentity_updated_idx ON rls_presentity USING btree (updated);


--
-- Name: rls_watchers_rls_watchers_expires; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX rls_watchers_rls_watchers_expires ON rls_watchers USING btree (expires);


--
-- Name: rls_watchers_rls_watchers_update; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX rls_watchers_rls_watchers_update ON rls_watchers USING btree (watcher_username, watcher_domain, event);


--
-- Name: rls_watchers_updated_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX rls_watchers_updated_idx ON rls_watchers USING btree (updated);


--
-- Name: sca_subscriptions_sca_expires_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX sca_subscriptions_sca_expires_idx ON sca_subscriptions USING btree (expires);


--
-- Name: sca_subscriptions_sca_subscribers_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX sca_subscriptions_sca_subscribers_idx ON sca_subscriptions USING btree (subscriber, event);


--
-- Name: silo_account_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX silo_account_idx ON silo USING btree (username, domain);


--
-- Name: sip_trace_callid_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX sip_trace_callid_idx ON sip_trace USING btree (callid);


--
-- Name: sip_trace_date_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX sip_trace_date_idx ON sip_trace USING btree (time_stamp);


--
-- Name: sip_trace_fromip_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX sip_trace_fromip_idx ON sip_trace USING btree (fromip);


--
-- Name: sip_trace_traced_user_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX sip_trace_traced_user_idx ON sip_trace USING btree (traced_user);


--
-- Name: subscriber_username_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX subscriber_username_idx ON subscriber USING btree (username);


--
-- Name: topos_d_a_callid_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX topos_d_a_callid_idx ON topos_d USING btree (a_callid);


--
-- Name: topos_d_rectime_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX topos_d_rectime_idx ON topos_d USING btree (rectime);


--
-- Name: topos_t_a_callid_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX topos_t_a_callid_idx ON topos_t USING btree (a_callid);


--
-- Name: topos_t_rectime_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX topos_t_rectime_idx ON topos_t USING btree (rectime);


--
-- Name: trusted_peer_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX trusted_peer_idx ON trusted USING btree (src_ip);


--
-- Name: userblacklist_userblacklist_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX userblacklist_userblacklist_idx ON userblacklist USING btree (username, domain, prefix);


--
-- Name: usr_preferences_ua_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX usr_preferences_ua_idx ON usr_preferences USING btree (uuid, attribute);


--
-- Name: usr_preferences_uda_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX usr_preferences_uda_idx ON usr_preferences USING btree (username, domain, attribute);


--
-- Name: xcap_account_doc_type_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX xcap_account_doc_type_idx ON xcap USING btree (username, domain, doc_type);


--
-- Name: xcap_account_doc_type_uri_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX xcap_account_doc_type_uri_idx ON xcap USING btree (username, domain, doc_type, doc_uri);


--
-- Name: xcap_account_doc_uri_idx; Type: INDEX; Schema: public; Owner: kamailio; Tablespace: 
--

CREATE INDEX xcap_account_doc_uri_idx ON xcap USING btree (username, domain, doc_uri);


--
-- Name: D6d2e47c11d2fb8d7243f5dbb136c9e3; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_contacto
    ADD CONSTRAINT "D6d2e47c11d2fb8d7243f5dbb136c9e3" FOREIGN KEY (bd_contacto_id) REFERENCES ominicontacto_app_basedatoscontacto(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: D790090bf77bd6ae57bbcd278f80b4bf; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_campana
    ADD CONSTRAINT "D790090bf77bd6ae57bbcd278f80b4bf" FOREIGN KEY (bd_contacto_id) REFERENCES ominicontacto_app_basedatoscontacto(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: D8da2b3b45492920f6ec709e3b513e07; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_agenteprofile_modulos
    ADD CONSTRAINT "D8da2b3b45492920f6ec709e3b513e07" FOREIGN KEY (agenteprofile_id) REFERENCES ominicontacto_app_agenteprofile(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permiss_permission_id_84c5c92e_fk_auth_permission_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permiss_permission_id_84c5c92e_fk_auth_permission_id FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permiss_content_type_id_2f476e4b_fk_django_content_type_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permiss_content_type_id_2f476e4b_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ca685487dc3a9bf18d5e9e0fd006bf67; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_campana
    ADD CONSTRAINT ca685487dc3a9bf18d5e9e0fd006bf67 FOREIGN KEY (calificacion_campana_id) REFERENCES ominicontacto_app_calificacioncampana(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_content_type_id_c4bce8eb_fk_django_content_type_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_content_type_id_c4bce8eb_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log_user_id_c564eba6_fk_ominicontacto_app_user_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_ominicontacto_app_user_id FOREIGN KEY (user_id) REFERENCES ominicontacto_app_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: e81ed6bab1cb48461414d88108216e55; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_calificacioncampana_calificacion
    ADD CONSTRAINT e81ed6bab1cb48461414d88108216e55 FOREIGN KEY (calificacioncampana_id) REFERENCES ominicontacto_app_calificacioncampana(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: mensaj_agente_id_de9cfeb5_fk_ominicontacto_app_agenteprofile_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY mensaje_enviado
    ADD CONSTRAINT mensaj_agente_id_de9cfeb5_fk_ominicontacto_app_agenteprofile_id FOREIGN KEY (agente_id) REFERENCES ominicontacto_app_agenteprofile(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: o_calificacion_id_73b5d2c5_fk_ominicontacto_app_calificacion_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_calificacioncliente
    ADD CONSTRAINT o_calificacion_id_73b5d2c5_fk_ominicontacto_app_calificacion_id FOREIGN KEY (calificacion_id) REFERENCES ominicontacto_app_calificacion(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: o_calificacion_id_e56288ab_fk_ominicontacto_app_calificacion_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_calificacioncampana_calificacion
    ADD CONSTRAINT o_calificacion_id_e56288ab_fk_ominicontacto_app_calificacion_id FOREIGN KEY (calificacion_id) REFERENCES ominicontacto_app_calificacion(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: omini_formulario_id_0184bc8d_fk_ominicontacto_app_formulario_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_campana
    ADD CONSTRAINT omini_formulario_id_0184bc8d_fk_ominicontacto_app_formulario_id FOREIGN KEY (formulario_id) REFERENCES ominicontacto_app_formulario(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: omini_formulario_id_b5355e5d_fk_ominicontacto_app_formulario_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_fieldformulario
    ADD CONSTRAINT omini_formulario_id_b5355e5d_fk_ominicontacto_app_formulario_id FOREIGN KEY (formulario_id) REFERENCES ominicontacto_app_formulario(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominic_agente_id_1070b434_fk_ominicontacto_app_agenteprofile_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_calificacioncliente
    ADD CONSTRAINT ominic_agente_id_1070b434_fk_ominicontacto_app_agenteprofile_id FOREIGN KEY (agente_id) REFERENCES ominicontacto_app_agenteprofile(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominic_agente_id_15e63fce_fk_ominicontacto_app_agenteprofile_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_wombatlog
    ADD CONSTRAINT ominic_agente_id_15e63fce_fk_ominicontacto_app_agenteprofile_id FOREIGN KEY (agente_id) REFERENCES ominicontacto_app_agenteprofile(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominic_agente_id_32c1d2d4_fk_ominicontacto_app_agenteprofile_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_metadatacliente
    ADD CONSTRAINT ominic_agente_id_32c1d2d4_fk_ominicontacto_app_agenteprofile_id FOREIGN KEY (agente_id) REFERENCES ominicontacto_app_agenteprofile(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominic_agente_id_341aa330_fk_ominicontacto_app_agenteprofile_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_duraciondellamada
    ADD CONSTRAINT ominic_agente_id_341aa330_fk_ominicontacto_app_agenteprofile_id FOREIGN KEY (agente_id) REFERENCES ominicontacto_app_agenteprofile(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominic_agente_id_6baadc27_fk_ominicontacto_app_agenteprofile_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_agenda
    ADD CONSTRAINT ominic_agente_id_6baadc27_fk_ominicontacto_app_agenteprofile_id FOREIGN KEY (agente_id) REFERENCES ominicontacto_app_agenteprofile(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominic_agente_id_b0b74e82_fk_ominicontacto_app_agenteprofile_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_chat
    ADD CONSTRAINT ominic_agente_id_b0b74e82_fk_ominicontacto_app_agenteprofile_id FOREIGN KEY (agente_id) REFERENCES ominicontacto_app_agenteprofile(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominicont_contacto_id_7b0281c2_fk_ominicontacto_app_contacto_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_wombatlog
    ADD CONSTRAINT ominicont_contacto_id_7b0281c2_fk_ominicontacto_app_contacto_id FOREIGN KEY (contacto_id) REFERENCES ominicontacto_app_contacto(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominicont_contacto_id_8edc7340_fk_ominicontacto_app_contacto_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_metadatacliente
    ADD CONSTRAINT ominicont_contacto_id_8edc7340_fk_ominicontacto_app_contacto_id FOREIGN KEY (contacto_id) REFERENCES ominicontacto_app_contacto(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominicont_contacto_id_e5df4663_fk_ominicontacto_app_contacto_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_calificacioncliente
    ADD CONSTRAINT ominicont_contacto_id_e5df4663_fk_ominicontacto_app_contacto_id FOREIGN KEY (contacto_id) REFERENCES ominicontacto_app_contacto(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominicontac_campana_id_0392f548_fk_ominicontacto_app_campana_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_calificacioncliente
    ADD CONSTRAINT ominicontac_campana_id_0392f548_fk_ominicontacto_app_campana_id FOREIGN KEY (campana_id) REFERENCES ominicontacto_app_campana(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominicontac_campana_id_a6c9c717_fk_ominicontacto_app_campana_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_wombatlog
    ADD CONSTRAINT ominicontac_campana_id_a6c9c717_fk_ominicontacto_app_campana_id FOREIGN KEY (campana_id) REFERENCES ominicontacto_app_campana(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominicontac_campana_id_cbd5c9f1_fk_ominicontacto_app_campana_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_metadatacliente
    ADD CONSTRAINT ominicontac_campana_id_cbd5c9f1_fk_ominicontacto_app_campana_id FOREIGN KEY (campana_id) REFERENCES ominicontacto_app_campana(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominicontac_campana_id_fdebc53b_fk_ominicontacto_app_campana_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_grabacion
    ADD CONSTRAINT ominicontac_campana_id_fdebc53b_fk_ominicontacto_app_campana_id FOREIGN KEY (campana_id) REFERENCES ominicontacto_app_campana(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominicontacto_a_grupo_id_474dfc5a_fk_ominicontacto_app_grupo_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_agenteprofile
    ADD CONSTRAINT ominicontacto_a_grupo_id_474dfc5a_fk_ominicontacto_app_grupo_id FOREIGN KEY (grupo_id) REFERENCES ominicontacto_app_grupo(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominicontacto_a_sender_id_49a6c90d_fk_ominicontacto_app_user_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_mensajechat
    ADD CONSTRAINT ominicontacto_a_sender_id_49a6c90d_fk_ominicontacto_app_user_id FOREIGN KEY (sender_id) REFERENCES ominicontacto_app_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominicontacto_app__permission_id_43f9ab68_fk_auth_permission_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_user_user_permissions
    ADD CONSTRAINT ominicontacto_app__permission_id_43f9ab68_fk_auth_permission_id FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominicontacto_app_chat_id_3845da5b_fk_ominicontacto_app_chat_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_mensajechat
    ADD CONSTRAINT ominicontacto_app_chat_id_3845da5b_fk_ominicontacto_app_chat_id FOREIGN KEY (chat_id) REFERENCES ominicontacto_app_chat(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominicontacto_app_m_to_id_a5f7aa2c_fk_ominicontacto_app_user_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_mensajechat
    ADD CONSTRAINT ominicontacto_app_m_to_id_a5f7aa2c_fk_ominicontacto_app_user_id FOREIGN KEY (to_id) REFERENCES ominicontacto_app_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominicontacto_app_user_group_group_id_f47e61a0_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_user_groups
    ADD CONSTRAINT ominicontacto_app_user_group_group_id_f47e61a0_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominicontacto_app_user_id_0e446b03_fk_ominicontacto_app_user_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_agenteprofile
    ADD CONSTRAINT ominicontacto_app_user_id_0e446b03_fk_ominicontacto_app_user_id FOREIGN KEY (user_id) REFERENCES ominicontacto_app_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominicontacto_app_user_id_4412e21b_fk_ominicontacto_app_user_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_user_user_permissions
    ADD CONSTRAINT ominicontacto_app_user_id_4412e21b_fk_ominicontacto_app_user_id FOREIGN KEY (user_id) REFERENCES ominicontacto_app_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominicontacto_app_user_id_7e593d05_fk_ominicontacto_app_user_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_chat
    ADD CONSTRAINT ominicontacto_app_user_id_7e593d05_fk_ominicontacto_app_user_id FOREIGN KEY (user_id) REFERENCES ominicontacto_app_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominicontacto_app_user_id_9520c89f_fk_ominicontacto_app_user_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_user_groups
    ADD CONSTRAINT ominicontacto_app_user_id_9520c89f_fk_ominicontacto_app_user_id FOREIGN KEY (user_id) REFERENCES ominicontacto_app_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ominicontacto_modulo_id_adce0149_fk_ominicontacto_app_modulo_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY ominicontacto_app_agenteprofile_modulos
    ADD CONSTRAINT ominicontacto_modulo_id_adce0149_fk_ominicontacto_app_modulo_id FOREIGN KEY (modulo_id) REFERENCES ominicontacto_app_modulo(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: queue__member_id_0e6c0aa5_fk_ominicontacto_app_agenteprofile_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY queue_member_table
    ADD CONSTRAINT queue__member_id_0e6c0aa5_fk_ominicontacto_app_agenteprofile_id FOREIGN KEY (member_id) REFERENCES ominicontacto_app_agenteprofile(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: queue_member_table_queue_name_cc6b888a_fk_queue_table_name; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY queue_member_table
    ADD CONSTRAINT queue_member_table_queue_name_cc6b888a_fk_queue_table_name FOREIGN KEY (queue_name) REFERENCES queue_table(name) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: queue_table_campana_id_be72b1c4_fk_ominicontacto_app_campana_id; Type: FK CONSTRAINT; Schema: public; Owner: kamailio
--

ALTER TABLE ONLY queue_table
    ADD CONSTRAINT queue_table_campana_id_be72b1c4_fk_ominicontacto_app_campana_id FOREIGN KEY (campana_id) REFERENCES ominicontacto_app_campana(id) DEFERRABLE INITIALLY DEFERRED;


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
-- Name: acc_cdrs; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE acc_cdrs FROM PUBLIC;
REVOKE ALL ON TABLE acc_cdrs FROM kamailio;
GRANT ALL ON TABLE acc_cdrs TO kamailio;
GRANT SELECT ON TABLE acc_cdrs TO kamailioro;


--
-- Name: acc_cdrs_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE acc_cdrs_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE acc_cdrs_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE acc_cdrs_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE acc_cdrs_id_seq TO kamailioro;


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
-- Name: address; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE address FROM PUBLIC;
REVOKE ALL ON TABLE address FROM kamailio;
GRANT ALL ON TABLE address TO kamailio;
GRANT SELECT ON TABLE address TO kamailioro;


--
-- Name: address_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE address_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE address_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE address_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE address_id_seq TO kamailioro;


--
-- Name: aliases; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE aliases FROM PUBLIC;
REVOKE ALL ON TABLE aliases FROM kamailio;
GRANT ALL ON TABLE aliases TO kamailio;
GRANT SELECT ON TABLE aliases TO kamailioro;


--
-- Name: aliases_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE aliases_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE aliases_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE aliases_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE aliases_id_seq TO kamailioro;


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
-- Name: dialog; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE dialog FROM PUBLIC;
REVOKE ALL ON TABLE dialog FROM kamailio;
GRANT ALL ON TABLE dialog TO kamailio;
GRANT SELECT ON TABLE dialog TO kamailioro;


--
-- Name: dialog_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE dialog_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE dialog_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE dialog_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE dialog_id_seq TO kamailioro;


--
-- Name: dialog_vars; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE dialog_vars FROM PUBLIC;
REVOKE ALL ON TABLE dialog_vars FROM kamailio;
GRANT ALL ON TABLE dialog_vars TO kamailio;
GRANT SELECT ON TABLE dialog_vars TO kamailioro;


--
-- Name: dialog_vars_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE dialog_vars_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE dialog_vars_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE dialog_vars_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE dialog_vars_id_seq TO kamailioro;


--
-- Name: dialplan; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE dialplan FROM PUBLIC;
REVOKE ALL ON TABLE dialplan FROM kamailio;
GRANT ALL ON TABLE dialplan TO kamailio;
GRANT SELECT ON TABLE dialplan TO kamailioro;


--
-- Name: dialplan_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE dialplan_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE dialplan_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE dialplan_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE dialplan_id_seq TO kamailioro;


--
-- Name: dispatcher; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE dispatcher FROM PUBLIC;
REVOKE ALL ON TABLE dispatcher FROM kamailio;
GRANT ALL ON TABLE dispatcher TO kamailio;
GRANT SELECT ON TABLE dispatcher TO kamailioro;


--
-- Name: dispatcher_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE dispatcher_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE dispatcher_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE dispatcher_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE dispatcher_id_seq TO kamailioro;


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
-- Name: dr_gateways; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE dr_gateways FROM PUBLIC;
REVOKE ALL ON TABLE dr_gateways FROM kamailio;
GRANT ALL ON TABLE dr_gateways TO kamailio;
GRANT SELECT ON TABLE dr_gateways TO kamailioro;


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
GRANT SELECT ON SEQUENCE lcr_rule_id_seq TO kamailioro;


--
-- Name: lcr_rule_target; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE lcr_rule_target FROM PUBLIC;
REVOKE ALL ON TABLE lcr_rule_target FROM kamailio;
GRANT ALL ON TABLE lcr_rule_target TO kamailio;
GRANT SELECT ON TABLE lcr_rule_target TO kamailioro;


--
-- Name: lcr_rule_target_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE lcr_rule_target_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE lcr_rule_target_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE lcr_rule_target_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE lcr_rule_target_id_seq TO kamailioro;


--
-- Name: location; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE location FROM PUBLIC;
REVOKE ALL ON TABLE location FROM kamailio;
GRANT ALL ON TABLE location TO kamailio;
GRANT SELECT ON TABLE location TO kamailioro;


--
-- Name: location_attrs; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE location_attrs FROM PUBLIC;
REVOKE ALL ON TABLE location_attrs FROM kamailio;
GRANT ALL ON TABLE location_attrs TO kamailio;
GRANT SELECT ON TABLE location_attrs TO kamailioro;


--
-- Name: location_attrs_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE location_attrs_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE location_attrs_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE location_attrs_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE location_attrs_id_seq TO kamailioro;


--
-- Name: location_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE location_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE location_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE location_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE location_id_seq TO kamailioro;


--
-- Name: missed_calls; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE missed_calls FROM PUBLIC;
REVOKE ALL ON TABLE missed_calls FROM kamailio;
GRANT ALL ON TABLE missed_calls TO kamailio;
GRANT SELECT ON TABLE missed_calls TO kamailioro;


--
-- Name: missed_calls_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE missed_calls_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE missed_calls_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE missed_calls_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE missed_calls_id_seq TO kamailioro;


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
-- Name: pdt; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE pdt FROM PUBLIC;
REVOKE ALL ON TABLE pdt FROM kamailio;
GRANT ALL ON TABLE pdt TO kamailio;
GRANT SELECT ON TABLE pdt TO kamailioro;


--
-- Name: pdt_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE pdt_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE pdt_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE pdt_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE pdt_id_seq TO kamailioro;


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
GRANT SELECT ON TABLE presentity TO kamailioro;


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
-- Name: re_grp; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE re_grp FROM PUBLIC;
REVOKE ALL ON TABLE re_grp FROM kamailio;
GRANT ALL ON TABLE re_grp TO kamailio;
GRANT SELECT ON TABLE re_grp TO kamailioro;


--
-- Name: re_grp_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE re_grp_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE re_grp_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE re_grp_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE re_grp_id_seq TO kamailioro;


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
-- Name: silo; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE silo FROM PUBLIC;
REVOKE ALL ON TABLE silo FROM kamailio;
GRANT ALL ON TABLE silo TO kamailio;
GRANT SELECT ON TABLE silo TO kamailioro;


--
-- Name: silo_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE silo_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE silo_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE silo_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE silo_id_seq TO kamailioro;


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
-- Name: subscriber; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE subscriber FROM PUBLIC;
REVOKE ALL ON TABLE subscriber FROM kamailio;
GRANT ALL ON TABLE subscriber TO kamailio;
GRANT SELECT ON TABLE subscriber TO kamailioro;


--
-- Name: subscriber_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE subscriber_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE subscriber_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE subscriber_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE subscriber_id_seq TO kamailioro;


--
-- Name: topos_d; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE topos_d FROM PUBLIC;
REVOKE ALL ON TABLE topos_d FROM kamailio;
GRANT ALL ON TABLE topos_d TO kamailio;
GRANT SELECT ON TABLE topos_d TO kamailioro;


--
-- Name: topos_d_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE topos_d_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE topos_d_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE topos_d_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE topos_d_id_seq TO kamailioro;


--
-- Name: topos_t; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE topos_t FROM PUBLIC;
REVOKE ALL ON TABLE topos_t FROM kamailio;
GRANT ALL ON TABLE topos_t TO kamailio;
GRANT SELECT ON TABLE topos_t TO kamailioro;


--
-- Name: topos_t_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE topos_t_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE topos_t_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE topos_t_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE topos_t_id_seq TO kamailioro;


--
-- Name: trusted; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE trusted FROM PUBLIC;
REVOKE ALL ON TABLE trusted FROM kamailio;
GRANT ALL ON TABLE trusted TO kamailio;
GRANT SELECT ON TABLE trusted TO kamailioro;


--
-- Name: trusted_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE trusted_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE trusted_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE trusted_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE trusted_id_seq TO kamailioro;


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
-- Name: usr_preferences; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON TABLE usr_preferences FROM PUBLIC;
REVOKE ALL ON TABLE usr_preferences FROM kamailio;
GRANT ALL ON TABLE usr_preferences TO kamailio;
GRANT SELECT ON TABLE usr_preferences TO kamailioro;


--
-- Name: usr_preferences_id_seq; Type: ACL; Schema: public; Owner: kamailio
--

REVOKE ALL ON SEQUENCE usr_preferences_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE usr_preferences_id_seq FROM kamailio;
GRANT ALL ON SEQUENCE usr_preferences_id_seq TO kamailio;
GRANT SELECT ON SEQUENCE usr_preferences_id_seq TO kamailioro;


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

