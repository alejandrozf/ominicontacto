<template>
  <div class="card">
    <Toolbar class="p-mb-4">
      <template #start>
        <h1>{{ $t("globals.new") }} {{ $tc("globals.external_site") }}</h1>
      </template>
      <template #end>
        <Button
          :label="
            $tc('globals.back_to', { type: $tc('globals.external_site', 2) })
          "
          icon="pi pi-arrow-left"
          class="p-button-info p-mr-2"
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
