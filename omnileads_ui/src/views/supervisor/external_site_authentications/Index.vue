<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("views.external_site_authentication.list_title") }}</h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.new')"
          icon="pi pi-plus"
          class="p-button-success"
          @click="newExternalSiteAuthentication"
        />
      </template>
    </Toolbar>
    <ListTable
      :externalSiteAuthentications="externalSiteAuthentications"
      @showDetail="showDetail"
    />
    <ModalDetail
      :showModal="showModalDetail"
      :externalSiteAuthentication="externalSiteAuthentication"
      @handleModal="handleModal"
    />
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import ListTable from '@/components/supervisor/external_site_authentications/ListTable';
import ModalDetail from '@/components/supervisor/external_site_authentications/ModalDetail';

export default {
    data () {
        return {
            showModalDetail: false,
            externalSiteAuthentication: null
        };
    },
    components: {
        ListTable,
        ModalDetail
    },
    async created () {
        await this.initExternalSiteAuthentications();
    },
    methods: {
        showDetail (data) {
            this.externalSiteAuthentication = data;
            this.showModalDetail = true;
        },
        handleModal (show) {
            this.showModalDetail = show;
        },
        newExternalSiteAuthentication () {
            this.$router.push({ name: 'supervisor_external_site_authentications_new' });
        },
        ...mapActions(['initExternalSiteAuthentications'])
    },
    computed: {
        ...mapState(['externalSiteAuthentications'])
    }
};
</script>
