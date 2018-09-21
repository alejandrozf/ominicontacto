<h1>Campaña: <b id="nombreCamp"><?= $_GET['nomcamp'] ?></b></h1>
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
                <div class="text-center">
                    <div id="CallStatus"></div>
                    <div id="SipStatus"></div>
                </div>
                <hr>
                <div>
                    <button type="button" placeholder='atender' id="call" class="btn btn-primary btn-block">
                        Atender
                    </button>
                    <button type="button" placeholder='finalizar' id="endCall" class="btn btn-outline-danger btn-block">
                        Finalizar
                    </button>
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
                <button type="button" id="answer" class="btn btn-primary">Responder</button>
                <button type="button" id="doNotAnswer" class="btn btn-outline-danger">Rechazar</button>
            </div>
        </div>
    </div>
</div>

<button type="button" id="webphone" class="btn btn-outline-primary" alt="openWebPhone"><span class="icon icon-solid-phone"></span> Phone</button>

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
                  <!-- <tr>
                    <td><span class="badge badge-outline line-connected">Connected</span></td><td>3516285260</td>
                  </tr>
                  <tr>
                    <td><span class="badge badge-outline line-calling">Calling</span></td><td>3516285260</td>
                  </tr>
                  <tr>
                    <td><span class="badge badge-outline line-shortcall">Short call</span></td><td>3516285260</td>
                  </tr>
                  <tr>
                    <td><span class="badge badge-outline line-connected">Connected</span></td><td>3516285260</td>
                  </tr>
                  <tr>
                    <td><span class="badge badge-outline line-calling">Calling</span></td><td>3514215610</td>
                  </tr> -->
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
                    <!-- <tr>
                      <td><span class="icon far fa-clock"></span>00:02:56</td><td>4553131</td>
                    </tr>
                    <tr>
                      <td><span class="icon far fa-clock"></span>00:00:34</td><td>4328977</td>
                    </tr>
                    <tr>
                      <td><span class="icon far fa-clock"></span>00:01:09</td><td>4149090</td>
                    </tr>
                    <tr>
                      <td><span class="icon far fa-clock"></span>00:05:12</td><td>4287920</td>
                    </tr>
                    <tr>
                      <td><span class="icon far fa-clock"></span>00:05:12</td><td>4287920</td>
                    </tr> -->
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
                      <h1 class="display-3">
                        <span id="objcampana"></span>
                        <span>/</span>
                        <span id="gestioncampana"></span>
                      </h1>
                      <span class="label">Avance de objetivo</span>
                  </div>
                  <div class="col-sm-6">
                      <h1 class="display-3"><span id="percent"></span></h1>
                      <span class="label">Porcentaje de objetivo</span>
                  </div>
              </div>
              <hr>
              <h2>Llamadas</h2>
              <div id="bodyScore">
              </div>
          </div>
      </div>
  </div>
</div>
