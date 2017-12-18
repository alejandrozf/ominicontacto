<?php
include_once $_SERVER['DOCUMENT_ROOT'] . '/Omnisup/config.php';
$SupervId = isset($_GET["supervId"]) ? $_GET["supervId"] : "";
$admin = isset($_GET['es_admin']) ? $_GET['es_admin'] : "";
?>
<div class="navbar navbar-inverse navbar-fixed-top" role="navigation">
    <div class="container-fluid col-lg-12">
        <div class="navbar-header col-lg-2">
            <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
                <span class="sr-only">Toggle navigation</span>
            </button>
            <a class="navbar-brand" href="">
            </a>
        </div>
        <div class="navbar-collapse collapse">
            <ul class="nav navbar-nav navbar-right">
              <?php
              if($_GET['page'] == "Detalle_Campana") {
              ?>
                <li>
                    <a href="/Omnisup/index.php?page=Lista_Campanas&supervId=<?= $SupervId ?>&es_admin=<?= $admin ?>">Volver a Campañas
                    </a>
                </li>
              <?php
              }
              ?>
                <li>
                    <a href="https://<?= OMNI_HOST ?>">Volver a Principal
                   </a>
                </li>
            </ul>
            <ul class="nav navbar-nav">
                <!-- <li role="presentation" class="dropdown">
                    <a class="dropdown-toggle" data-toggle="dropdown" href="#" role="button" aria-expanded="false">
                        Usuarios <span class="caret"></span>
                    </a>
                    <ul class="dropdown-menu" role="menu">
                        <li>
                            <a href="https://<?= $_SERVER['SERVER_ADDR']; ?>/users/list/page1/">Usuarios</a>
                        </li>
                        <li>
                            <a href="https://<?= $_SERVER['SERVER_ADDR']; ?>/user/nuevo/">Crear Usuario</a>
                        </li>
                        <li class="divider"></li>
                        <li>
                            <a href="https://<?= $_SERVER['SERVER_ADDR']; ?>/agente/list/">Agentes</a>
                        </li>
                        <li class="divider"></li>
                        <li>
                            <a href="https://<?= $_SERVER['SERVER_ADDR']; ?>/grupo/list/">Grupos</a>
                        </li>
                        <li>
                            <a href="https://<?= $_SERVER['SERVER_ADDR']; ?>/grupo/nuevo/">Crear Grupo</a>
                        </li>
                    </ul>
                </li>
                <li role="presentation" class="dropdown">
                    <a class="dropdown-toggle" data-toggle="dropdown" href="#" role="button" aria-expanded="false">
                        Modulos <span class="caret"></span>
                    </a>
                    <ul class="dropdown-menu" role="menu">
                        <li>
                            <a href="https://<?= $_SERVER['SERVER_ADDR']; ?>/modulo/list/">Modulos</a>
                        </li>
                        <li>
                            <a href="https://<?= $_SERVER['SERVER_ADDR']; ?>/modulo/nuevo/">Habilitar Modulo</a>
                        </li>
                    </ul>
                </li>
                <li role="presentation" class="dropdown">
                    <a class="dropdown-toggle" data-toggle="dropdown" href="#" role="button" aria-expanded="false">
                        Campaña <span class="caret"></span>
                    </a>
                    <ul class="dropdown-menu" role="menu">
                        <li>
                            <a href="https://<?= $_SERVER['SERVER_ADDR']; ?>/campana/list/">Listado de campañas</a>
                        </li>
                        <li>
                            <a href="https://<?= $_SERVER['SERVER_ADDR']; ?>/campana/nuevo/">Crear nueva campaña</a>
                        </li>
                        <li>
                            <a href="https://<?= $_SERVER['SERVER_ADDR']; ?>/regenerar_asterisk/">Regenerar asterisk</a>
                        </li>
                        <li class="divider"></li>
                        <li>
                            <a href="https://<?= $_SERVER['SERVER_ADDR']; ?>/calificacion/list/">Listado de Calificaciones</a>
                        </li>
                        <li>
                            <a href="https://<?= $_SERVER['SERVER_ADDR']; ?>/calificacion/nuevo/">Nueva Calificacion</a>
                        </li>
                        <li>
                            <a href="https://<?= $_SERVER['SERVER_ADDR']; ?>/calificacion_campana/lista/">Grupo de calificaciones</a>
                        </li>
                        <li>
                            <a href="https://<?= $_SERVER['SERVER_ADDR']; ?>/calificacion_campana/nuevo/">Nuevo grupo de calificaciones</a>
                        </li>
                        <li class="divider"></li>
                        <li>
                            <a href="https://<?= $_SERVER['SERVER_ADDR']; ?>/formulario/nuevo/">Crear nuevo formulario</a>
                        </li>
                        <li>
                            <a href="https://<?= $_SERVER['SERVER_ADDR']; ?>/formulario/list/">Listado de formularios</a>
                        </li>
                    </ul>
                </li>
                <li role="presentation" class="dropdown">
                    <a class="dropdown-toggle" data-toggle="dropdown" href="#" role="button" aria-expanded="false">
                        Pausas <span class="caret"></span>
                    </a>
                    <ul class="dropdown-menu" role="menu">
                        <li>
                            <a href="https://<?= $_SERVER['SERVER_ADDR']; ?>/pausa/list/">Pausas</a>
                        </li>
                        <li>
                            <a href="https://<?= $_SERVER['SERVER_ADDR']; ?>/pausa/nuevo/">Crear nueva pausa</a>
                        </li>
                    </ul>
                </li>
                <li role="presentation" class="dropdown">
                    <a class="dropdown-toggle" data-toggle="dropdown" href="#" role="button" aria-expanded="false">
                        Contactos <span class="caret"></span>
                    </a>
                    <ul class="dropdown-menu" role="menu">
                        <li>
                            <a href="https://<?= $_SERVER['SERVER_ADDR']; ?>/base_datos_contacto/nueva/">Cargar nueva base de datos de contactos</a>
                        </li>
                        <li>
                            <a href="https://<?= $_SERVER['SERVER_ADDR']; ?>/base_datos_contacto/">Base de datos de contactos cargadas</a>
                        </li>
                    </ul>
                </li>
                <li>
                    <a href="https://<?= $_SERVER['SERVER_ADDR']; ?>/grabacion/buscar/1/">Buscar Grabación</a>
                </li>
                <li role="presentation" class="dropdown">
                    <a class="dropdown-toggle" data-toggle="dropdown" href="#" role="button" aria-expanded="false">
                        Reportes <span class="caret"></span>
                    </a>
                    <ul class="dropdown-menu" role="menu">
                        <li>
                            <a href="<?php echo $_SERVER['SERVER_ADDR'] ?>/reporte/llamadas/"><span class=" glyphicon glyphicon-earphone" aria-hidden="true"></span> Llamadas</a>
                        </li>
                        <li>
                            <a href="#"><span class="glyphicon glyphicon-envelope" aria-hidden="true"></span> SMS</a>
                        </li>
                        <li>
                            <a href="#"><span class="glyphicon glyphicon-erase" aria-hidden="true"></span> IM</a>
                        </li>
                    </ul>
                </li>
                <li role="presentation" class="dropdown">
                    <a class="dropdown-toggle" data-toggle="dropdown" href="#" role="button" aria-expanded="false">
                        Supervision <span class="caret"></span>
                    </a>
                    <ul class="dropdown-menu" role="menu">
                        <li>
                            <a href=""><span class=" glyphicon glyphicon-earphone" aria-hidden="true"></span> Llamadas Activas</a>
                        </li>
                        <li>
                            <a href="https://<?php echo $_SERVER['SERVER_ADDR'] ?>/Omnisup/index.php?page=Lista_Campanas"><span class=" glyphicon glyphicon-earphone" aria-hidden="true"></span> Campañas</a>
                        </li>
                        <li>
                            <a href="https://<?php echo $_SERVER['SERVER_ADDR'] ?>/Omnisup/index.php?page=Lista_Agentes"><span class=" glyphicon glyphicon-earphone" aria-hidden="true"></span> Agentes</a>
                        </li>
                    </ul>
                </li>-->
            </ul>
        </div>
    </div>
</div>
