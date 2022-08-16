<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $tc("globals.inbound_route", 2) }}</h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.new')"
          icon="pi pi-plus"
          @click="newInboundRoute"
        />
      </template>
    </Toolbar>
    <InboundRoutesTable :inboundRoutes="inboundRoutes" />
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import InboundRoutesTable from '@/components/inbound_routes/InboundRoutesTable';

export default {
    components: {
        InboundRoutesTable
    },
    async created () {
        await this.initInboundRoutes();
    },
    methods: {
        newInboundRoute () {
            this.$router.push({ name: 'inbound_routes_new' });
        },
        ...mapActions(['initInboundRoutes'])
    },
    computed: {
        ...mapState(['inboundRoutes'])
    }
};
</script>
