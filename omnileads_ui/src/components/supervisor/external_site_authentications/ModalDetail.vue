<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '30vw' }"
    :closable="false"
    :modal="true"
  >
    <template #header>
      <h2>Autenticacion del sitio externo</h2>
    </template>
    <p>
      <b>{{ $t("models.external_site_authentication.name") }}: </b>
      {{ externalSiteAuthentication.nombre }}
    </p>
    <p>
      <b>{{ $t("models.external_site_authentication.url") }}: </b>
      {{ externalSiteAuthentication.url }}
    </p>
    <p>
      <b>{{ $t("models.external_site_authentication.username") }}: </b>
      {{ externalSiteAuthentication.username }}
    </p>
    <p>
      <b>{{ $t("models.external_site_authentication.campo_token") }}: </b>
      {{ externalSiteAuthentication.campo_token ? externalSiteAuthentication.campo_token : '-----' }}
    </p>
    <p>
      <b>{{ $t("models.external_site_authentication.token") }}: </b>
      {{ externalSiteAuthentication.token ? externalSiteAuthentication.token : '-----' }}
    </p>
    <p>
      <b>{{ $t("models.external_site_authentication.expiracion_token") }}: </b>
      {{ externalSiteAuthentication.expiracion_token? this.$helpers.formatTime(externalSiteAuthentication.expiracion_token) : '-----' }}
    </p>
    <p>
      <b>{{ $t("models.external_site_authentication.campo_duracion") }}: </b>
      {{ externalSiteAuthentication.campo_duracion ? externalSiteAuthentication.campo_duracion : '-----' }}
    </p>
    <p>
      <b>{{ $t("models.external_site_authentication.duracion") }}: </b>
      {{ externalSiteAuthentication.duracion ? this.$helpers.formatTime(externalSiteAuthentication.duracion) : '-----'}}
    </p>
    <template #footer>
      <Button label="ok" @click="closeModal" />
    </template>
  </Dialog>
</template>

<script>
export default {
    inject: ['$helpers'],
    props: {
        showModal: {
            type: Boolean,
            default: false
        },
        externalSiteAuthentication: {
            type: Object,
            default: () => {}
        }
    },
    methods: {
        closeModal () {
            this.$emit('handleModal', false);
        }
    }
};
</script>
