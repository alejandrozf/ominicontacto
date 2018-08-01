<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>OmniLeads</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <!-- Stylesheets -->
    <link rel="stylesheet" href="/static/bootstrap-4.0.0/css/bootstrap.min.css" >
    <!-- <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"/> -->
    <link rel="stylesheet" type="text/css" href="static/Css/jquery.dataTables.min.css"/>
    <link rel="stylesheet" type="text/css" href="static/Css/phone.css"/>
    <link rel="stylesheet" type="text/css" href="static/Css/main.css"/>
    <!-- Custom CSS -->
    <link rel="stylesheet" href="/static/ominicontacto/CSS/admin.css">
    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css?family=Asap:400,500" rel="stylesheet">
    <link rel="stylesheet" href="/static/ominicontacto/CSS/fa-solid.css">
    <link rel="stylesheet" href="/static/ominicontacto/CSS/fa-regular.css">
    <link rel="stylesheet" href="/static/ominicontacto/CSS/fontawesome.css">
    <link rel="stylesheet" href="/static/ominicontacto/CSS/oml-icons.css">
    <!-- jquery -->
    <script src="/static/jquery-2.2.4.min.js"></script>
    <!-- <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script> -->
    <script src = "https://ajax.googleapis.com/ajax/libs/angularjs/1.2.15/angular.min.js"></script>
    <!-- Scripts -->
    <script type="text/javascript" src="static/Js/config.js"></script>
    <script type="text/javascript" src="static/Js/jquery.dataTables.min.js"></script>
    <script type="text/javascript" src="static/Js/jssip.js"></script>
    <script type="text/javascript" src="static/Js/phone.js"></script>
    <script type="text/javascript" src="static/Js/tables.js"></script>
    <!-- Bootstrap -->
    <script src="/static/bootstrap-4.0.0/js/bootstrap.bundle.min.js"></script>
    <!-- <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script> -->
</head>
<body>
    <?php /*
    <?php include 'View/Navbar.php' ?>
    */ ?>
    <div class="wrapper-main">
        <nav id="sidebar">
            <div class="sidebar-header">
                <a href="#">
                    <img id="nav-logo" src="/static/ominicontacto/Img/ic_logo.svg">
                    <img id="nav-logo-symbol" src="/static/ominicontacto/Img/ic_logo_symbol.svg">
                </a>
            </div>
            <ul id="nav-main-menu" class="list-unstyled">
                <li class="main-menu-li">
                    <span class="icon icon-chevron-left"></span>
                    <a class="menu-link" href="https://<?= OMNI_HOST ?>">Volver</a>
                </li>
                <li class="main-menu-li">
                    <span class="icon icon-campaign"></span>
                    <a class="menu-header" aria-expanded="true">Campañas</a>
                    <ul class="list-unstyled submenu" id="menuCampaigns">
                        <li>
                            <a href="">Campaña 1</a>
                        </li>
                        <li>
                            <a href="">Campaña 2</a>
                        </li>
                        <li>
                            <a href="">Campaña 3</a>
                        </li>
                    </ul>
                </li>
            </ul>
        </nav>
        <div class="wrapper-content">
            <div id="topbar">
                <div class="nav">
                    <button type="button" id="sidebarCollapse" class="btn">
                        <span class="fas fa-bars"></span>
                    </button>
                    <div id="nav-user">
                        <div class="dropdown">
                            <button class="btn btn-light dropdown-toggle" type="button" id="dropdownUser" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                            <span class="icon icon-user"></span>
                            </button>
                            <div class="dropdown-menu dropdown-menu-right" aria-labelledby="dropdownUser">
                                <a class="dropdown-item" href="">Salir</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="wrapper-info">
                <?php
                session_start();
                include('helpers/path_helper.php');
                /* if (isset($_SESSION["Usuario"])) {
                  $_SESSION['REMOTE_ADDR'] = $_SERVER['REMOTE_ADDR'];
                  $_SESSION['HTTP_USER_AGENT'] = $_SERVER['HTTP_USER_AGENT']; */
                include obtenerPath();
                //}
                ?>
            </div>
        </div>
    </div>

    <script type="text/javascript">
    $(document).ready(function () {

        /* Toggle */
        $('#sidebarCollapse').on('click',function(){
            $('#sidebar').toggleClass('active');
        });

        // Get current window path
        currentPath = window.location.pathname;

        // Add active class to current selected anchor
        $("a[href='" + currentPath + "']").addClass("active");

        // Expand sidebar first level submenus for current selected anchor
        $("a[href='" + currentPath + "']").closest('ul .submenu').collapse('show');

        // Add active class to sidebar icon
        $("a[href='" + currentPath + "']").closest('.main-menu-li').find('.icon').addClass('active');

    });
    </script>

</body>
</html>
