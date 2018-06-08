<br/><br/>
<div class="container-fluid">
  <input type="hidden" id="sipUser" name="sipUser" value="" />
  <input type="hidden" id="sipPass" name="sipPass" value="" />
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
                        <input type="hidden" value="<?= $_GET['supervId'] ?>" id="userId"/>
                        <input type="hidden" value="<?= $_GET['campId'] ?>" id="campId"/>
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
    <div class="col-md-11">
        <img class="webphone" src="static/Img/webCallTransp.png" alt="openWebPhone" id="webphone"/>
        <h3 class="col-md-11">Campaña: <b id='nombreCamp'><?= $_GET['nomcamp'] ?></b>.
                       &nbsp;Avance de objetivo: <b id="gestioncampana"></b>/<b id="objcampana"></b>
                       &nbsp;Porcentaje de objetivo: <b id="percent"></b></h3><!-- NOMBRE CAMPANA -->
    </div>
    <div class="col-md-12">
        <br>
        <div class="col-md-2"><!-- CUADRO RESUMEN CAMPANA -->
          <h4 class="subtitle">Resumen y calificaciones</h4>
          <br>
          <table id="tableCampSummary" class="table table-striped table-condensed">
              <tbody id="bodySummary">
                <!-- <tr><td><b>Llamadas:</b></td><td></td></tr>
                <tr><td>Recibidas</td><td id="received"></td></tr>
                <tr><td>Atendidas</td><td id="attended"></td></tr>
                <tr><td>Abandonadas</td><td id="abandoned"></td></tr>
                <tr><td>Expiradas</td><td id="expired"></td></tr>
                <tr><td>Manuales</td><td id="manuals"></td></tr>
                <tr><td>Manuales atendidas</td><td id="manualsa"></td></tr>
                <tr><td>Manuales NO atendidas</td><td id="manualsna"></td></tr>
                <tr><td>Contestador detectado</td><td id="answererdetected"></td></tr> -->
              </tbody>
              <tr><td><b>Llamadas:</b></td><td></td></tr>
              <tbody id="bodyScore">
              </tbody>
          </table>
        </div>
        <div class="col-md-5"><!-- CUADRO AGENTES -->
            <h4 class="subtitle">Agentes</h4>
            <table id="tableAgt" class="table table-striped table-condensed">
                <thead>
                    <tr>
                        <th>Agentes</th><th>Estado</th><th>Tiempo</th><th>Acciones</th>
                    </tr>
                </thead>
                <tbody id="tableAgBody">
                </tbody>
            </table>
        </div>
        <div class="col-md-3"><!-- CUADRO CANALES -->
          <h4 class="subtitle">Estado general de lineas</h4>
          <table id="" class="table table-striped table-condensed">
              <thead>
                  <tr>
                      <th>Estado</th><th>Destino</th>
                  </tr>
              </thead>
              <tbody id="tableChannelsWombat">
              </tbody>
          </table>
        </div>
        <div class="col-md-2"><!-- CUADRO LLAMADAS EN COLA -->
          <h4 class="subtitle">Llamadas en espera</h4>
          <table class="table table-striped table-condensed">
              <thead>
                <tr>
                    <th>Tiempo</th><th>#</th>
                </tr>
              </thead>
              <tbody id="tableQueuedCalls">
              </tbody>
          </table>
        </div>
    </div>
</div>
