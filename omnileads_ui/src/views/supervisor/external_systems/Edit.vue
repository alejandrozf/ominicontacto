<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("globals.edit") }} {{ $tc("globals.external_system") }}</h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.back')"
          icon="pi pi-arrow-left"
          class="p-button-info mr-2"
          @click="backToExternalSitiesList"
        />
      </template>
    </Toolbar>
    <Form :externalSystem="externalSystemDetail" :formToCreate="false" />
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import Form from '@/components/supervisor/external_systems/Form';

export default {
    components: {
        Form
    },
    async created () {
        const id = this.$route.params.id;
        await this.initExternalSystemDetail(id);
    },
    methods: {
        ...mapActions(['initExternalSystemDetail']),
        backToExternalSitiesList () {
            this.$router.push({ name: 'supervisor_external_systems' });
        }
    },
    computed: {
        ...mapState(['externalSystemDetail'])
    }
};
</script>
