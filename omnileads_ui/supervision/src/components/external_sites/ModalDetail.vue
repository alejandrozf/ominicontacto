<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '30vw' }"
    :closable="false"
    :modal="false"
  >
    <template #header>
      <h2>Informacion del sitio externo</h2>
    </template>
    <p>
      <b>{{ $t("models.external_site.name") }}: </b>
      {{ externalSite.nombre }}
    </p>
    <p>
      <b>{{ $t("models.external_site.url") }}: </b>
      {{ externalSite.url }}
    </p>
    <p>
      <b>{{ $t("models.external_site.method") }}: </b>
      {{ getMethod(externalSite.metodo) }}
    </p>
    <p>
      <b>{{ $t("models.external_site.trigger") }}: </b>
      {{ getTigger(externalSite.disparador) }}
    </p>
    <p>
      <b>{{ $t("models.external_site.format") }}: </b>
      {{ getFormat(externalSite.formato) }}
    </p>
    <p>
      <b>{{ $t("models.external_site.objective") }}: </b>
      {{ getObjective(externalSite.objetivo) }}
    </p>
    <p>
      <b>{{ $t("models.external_site.status") }}: </b>
      {{ getStatus(externalSite.oculto) }}
    </p>
    <template #footer>
      <Button label="ok" @click="closeModal" />
    </template>
  </Dialog>
</template>

<script>
export default {
    props: {
        showModal: {
            type: Boolean,
            default: false
        },
        externalSite: {
            type: Object,
            default: function () {
                return {
                    name: '',
                    url: '',
                    disparador: 0,
                    metodo: 0,
                    objetivo: 0,
                    formato: 0
                };
            }
        }
    },
    methods: {
        closeModal () {
            this.$emit('handleModal', false);
        },
        getMethod (option) {
            if (option === 1) {
                return 'GET';
            } else {
                return 'POST';
            }
        },
        getObjective (option) {
            if (option === 1) {
                return 'Embebido';
            } else {
                return 'Nueva pestana';
            }
        },
        getStatus (option) {
            if (option) {
                return 'Inactivo';
            } else {
                return 'Activo';
            }
        },
        getTigger (option) {
            if (option === 1) {
                return 'Agente';
            } else if (option === 2) {
                return 'Automatico';
            } else if (option === 3) {
                return 'Servidor';
            } else if (option === 4) {
                return 'Calificacion';
            }
        },
        getFormat (option) {
            if (option === 1) {
                return 'Multipart / FormData';
            } else if (option === 2) {
                return 'WWW Form Urlencoded';
            } else if (option === 3) {
                return 'Texto Plano';
            } else if (option === 4) {
                return 'Json';
            }
        }
    }
};
</script>
