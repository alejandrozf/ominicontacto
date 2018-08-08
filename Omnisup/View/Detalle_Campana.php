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

<button style="position:absolute; top:30px; right:50px;" type="button" class="btn btn-outline-primary btn-sm" alt="openWebPhone" id="webphone"><span class="icon icon-phone"></span> webphone</button>

<ul class="nav nav-tabs" id="supervisionTabBar" role="tablist">
  <li class="nav-item">
    <a class="nav-link active" id="stateTab" data-toggle="tab" href="#stateContent" role="tab" aria-controls="home" aria-selected="true">Estado</a>
  </li>
  <li class="nav-item">
    <a class="nav-link" id="callsTab" data-toggle="tab" href="#callsContent" role="tab" aria-controls="profile" aria-selected="false">Llamadas</a>
  </li>
</ul>

<div class="tab-content" id="supervisionTabContent">

    <div class="tab-pane fade show active" id="stateContent" role="tabpanel" aria-labelledby="stateTab">
        <div class="row">
            <div class="col-md-6"><!-- CUADRO AGENTES -->
              <table id="tableAgt" class="table table-sm">
                <thead>
                    <tr>
                        <th>Agentes</th><th>Estado</th><th>Tiempo</th><th>Acciones</th>
                    </tr>
                </thead>
                  <tbody id="tableAgBody">
                  </tbody>
              </table>
              <nav aria-label="Page navigation example">
                <ul class="pagination pagination-sm">
                  <li class="page-item">
                    <a class="page-link" href="#" aria-label="Previous">
                      <span aria-hidden="true">&laquo;</span>
                      <span class="sr-only">Previous</span>
                    </a>
                  </li>
                  <li class="page-item"><a class="page-link" href="#">1</a></li>
                  <li class="page-item"><a class="page-link" href="#">2</a></li>
                  <li class="page-item"><a class="page-link" href="#">3</a></li>
                  <li class="page-item">
                    <a class="page-link" href="#" aria-label="Next">
                      <span aria-hidden="true">&raquo;</span>
                      <span class="sr-only">Next</span>
                    </a>
                  </li>
                </ul>
              </nav>
            </div>

          <div class="col-md-3"><!-- CUADRO CANALES -->
            <h2>Estado de lineas</h2>
            <table id="" class="table table-sm">
                <tbody id="tableChannelsWombat">
                </tbody>
            </table>
            <nav aria-label="Page navigation example">
              <ul class="pagination pagination-sm">
                <li class="page-item">
                  <a class="page-link" href="#" aria-label="Previous">
                    <span aria-hidden="true">&laquo;</span>
                    <span class="sr-only">Previous</span>
                  </a>
                </li>
                <li class="page-item"><a class="page-link" href="#">1</a></li>
                <li class="page-item"><a class="page-link" href="#">2</a></li>
                <li class="page-item"><a class="page-link" href="#">3</a></li>
                <li class="page-item">
                  <a class="page-link" href="#" aria-label="Next">
                    <span aria-hidden="true">&raquo;</span>
                    <span class="sr-only">Next</span>
                  </a>
                </li>
              </ul>
            </nav>
        </div>
        <div class="col-md-3">
            <h2>Llamadas en espera</h2>
            <table class="table table-sm">
                <tbody id="tableQueuedCalls">
                </tbody>
            </table>
            <nav aria-label="Page navigation example">
              <ul class="pagination pagination-sm">
                <li class="page-item">
                  <a class="page-link" href="#" aria-label="Previous">
                    <span aria-hidden="true">&laquo;</span>
                    <span class="sr-only">Previous</span>
                  </a>
                </li>
                <li class="page-item"><a class="page-link" href="#">1</a></li>
                <li class="page-item"><a class="page-link" href="#">2</a></li>
                <li class="page-item"><a class="page-link" href="#">3</a></li>
                <li class="page-item">
                  <a class="page-link" href="#" aria-label="Next">
                    <span aria-hidden="true">&raquo;</span>
                    <span class="sr-only">Next</span>
                  </a>
                </li>
              </ul>
            </nav>
          </div>
      </div>
  </div>


  <div class="tab-pane fade" id="callsContent" role="tabpanel" aria-labelledby="callsTab">

      <div class="row">
          <div class="col-md-6"><!-- CUADRO RESUMEN CAMPANA -->
            <h2>Resumen y calificaciones</h2>
            <table id="tableCampSummary" class="table table-sm">
                <tbody id="bodySummary">
                </tbody>
            </table>
            <nav aria-label="Page navigation example">
              <ul class="pagination pagination-sm">
                <li class="page-item">
                  <a class="page-link" href="#" aria-label="Previous">
                    <span aria-hidden="true">&laquo;</span>
                    <span class="sr-only">Previous</span>
                  </a>
                </li>
                <li class="page-item"><a class="page-link" href="#">1</a></li>
                <li class="page-item"><a class="page-link" href="#">2</a></li>
                <li class="page-item"><a class="page-link" href="#">3</a></li>
                <li class="page-item">
                  <a class="page-link" href="#" aria-label="Next">
                    <span aria-hidden="true">&raquo;</span>
                    <span class="sr-only">Next</span>
                  </a>
                </li>
              </ul>
            </nav>
          </div>
          <div class="col-md-6">
              <div class="row">
                  <div class="col-sm-6">
                      <h1 class="display-3"><span id="objcampana"></span><span id="gestioncampana"></span></h1>
                      <span class="label">Avance de objetivo</span>
                  </div>
                  <div class="col-sm-6">
                      <h1 class="display-3"><span id="percent"></span></h1>
                      <span class="label">Porcentaje de objetivo</span>
                  </div>
              </div>
              <hr>
              <h2>Llamadas</h2>
              <div class="">
                  <span class="label">Recibidas</span>,
                  <span class="label">Atendidas</span>,
                  <span class="label">Abandonadas</span>,
                  <span class="label">Expiradas</span>,
                  <span class="label">Espera</span>,
                  <span class="label">Abandono</span>
              </div>
              <hr>
              <h2>Llamadas Manuales</h2>
              <div class="">
                  <span class="label">Efectuadas</span>,
                  <span class="label">Conectadas</span>,
                  <span class="label">No conec.</span>,
                  <span class="label">Espera prom.</span>
              </div>
          </div>
      </div>
  </div>
</div>
