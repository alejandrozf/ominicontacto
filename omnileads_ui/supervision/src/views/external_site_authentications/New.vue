<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("views.external_site_authentication.new_title") }}</h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.back')"
          icon="pi pi-arrow-left"
          class="p-button-info mr-2"
          @click="back"
        />
      </template>
    </Toolbar>
    <Form />
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import Form from '@/components/external_site_authentications/Form';

export default {
    inject: ['$helpers'],
    components: {
        Form
    },
    async created () {
        await this.initExternalSiteAuthentication();
    },
    methods: {
        ...mapActions(['initExternalSiteAuthentication']),
        back () {
            this.$router.push({ name: 'external_site_authentications' });
        }
    }
};
</script>
