<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("views.call_dispositions.list_title") }}</h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.new')"
          icon="pi pi-plus"
          @click="newCallDisposition"
        />
      </template>
    </Toolbar>
    <ListTable
      :callDispositions="callDispositions"
      @handleModalEvent="handleModal"
    />
    <FormModal
      :showModal="showModal"
      :formToCreate="formToCreate"
      :formToAddSubdisposition="formToAddSubdisposition"
      :callDisposition="callDisposition"
      @handleModalEvent="handleModal"
    />
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import ListTable from '@/components/supervisor/call_dispositions/ListTable';
import FormModal from '@/components/supervisor/call_dispositions/FormModal';

export default {
    data () {
        return {
            formToCreate: true,
            showModal: false,
            callDisposition: { nombre: '' , subcalificaciones: []}
        };
    },
    components: {
        ListTable,
        FormModal
    },
    async created () {
        await this.initData();
    },
    methods: {
        handleModal ({ showModal, formToCreate, toAddSubcategory, callDisposition }) {
            this.formToCreate = formToCreate;
            this.formToAddSubdisposition = toAddSubcategory;
            this.showModal = showModal;
            this.callDisposition = callDisposition;
        },
        newCallDisposition () {
            this.showModal = true;
            this.formToCreate = true;
            this.callDisposition = { nombre: '', subcalificaciones: []};
        },
        async initData () {
            await this.initCallDispositions();
        },
        ...mapActions(['initCallDispositions'])
    },
    computed: {
        ...mapState(['callDispositions'])
    }
};
</script>
