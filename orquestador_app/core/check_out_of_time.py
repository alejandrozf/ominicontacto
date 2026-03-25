# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#
def _matches_start(current, start):
    return start is None or start <= current


def _matches_end(current, end):
    return end is None or end >= current


def _matches_validation(validacion, time, weekday, monthday, month):
    return (
        _matches_start(time, validacion.tiempo_inicial) and
        _matches_end(time, validacion.tiempo_final) and
        _matches_start(weekday, validacion.dia_semana_inicial) and
        _matches_end(weekday, validacion.dia_semana_final) and
        _matches_start(monthday, validacion.dia_mes_inicio) and
        _matches_end(monthday, validacion.dia_mes_final) and
        _matches_start(month, validacion.mes_inicio) and
        _matches_end(month, validacion.mes_final)
    )


def is_out_of_time(obj, timestamp):
    if not obj.horario:
        return False

    time = timestamp.time()
    weekday = timestamp.weekday()
    monthday = timestamp.day
    month = timestamp.month
    validaciones_tiempo = obj.horario.validaciones_tiempo.all()

    for validacion in validaciones_tiempo:
        if _matches_validation(validacion, time, weekday, monthday, month):
            return False

    return validaciones_tiempo.exists()
