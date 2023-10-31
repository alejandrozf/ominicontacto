CREATE OR REPLACE FUNCTION insert_queue_log_ominicontacto_queue_log() returns trigger as $$
$fecha = $_TD->{new}{time};
$callid = $_TD->{new}{callid};
$queuename = $_TD->{new}{queuename}; # <id-campana>-<tipo-campana>-<tipo-llamada>
$agente_id = $_TD->{new}{agent};
$event = $_TD->{new}{event};
# 'data1' en los logs de llamadas tiene el número marcado y en los eventos de agente
# el id de la pausa
$data1 = $_TD->{new}{data1};
$contacto_id = $_TD->{new}{data2};
$bridge_wait_time = $_TD->{new}{data3};
$duracion_llamada = $_TD->{new}{data4};
$archivo_grabacion = $_TD->{new}{data5};

@EVENTOS_LLAMADAS = (
    'DIAL',
    'ANSWER',
    'CONNECT',
    'COMPLETEAGENT',
    'COMPLETEOUTNUM',
    'ENTERQUEUE',
    'EXITWITHTIMEOUT',
    'ABANDON',
    'NOANSWER',
    'CANCEL',
    'BUSY',
    'CHANUNAVAIL',
    'OTHER',
    'FAIL',
    'AMD',
    'BLACKLIST',
    'RINGNOANSWER',
    'NONDIALPLAN',
    'CONGESTION',
    'ABANDONWEL',
    );

@EVENTOS_TRANSFERENCIAS = (
    'BT-TRY',
    'BT-ANSWER',
    'BT-BUSY',
    'BT-CANCEL',
    'BT-CHANUNAVAIL',
    'BT-CONGESTION',
    'BT-ABANDON',
    'BT-NOANSWER',
    'CAMPT-TRY',
    'CAMPT-FAIL',
    'CAMPT-COMPLETE',
    'ENTERQUEUE-TRANSFER',
    'CT-TRY',
    'CT-ANSWER',
    'CT-ACCEPT',
    'CT-COMPLETE',
    'CT-DISCARD',
    'CT-BUSY',
    'CT-CANCEL',
    'CT-CHANUNAVAIL',
    'CT-CONGESTION',
    'BTOUT-TRY',
    'BTOUT-ANSWER',
    'BTOUT-BUSY',
    'BTOUT-CANCEL',
    'BTOUT-CONGESTION',
    'BTOUT-CHANUNAVAIL',
    'BTOUT-ABANDON',
    'BTOUT-NONDIALPLAN',
    'CTOUT-TRY',
    'CTOUT-ANSWER',
    'CTOUT-ACCEPT',
    'CTOUT-COMPLETE',
    'CTOUT-DISCARD',
    'CTOUT-BUSY',
    'CTOUT-CANCEL',
    'CTOUT-CHANUNAVAIL',
    'CTOUT-CONGESTION',
    'CTOUT-NONDIALPLAN',
    'COMPLETE-CTOUT',
    'COMPLETE-CT',
    'COMPLETE-BT',
    'COMPLETE-BTOUT',
    'COMPLETE-CAMPT',
    'CT-ABANDON',
    'ABANDON-CT',
    'CTOUT-ABANDON',
    'ABANDON-CTOUT',
    );

@EVENTOS = (@EVENTOS_LLAMADAS, @EVENTOS_TRANSFERENCIAS);


sub is_number  {
    if (length($_[0]) == length(int($_[0]))) {
        return 1;
    }
    else {
        return 0;
    }
}


sub procesar_datos_transferencias {
    # Parsea la información de los valores generados desde los campos 'agent', 'data4' y
    # 'data5' para obtener los valores de los campos de los logs de transferencias de llamadas:
    # (agente_extra_id, campana_extra_id, numero_extra)
    $agente_data = $_TD->{new}{agent};
    ($agente_id_modificado, $agente_extra_id, $campana_extra_id, $numero_extra) = (-1, -1, -1, -1);
    eval {
        ($valor_transf_1, $valor_transf_2) = split("-", $agente_data);
    }
    or do {
        ($valor_transf_1, $valor_transf_2) = ($agente_data, undef);
    };
    if( grep $_ eq $event,  ('BT-TRY', 'CAMPT-COMPLETE', 'CT-TRY')) {
        # agente_id_origen - id_agente_origen
        $agente_id_modificado = $valor_transf_1;
        $agente_extra_id = $valor_transf_2;
    }
    elsif ( $event eq 'CAMPT-TRY') {
        # agente_id - id_camp_destino
        $agente_id_modificado = $valor_transf_1;
        $campana_extra_id = $valor_transf_2;
    }
    elsif ( $event eq 'ENTERQUEUE-TRANSFER') {
        # id_camp_origen - id_agente_origen (en data4, data5)
        $campana_extra_id = $_TD->{new}{data4};
        $agente_id_modificado = $_TD->{new}{data5};
    }
    elsif ($event eq ('BTOUT-TRY', 'CTOUT-TRY')) {
        # agente_id_origen - nro_telefono_destino
        $agente_id_modificado = $valor_transf_1;
        $numero_extra = $valor_transf_2;
    }
    elsif ( grep $_ eq $event,  ('BTOUT-ANSWER', 'BTOUT-BUSY', 'BTOUT-CANCEL', 'BTOUT-CONGESTION',
                                 'BTOUT-CHANUNAVAIL', 'BTOUT-ABANDON', 'CTOUT-ANSWER', 'CTOUT-ACCEPT',
                                 'CTOUT-DISCARD', 'CTOUT-BUSY', 'CTOUT-CANCEL', 'CTOUT-CHANUNAVAIL',
                                 'CTOUT-CONGESTION', 'COMPLETE-BTOUT', 'COMPLETE-CTOUT',
                                 'CTOUT-ABANDON', 'BTOUT-NONDIALPLAN', 'CTOUT-NONDIALPLAN')) {
        # el valor del campo 'agent' tiene un número de telefono
        $agente_id_modificado = -1;
        $numero_extra = $valor_transf_1;
    }
    else {
        # en los eventos de transferencias con un solo valor que contiene el id de un agente
        # solo se mantiene el valor de 'agente_id'
        $agente_id_modificado = $valor_transf_1;
    }
    return ($agente_id_modificado, $agente_extra_id, $campana_extra_id, $numero_extra);
}

if ( grep $_ eq $event,  @EVENTOS)  {
    eval {
        ($campana_id, $tipo_campana, $tipo_llamada) = split("-", $queuename);
    }
    or do {
        ($campana_id, $tipo_campana, $tipo_llamada) = (-1, -1, -1);
    };

    if (grep $_ eq $event,  @EVENTOS_TRANSFERENCIAS) {
        ($agente_id, $agente_extra_id, $campana_extra_id, $numero_extra) = procesar_datos_transferencias();
    } else {
        ($agente_extra_id, $campana_extra_id, $numero_extra) = (-1, -1, -1);
    }

    my $plan_llamadas_log =  spi_prepare('INSERT INTO reportes_app_llamadalog( time, callid, campana_id, tipo_campana, tipo_llamada, agente_id, event, numero_marcado, contacto_id, bridge_wait_time, duracion_llamada, archivo_grabacion, agente_extra_id, campana_extra_id, numero_extra )VALUES( $1 ,$2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15 )',
                                         'timestamp with time zone', 'text', 'int', 'int', 'int', 'int', 'text', 'text', 'int',
                                         'int', 'int', 'text', 'int', 'int', 'text');
    if (is_number($agente_id) == 1 || $agente_id == -1) {
        eval {
            spi_exec_prepared($plan_llamadas_log, {limit => 1}, $fecha, $callid, $campana_id, $tipo_campana, $tipo_llamada,
                              $agente_id, $event, $data1, $contacto_id, $bridge_wait_time,
                              $duracion_llamada, $archivo_grabacion, $agente_extra_id,
                              $campana_extra_id, $numero_extra);
        }
        or do {
            my $e = $@;
            my $entrada = "fecha=$fecha,\ncallid=$callid,\ncampana_id=$campana_id,\ntipo_campana=$tipo_campana,\n".
                "tipo_llamada=$tipo_llamada,\nagente_id=$agente_id,\nevent=$event,\ndata1=$data1,\n".
                "contacto_id=$contacto_id,\nbridge_wait_time=$bridge_wait_time,\nduracion_llamada=$duracion_llamada,\n".
                "archivo_grabacion=$archivo_grabacion,\nagente_extra_id=$agente_extra_id,\ncampana_extra_id=$campana_extra_id,\n".
                "numero_extra=$numero_extra.\n";
            elog(ERROR, "Error $e trying to insert input $entrada");
        };
    }

}

else {
    # no insertamos logs de estos eventos de momento
}

return;

$$ language plperl;
