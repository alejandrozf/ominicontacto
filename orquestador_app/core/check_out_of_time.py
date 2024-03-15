# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#


def is_out_of_time(line, timestamp):
    if line.horario:
        time = timestamp.time()
        weekday = timestamp.weekday()
        monthday = timestamp.day
        month = timestamp.month
        print(time, weekday, monthday, month)
        validaciones_tiempo = line.horario.validaciones_tiempo.all()
        for validacion in validaciones_tiempo:
            print(validacion.dia_semana_final)
            if validacion.tiempo_inicial is not None and validacion.tiempo_inicial > time:
                return True
            if validacion.tiempo_final is not None and validacion.tiempo_final < time:
                return True
            if validacion.dia_semana_inicial is not None and\
               validacion.dia_semana_inicial > weekday:
                return True
            if validacion.dia_semana_final is not None and validacion.dia_semana_final < weekday:
                return True
            if validacion.dia_mes_inicio is not None and validacion.dia_mes_inicio > monthday:
                return True
            if validacion.dia_mes_final is not None and validacion.dia_mes_final < monthday:
                return True
            if validacion.mes_inicio is not None and validacion.mes_inicio > month:
                return True
            if validacion.mes_final is not None and validacion.mes_final < month:
                return True
    return False
