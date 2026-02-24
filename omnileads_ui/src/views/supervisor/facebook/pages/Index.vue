<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $tc("globals.facebook.page", 2) }}</h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.new')"
          icon="pi pi-plus"
          @click="newPage"
        />
      </template>
    </Toolbar>
    <PagesTable @handleModalEvent="handleModal" />
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import PagesTable from '@/components/supervisor/facebook/pages/PagesTable';

export default {
    data () {
        return {
            showModal: false,
            formToCreate: false
        };
    },
    components: {
        PagesTable
    },
    async created () {
        await this.initFacebookPages();
    },
    methods: {
        handleModal ({ showModal = false, formToCreate = false, page = null }) {
            this.showModal = showModal;
            this.formToCreate = formToCreate;
            this.initFacebookPage({ page });
        },
        newPage () {
            this.$router.push({ name: 'supervisor_facebook_pages_new_step1' });
        },
        ...mapActions(['initFacebookPage', 'initFacebookPages'])
    }
};
</script>
