<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("forms.inbound_route.new_inbound_route") }}</h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.back')"
          icon="pi pi-arrow-left"
          class="p-button-info mr-2"
          @click="backToInboundRoutesList"
        />
      </template>
    </Toolbar>
    <Form />
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import Form from '@/components/inbound_routes/Form';

export default {
    components: {
        Form
    },
    created () {
        this.initInboundRouteForm();
    },
    methods: {
        ...mapActions(['initInboundRouteForm']),
        backToInboundRoutesList () {
            this.$router.push({ name: 'inbound_routes' });
        }
    }
};
</script>
