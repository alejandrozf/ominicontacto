<br>
<br>
<?php
include_once $_SERVER['DOCUMENT_ROOT'] . '/Omnisup/config.php';
include_once controllers . '/Campana.php';
$SupervId = isset($_GET["supervId"]) ? $_GET["supervId"] : "";
$admin = isset($_GET['es_admin']) ? $_GET['es_admin'] : "";
if($SupervId) {
    $Controller_Campana = new Campana();
    if($admin && $admin == 't') {
        $resul = $Controller_Campana->traerCampanas();
    } else {
        $resul = $Controller_Campana->traerCampanas($SupervId);
    }
}
?>
<div class="col-md-3 col-lg-offset-4">
    <table id="tableCamp" class="table table-striped table-condensed">
        <thead>
            <tr><th>Campañas</th></tr>
        </thead>
        <tbody>
            <?php
            foreach ($resul as $clave => $valor) {
            ?>
            <tr>
                <td style='color:green'><a href="index.php?page=Detalle_Campana&nomcamp=<?= $valor ?>&supervId=<?= $SupervId ?>&es_admin=<?= $admin ?>&campId=<?= $clave ?>"><?= $valor ?></a></td>
            </tr>
            <?php
            }
            ?>
        </tbody>
    </table>
</div>
