<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $tc("globals.pause", 2) }}</h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.new')"
          icon="pi pi-plus"
          @click="newPause"
        />
      </template>
    </Toolbar>
    <PausesTable :pauses="pauses" @handleModalEvent="handleModal"/>
    <ModalForm
      :pauses="pauses"
      :showModal="showModal"
      :formToCreate='formToCreate'
      @handleModalEvent="handleModal"
    />
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import PausesTable from '@/components/supervisor/pauses/PausesTable';
import ModalForm from '@/components/supervisor/pauses/ModalForm';

export default {
    components: {
        PausesTable,
        ModalForm
    },
    data () {
        return {
            showModal: false,
            formToCreate: false
        };
    },
    async created () {
        await this.initPauses();
    },
    methods: {
        ...mapActions(['initPauses', 'initPauseForm']),
        newPause () {
            this.showModal = true;
            this.formToCreate = true;
            this.initPauseForm();
        },
        handleModal ({ showModal, formToCreate, pause }) {
            this.showModal = showModal;
            this.formToCreate = formToCreate;
            this.initPauseForm(formToCreate === true ? null : pause);
        }
    },
    computed: {
        ...mapState(['pauses'])
    }
};
</script>
