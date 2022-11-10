<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $tc("globals.ivr", 2) }}</h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.new')"
          icon="pi pi-plus"
          @click="newIVR"
        />
      </template>
    </Toolbar>
    <IVRsTable />
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import IVRsTable from '@/components/ivrs/IVRsTable';
export default {
    components: {
        IVRsTable
    },
    async created () {
        await this.initIVRs();
    },
    methods: {
        newIVR () {
            this.$router.push({ name: 'ivrs_new' });
        },
        ...mapActions(['initIVRs'])
    }
};
</script>
