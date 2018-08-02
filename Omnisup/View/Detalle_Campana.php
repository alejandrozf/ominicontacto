<h1 id="nombreCamp">Campaña: <?= $_GET['nomcamp'] ?></h1>

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

<button style="position:absolute; top:30px; right:50px;" type="button" class="btn btn-outline-primary btn-sm" alt="openWebPhone" id="webphone">webphone</button>

<ul class="nav nav-tabs" id="supervisionTabBar" role="tablist">
  <li class="nav-item">
    <a class="nav-link active" id="messagesTab" data-toggle="tab" href="#messagesContent" role="tab" aria-controls="home" aria-selected="true">Uno</a>
  </li>
  <li class="nav-item">
    <a class="nav-link" id="registryTab" data-toggle="tab" href="#registryContent" role="tab" aria-controls="profile" aria-selected="false">Dos</a>
  </li>
</ul>

<div class="tab-content" id="messagesTabContent">

  <div class="tab-pane fade show active" id="messagesContent" role="tabpanel" aria-labelledby="messagesTab">

      <div class="col-md-6"><!-- CUADRO AGENTES -->
          <h2>Agentes</h2>
          <table id="tableAgt" class="table table-stripped table-sm">
              <thead>
                  <tr>
                      <th>Agentes</th>
                      <th>Estado</th>
                      <th>Tiempo</th>
                      <th>Acciones</th>
                  </tr>
              </thead>
              <tbody id="tableAgBody">
                <tr>
                  <td>felipem</td>
                  <td>DIALING</td>
                  <td>23:28:33</td>
                  <td>
                      <div class="dropdown">
                          <button type="button" class="btn btn-light dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                          Opciones
                          </button>
                          <div class="dropdown-menu dropdown-menu-right">
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-eye"></span>Monitorear
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Hablar con agente
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-control-pause"></span>Pausar agente
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Pausar agente
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Log off agente
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Tomar llamada
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Conferencia
                              </a>
                          </div>
                      </div>
                  </td>
                </tr>
                <tr>
                  <td>Pepe</td>
                  <td>PAUSE - Sanitario</td>
                  <td>23:28:33</td>
                  <td>
                      <div class="dropdown">
                          <button type="button" class="btn btn-light dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                          Opciones
                          </button>
                          <div class="dropdown-menu dropdown-menu-right">
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-eye"></span>Monitorear
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Hablar con agente
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-control-pause"></span>Pausar agente
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Pausar agente
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Log off agente
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Tomar llamada
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Conferencia
                              </a>
                          </div>
                      </div>
                  </td>
                </tr>
                <tr role="row" class="odd">
                  <td>AgenteTest</td><td>OFFLINE</td><td>23:28:33</td>
                  <td>
                      <div class="dropdown">
                          <button type="button" class="btn btn-light dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                          Opciones
                          </button>
                          <div class="dropdown-menu dropdown-menu-right">
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-eye"></span>Monitorear
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Hablar con agente
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-control-pause"></span>Pausar agente
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Pausar agente
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Log off agente
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Tomar llamada
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Conferencia
                              </a>
                          </div>
                      </div>
                  </td>
                </tr>
                <tr role="row" class="odd">
                  <td>Fulano</td><td>READY</td><td>23:28:33</td>
                  <td>
                      <div class="dropdown">
                          <button type="button" class="btn btn-light dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                          Opciones
                          </button>
                          <div class="dropdown-menu dropdown-menu-right">
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-eye"></span>Monitorear
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Hablar con agente
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-control-pause"></span>Pausar agente
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Pausar agente
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Log off agente
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Tomar llamada
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Conferencia
                              </a>
                          </div>
                      </div>
                  </td>
                </tr>
                <tr role="row" class="odd">
                  <td>ABCDEG</td><td>ONCALL</td><td>23:28:33</td>
                  <td>
                      <div class="dropdown">
                          <button type="button" class="btn btn-light dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                          Opciones
                          </button>
                          <div class="dropdown-menu dropdown-menu-right">
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-eye"></span>Monitorear
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Hablar con agente
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-control-pause"></span>Pausar agente
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Pausar agente
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Log off agente
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Tomar llamada
                              </a>
                              <a class="dropdown-item" href="#">
                                  <span class="icon icon-pencil"></span>Conferencia
                              </a>
                          </div>
                      </div>
                  </td>
                </tr>
              </tbody>
          </table>
      </div>

      <div class="row">
          <div class="col-md-6"><!-- CUADRO CANALES -->
            <hr>
            <h2>Estado general de lineas</h2>
            <table id="" class="table table-sm">
                <thead>
                    <tr>
                        <th>Estado</th><th>Destino</th>
                    </tr>
                </thead>
                <tbody id="tableChannelsWombat">
                  <tr>
                    <td>Connected</td><td>3516285260</td>
                  </tr>
                  <tr>
                    <td>Connected</td><td>3516285260</td>
                  </tr>
                  <tr>
                    <td>Connected</td><td>3516285260</td>
                  </tr>
                  <tr>
                    <td>Calling</td><td>3516285260</td>
                  </tr>
                  <tr>
                    <td>Calling</td><td>3516285260</td>
                  </tr>
                  <tr>
                    <td>ShortCall</td><td>3516285260</td>
                  </tr>
                  <tr>
                    <td>Connected</td><td>3516285260</td>
                  </tr>
                  <tr>
                    <td>Calling</td><td>3514215610</td>
                  </tr>
                  <tr>
                    <td>ShortCall</td><td>3516285260</td>
                  </tr>
                </tbody>

            </table>
          </div>
          <div class="col-md-6"><!-- CUADRO LLAMADAS EN COLA -->
              <hr>
            <h2>Llamadas en espera</h2>
            <table class="table table-sm">
                <thead>
                  <tr>
                      <th>Tiempo</th>
                      <th>#</th>
                  </tr>
                </thead>
                <tbody id="tableQueuedCalls">
                    <tr>
                      <td>00:02:56</td><td>4553131</td>
                    </tr>
                    <tr>
                      <td>00:00:34</td><td>4328977</td>
                    </tr>
                    <tr>
                      <td>00:01:09</td><td>4149090</td>
                    </tr>
                    <tr>
                      <td>00:05:12</td><td>4287920</td>
                    </tr>
                </tbody>
            </table>
          </div>
      </div>
  </div>


  <div class="tab-pane fade" id="registryContent" role="tabpanel" aria-labelledby="registryTab">

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

</div>
      <div class="row">
          <div class="col-md-6"><!-- CUADRO RESUMEN CAMPANA -->
            <h2>Resumen y calificaciones</h2>
            <table id="tableCampSummary" class="table table-sm">
                <tbody id="bodySummary">
                  <tr>
                    <td>Agendados</td><td>2374</td>
                  </tr>
                  <tr>
                    <td>bonito</td><td>1148</td>
                  </tr>
                  <tr>
                    <td>Venta</td><td>995</td>
                  </tr>
                  <tr>
                    <td>barato</td><td>3286</td>
                  </tr>
                  <tr>
                    <td>Agendado</td><td>787</td>
                  </tr>
                </tbody>
            </table>
          </div>
          <div class="col-md-6">
              <h2>Llamadas</h2>
              <div class="">
                  0<span class="label">Recibidas</span>,
                  0<span class="label">Atendidas</span>,
                  0<span class="label">Abandonadas</span>,
                  0<span class="label">Expiradas</span>,
                  0<span class="label">Espera</span>,
                  0<span class="label">Abandono</span>
              </div>
              <hr>
              <h2>Llamadas Manuales</h2>
              <div class="">
                  0<span class="label">Efectuadas</span>,
                  0<span class="label">Conectadas</span>,
                  0<span class="label">No conec.</span>,
                  0<span class="label">Espera prom.</span>
              </div>
          </div>
      </div>
  </div>
</div>
