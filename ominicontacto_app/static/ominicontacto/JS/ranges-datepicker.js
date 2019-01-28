function get_ranges(fecha_inicio) {
  var ranges = {};
  ranges[gettext('Hoy')] = [moment(), moment()];
  ranges[gettext('Ayer')] = [moment().subtract(1, 'days'), moment().subtract(1, 'days')];
  ranges[gettext('Últimos 7 Días')] = [moment().subtract(6, 'days'), moment()];
  ranges[gettext('Últimos 30 Días')] = [moment().subtract(29, 'days'), moment()];
  ranges[gettext('Este mes')] = [moment().startOf('month'), moment().endOf('month')];
  ranges[gettext('Último Mes')] = [moment().subtract(1, 'month').startOf('month'),
                                   moment().subtract(1, 'month').endOf('month')];
  if (fecha_inicio){
    ranges[gettext('Desde el inicio')] = [moment(fecha_inicio, "DD/MM/YYYY"), moment()];
  }
  return ranges;
}
