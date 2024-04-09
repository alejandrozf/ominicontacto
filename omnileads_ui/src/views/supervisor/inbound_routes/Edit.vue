<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("forms.inbound_route.edit_inbound_route") }}</h1>
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
    <Form :inboundRoute="inboundRouteDetail" :formToCreate="false" />
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import Form from '@/components/supervisor/inbound_routes/Form';

export default {
    components: {
        Form
    },
    async created () {
        const id = this.$route.params.id;
        await this.initInboundRouteDetail(id);
        await this.initInboundRouteForm(this.inboundRouteDetail);
    },
    methods: {
        ...mapActions(['initInboundRouteDetail', 'initInboundRouteForm']),
        backToInboundRoutesList () {
            this.$router.push({ name: 'supervisor_inbound_routes' });
        }
    },
    computed: {
        ...mapState(['inboundRouteDetail'])
    }
};
</script>
