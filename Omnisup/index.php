<!DOCTYPE html>
<html lang="es">
    <head>
        <meta charset="UTF-8">
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"/>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous">
        <link rel="stylesheet" type="text/css" href="static/Css/jquery.dataTables.min.css"/>
        <link rel="stylesheet" type="text/css" href="static/Css/phone.css"/>
        <link rel="stylesheet" type="text/css" href="static/Css/main.css"/>
        <title>OmniLeads</title>
    </head>
    <body>
        <script type="text/javascript" src="static/Js/config.js"></script>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
        <script src = "https://ajax.googleapis.com/ajax/libs/angularjs/1.2.15/angular.min.js"></script>
        <script type="text/javascript" src="static/Js/jquery.dataTables.min.js"></script>
        <script type="text/javascript" src="static/Js/jssip.js"></script>
        <script type="text/javascript" src="static/Js/phone.js"></script>
        <script type="text/javascript" src="static/Js/tables.js"></script>
        <div class="container-fluid">
            <?php include 'View/Navbar.php' ?>
            <br/>
            <div class="row-fluid">
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
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
    </body>
</html>
