<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $tc("globals.outbound_route", 2) }}</h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.new')"
          icon="pi pi-plus"
          @click="newOutboundRoute"
        />
      </template>
    </Toolbar>
    <OutboundRoutesTable :outboundRoutes="outboundRoutes" />
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import OutboundRoutesTable from '@/components/outbound_routes/OutboundRoutesTable';

export default {
    components: {
        OutboundRoutesTable
    },
    async created () {
        await this.initOutboundRoutes();
    },
    methods: {
        newOutboundRoute () {
            this.$router.push({ name: 'outbound_routes_new' });
        },
        ...mapActions(['initOutboundRoutes'])
    },
    computed: {
        ...mapState(['outboundRoutes'])
    }
};
</script>
