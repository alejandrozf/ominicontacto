<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("globals.new") }} {{ $tc("globals.external_site") }}</h1>
      </template>
      <template #end>
        <Button
          :label="$t('globals.back')"
          icon="pi pi-arrow-left"
          class="p-button-info mr-2"
          @click="backToExternalSitesList"
        />
      </template>
    </Toolbar>
    <Form />
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import Form from '@/components/external_sites/Form';

export default {
    inject: ['$helpers'],
    components: {
        Form
    },
    methods: {
        ...mapActions(['createPauseSet', 'initPauses']),
        backToExternalSitesList () {
            this.$router.push({ name: 'external_sites' });
        }
    }
};
</script>
