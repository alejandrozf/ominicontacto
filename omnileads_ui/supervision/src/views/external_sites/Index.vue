<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("views.external_sites.list_title") }}</h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.new')"
          icon="pi pi-plus"
          class="p-button-success"
          @click="newExternalSite"
        />
      </template>
    </Toolbar>
    <ExternalSitesTable
      :externalSites="externalSites"
      @showDetail="showDetail"
    />
    <ModalDetail
      :showModal="showModalDetail"
      :externalSite="externalSite"
      @handleModal="handleModal"
    />
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import ExternalSitesTable from '@/components/external_sites/ExternalSitesTable';
import ModalDetail from '@/components/external_sites/ModalDetail';

export default {
    data () {
        return {
            showModalDetail: false,
            externalSite: null
        };
    },
    components: {
        ExternalSitesTable,
        ModalDetail
    },
    async created () {
        await this.initData();
    },
    methods: {
        showDetail (data) {
            this.externalSite = data;
            this.showModalDetail = true;
        },
        handleModal (show) {
            this.showModalDetail = show;
        },
        newExternalSite () {
            this.$router.push({ name: 'external_sites_new' });
        },
        async initData () {
            await this.initExternalSites();
        },
        ...mapActions(['initExternalSites'])
    },
    computed: {
        ...mapState(['externalSites'])
    }
};
</script>
