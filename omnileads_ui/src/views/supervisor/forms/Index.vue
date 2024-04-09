<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $tc("globals.form", 2) }}</h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.new')"
          icon="pi pi-plus"
          @click="newForm"
        />
      </template>
    </Toolbar>
    <FormsTable :forms="forms" />
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import FormsTable from '@/components/supervisor/forms/FormsTable';

export default {
    components: {
        FormsTable
    },
    async created () {
        await this.initForms();
    },
    methods: {
        newForm () {
            this.$router.push({ name: 'supervisor_forms_new_step1' });
        },
        ...mapActions(['initForms'])
    },
    computed: {
        ...mapState(['forms'])
    }
};
</script>
