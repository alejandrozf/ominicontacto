<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("globals.new") }} {{ $tc("globals.external_system") }}</h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.back')"
          icon="pi pi-arrow-left"
          class="p-button-info mr-2"
          @click="backToExternalSystemsList"
        />
      </template>
    </Toolbar>
    <Form />
  </div>
</template>

<script>
import Form from '@/components/supervisor/external_systems/Form';

export default {
    components: {
        Form
    },
    methods: {
        backToExternalSystemsList () {
            this.$router.push({ name: 'supervisor_external_systems' });
        }
    }
};
</script>
