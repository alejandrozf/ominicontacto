<h1>Campaña: <b id="nombreCamp"><?= $_GET['nomcamp'] ?></b></h1>

<!-- Web phone -->
<input type="hidden" id="sipUser" name="sipUser" value="" />
<input type="hidden" id="sipPass" name="sipPass" value="" />
<div class="modal fade" id="modalWebCall" role="dialog">
    <div class="modal-dialog modal-sm">
        <div class="modal-content">
            <div class="modal-header">
                <h1 class="modal-title">Webphone</h1>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            <div class="modal-body">
                <!-- -->
                <input type="hidden" value="<?= $_GET['supervId'] ?>" id="userId"/>
                <input type="hidden" value="<?= $_GET['campId'] ?>" id="campId"/>
                <!-- -->
                <div class="row">
                    <div class="backgroundWebPhone">
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

<!-- Moda de llamada entrante -->
<div id="modalReceiveCalls" class="modal fade bs-modal-sm" tabindex="-1" role="dialog" aria-labelledby="mySmallModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-sm">
        <div class="modal-content">
            <div class="modal-header">
                <h1 class="modal-title">Llamada Entrante</h1>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
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
                <button type="button" id="answer" class="btn btn-primary btn-sm">Responder</button>
                <button type="button" id="doNotAnswer" class="btn btn-danger btn-sm">Rechazar</button>
            </div>
        </div>
    </div>
</div>

<div class="jumbotron">
    <div class="row">
        <div class="col-sm-3">
            <h1 class="display-2">12<span id="objcampana"></span> <span id="gestioncampana"></span></h1>
            <h3>Avance de objetivo</h3>
        </div>
        <div class="col-sm-3">
            <h1 class="display-2">12%<span id="percent"></span></h1>
            <h3>Porcentaje de objetivo</h3>
        </div>
    </div>
</div>

<div class="row">
    <button alt="openWebPhone" id="webphone">webphone</button>
    <hr>
    <br>
    <br>
</div>

<div class="row">
    <div class="col-md-6"><!-- CUADRO RESUMEN CAMPANA -->
      <h2>Resumen y calificaciones</h2>
      <table id="tableCampSummary" class="table">
          <tbody id="bodySummary">
          </tbody>
          <tr>
              <td>Llamadas:</td>
              <td></td>
          </tr>
          <tbody id="bodyScore">
          </tbody>
      </table>
    </div>
    <div class="col-md-6"><!-- CUADRO AGENTES -->
        <h2>Agentes</h2>
        <table id="tableAgt" class="table">
            <thead>
                <tr>
                    <th>Agentes</th>
                    <th>Estado</th>
                    <th>Tiempo</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody id="tableAgBody">
            </tbody>
        </table>
    </div>
</div>
<hr class="hr-space">
<div class="row">
    <div class="col-md-6"><!-- CUADRO CANALES -->
      <h2>Estado general de lineas</h2>
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
    <div class="col-md-6"><!-- CUADRO LLAMADAS EN COLA -->
      <h2>Llamadas en espera</h2>
      <table class="table">
          <thead>
            <tr>
                <th>Tiempo</th>
                <th>#</th>
            </tr>
          </thead>
          <tbody id="tableQueuedCalls">
          </tbody>
      </table>
    </div>
</div>
