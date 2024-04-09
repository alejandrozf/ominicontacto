<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("views.outbound_route.new_title") }}</h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.back')"
          icon="pi pi-arrow-left"
          class="p-button-info mr-2"
          @click="backToOutboundRoutesList"
        />
      </template>
    </Toolbar>
    <Form />
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import Form from '@/components/supervisor/outbound_routes/Form';

export default {
    components: {
        Form
    },
    created () {
        this.initOutboundRoute();
    },
    methods: {
        ...mapActions(['initOutboundRoute']),
        backToOutboundRoutesList () {
            this.$router.push({ name: 'supervisor_outbound_routes' });
        }
    }
};
</script>
