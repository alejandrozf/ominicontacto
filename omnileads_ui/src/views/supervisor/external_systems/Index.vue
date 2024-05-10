<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $tc("globals.external_system", 2) }}</h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.new')"
          icon="pi pi-plus"
          @click="newExternalSystem"
        />
      </template>
    </Toolbar>
    <ExternalSystemsTable :externalSystems="externalSystems" />
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import ExternalSystemsTable from '@/components/supervisor/external_systems/ExternalSystemsTable';

export default {
    data () {
        return {
            showModalDetail: false,
            externalSystem: null
        };
    },
    components: {
        ExternalSystemsTable
    },
    async created () {
        await this.initExternalSystems();
    },
    methods: {
        newExternalSystem () {
            this.$router.push({ name: 'supervisor_external_systems_new' });
        },
        ...mapActions(['initExternalSystems'])
    },
    computed: {
        ...mapState(['externalSystems'])
    }
};
</script>
