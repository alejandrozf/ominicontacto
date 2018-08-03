#!/bin/bash

if [ "$VIRTUAL_ENV" = "" ] ; then
        echo "ERROR: virtualenv (o alguno de la flia.) no encontrado"
        exit 1
fi

Test() {
    apps=""
    sources=""
    tests=""
    if [ -z ${array[0]} ] && [ -z ${array[1]} ] && [ -z ${array[2]} ]; then
        echo "Tienes que ingresar una aplicacion como minimo"
        exit 1
    fi
    i=0
    cantidad_apps=${#array[@]}
    while [ $cantidad_apps -gt 0 ]; do
        if [ ! -z ${array[i]} ]; then
	    apps="${array[i]}/migrations/*,${array[i]}/tests/*,${array[i]}/tests/tests.py,$apps"
            sources=${array[i]},$sources
            tests=${array[i]} $tests
	fi
	cantidad_apps=`expr $cantidad_apps - 1`
        i=`expr $i + 1`

    done

    coverage run --omit="$apps" --source="$sources" manage.py test ${tests}
    coverage html -d /tmp/oml-coverity --title="Coverage para Omnileads"
    #which gnome-open > /dev/null 2> /dev/null && gnome-open /tmp/oml-coverity/index.html &
}

Help() {
  USAGE= "Script para correr tests unitarios y modulares del sistema \n
          Modo de uso: \n
            - ./run_covererage_tests.sh -t reportes_app,ominicontacto_app,etc..."
  echo -e $USAGE
}

while getopts ":t:h" OPTION;do
	case "${OPTION}" in
		t) #Test
		    set -f # disable glob
            	    IFS=',' # split on space characters
            	    array=($OPTARG) # use the split+glob operator
		    Test $array
		;;
		h) # Print the help option
			Help
		;;
	esac
done
if [ $# -eq 0  ]; then Help; fi
