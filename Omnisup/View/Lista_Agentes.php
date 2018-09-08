<br><br>
<!-- Copyright (C) 2018 Freetech Solutions

 This file is part of OMniLeads

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see http://www.gnu.org/licenses/.

-->
<div class="container-fluid">
    <div class="modal fade" id="modalWebCall" role="dialog">
        <div class="modal-dialog modal-sm">
            <div class="modal-content Modal-Content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal">&times;</button>
                    <h4>WebPhone</h4>
                </div>
                <div class="modal-body">
                    <div class="container-fluid">
                        <!-- -->
                        <div id="modalReceiveCalls" class="modal fade bs-modal-sm" tabindex="-1" role="dialog" aria-labelledby="mySmallModalLabel" aria-hidden="true">
                            <div class="modal-dialog modal-sm">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <em><b class="tituloLlamEntrante">Llamada Entrante</b></em>
                                        <button type="button" class="close" data-dismiss="modal">&times;</button>
                                    </div>
                                    <div class="modal-body">
                                        <h4 class="cuerpoLlamEntrante">
                                            <span class="label label-info">De:</span>
                                            <label name="callerid" id="callerid"></label><br>
                                            <span class="label label-info">Info extra:</span>
                                            <label name="extraInfo" id="extraInfo">.....</label>
                                        </h4>
                                    </div>
                                    <div class="modal-footer">
                                        <button type="button" id="answer" class="btn btn-success btn-sm">Responder</button>
                                        <button type="button" id="doNotAnswer" class="btn btn-danger btn-sm">Rechazar</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <!-- -->
                        <div class="row">
                            <br>
                            <div class="backgroundWebPhone col-md-10 col-md-offset-1">
                                <div class="row">
                                    <div id="CallStatus" class="botonera1">
                                    </div>
                                </div>
                                <div class="row">
                                    <div id="SipStatus" class="botonera1">
                                    </div>
                                </div>
                                <div class="row filaBotonesDiscar">
                                    <button type="button" placeholder='atender' id="call" class="btn btn-success">
                                        <span class="glyphicon glyphicon-earphone"></span>
                                    </button>
                                    <button type="button" placeholder='finalizar' id="endCall" class="btn btn-danger">
                                        <span class="glyphicon glyphicon-phone-alt"></span>
                                    </button>
                                </div>
                            </div>
                        </div><br>
                    </div>
                </div>
            </div>
            <audio id="remoteAudio" autoplay="autoplay"></audio>
            <audio id="localAudio" muted="muted"></audio>
            <audio id="RingIn">
                <source id="fuenteIn" src="static/Tones/Kuma.mp3" type="audio/mpeg">
            </audio>
            <audio id="RingOut">
                <source id="fuenteOut" src="static/Tones/tonoallamar.mp3" type="audio/mpeg">
            </audio>
            <audio id="RingBusy">
                <source id="fuentebOut" src="static/Tones/busy.mp3" type="audio/mpeg">
            </audio>
        </div>
    </div>

    <div class="col-md-4 col-lg-offset-4">
        <table id="tableAgt" class="table table-stripped">
            <thead>
                <tr>
                    <th>Agentes</th><th>Estado</th><th>Tiempo</th><th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                <?php
                include $_SERVER['DOCUMENT_ROOT'] . '/Omnisup/config.php';
                include controllers . '/Agente.php';

                $Controller_Agente = new Agente();
                $resul = $Controller_Agente->traerAgentes();
                foreach ($resul as $clave => $valor) {
                    if ($clave == "Ok") {
                        foreach ($valor as $cla => $val) {
                            if (strpos($val, "/")) {
                                $backslashPos = strpos($val, "/");
                                $val = substr($val, $backslashPos + 1);
                            }
                            ?>
                            <tr>
                                <td style='color:green'>
                                    <?= $val ?>
                                </td>
                                <td style='color:green'>
                                    Online
                                </td>
                                <td>
                                    <label id="horas"></label><label id="minutos"></label><label id="segundos"></label>
                                </td>
                                <td>
                                    <button type="button" id="<?= $val ?>" class="btn btn-primary btn-xs chanspy" placeholder="monitorear">
                                        <span class="glyphicon glyphicon-eye-open"></span>
                                    </button>
                                    <button type="button" id="<?= $val ?>" class="btn btn-primary btn-xs chanspywhisper" placeholder="hablar con agente">
                                        <span class="glyphicon glyphicon-sunglasses"></span>
                                    </button>
                                </td>
                            </tr>
                            <?php
                        }
                    } elseif ($clave == "Unk") {
                        foreach ($valor as $cla => $val) {
                            if (strpos($val, "/")) {
                                $backslashPos = strpos($val, "/");
                                $val = substr($val, $backslashPos + 1);
                            }
                            ?>
                            <tr>
                                <td style='color:grey'><?= $val ?>
                                </td>
                                <td style='color:grey'>
                                    Unknown
                                </td>
                                <td>B</td>
                            </tr>
                            <?php
                        }
                    } elseif ($clave == "Unr") {
                        foreach ($valor as $cla => $val) {
                            if (strpos($val, "/")) {
                                $backslashPos = strpos($val, "/");
                                $val = substr($val, $backslashPos + 1);
                            }
                            ?>
                            <tr>
                                <td style='color:darkcyan'><?= $val ?>
                                </td>
                                <td style='color:darkcyan'>
                                    Unreachable
                                </td>
                                <td>B</td>
                            </tr>
                            <?php
                        }
                    }
                }
                ?>
            </tbody>
        </table>
    </div>
</div>
