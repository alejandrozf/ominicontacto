<template>
  <div class="card">
    <Toolbar class="p-mb-4">
      <template #start>
        <h1>
          {{
            $t("globals.external_system") + ": " + externalSystemDetail.nombre
          }}
        </h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.back')"
          icon="pi pi-arrow-left"
          class="p-button-info p-mr-2"
          @click="toExternalSystemsList"
        />
      </template>
    </Toolbar>
    <AgentsTable :agents="externalSystemDetail.agentes" :tableToShow="true" />
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import AgentsTable from '@/components/external_systems/AgentsTable';

export default {
    components: {
        AgentsTable
    },
    async created () {
        await this.initExternalSystemDetail(this.$route.params.id);
    },
    methods: {
        toExternalSystemsList () {
            this.$router.push({ name: 'external_systems' });
        },
        ...mapActions(['initExternalSystemDetail'])
    },
    computed: {
        ...mapState(['externalSystemDetail'])
    }
};
</script>
