<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("views.pause_sets.title") }}</h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.new')"
          icon="pi pi-plus"
          @click="newPauseGroup"
        />
      </template>
    </Toolbar>
    <PauseSetsTable
      :pauseSets="pauseSets"
      @editGroupEvent="editGroup"
    />
    <EditGroup
      :showModal="showModalEdit"
      :group="group"
      @handleModal="handleEditModal"
      @initDataEvent="initData"
    />
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import PauseSetsTable from '@/components/pause_sets/PauseSetsTable';
import EditGroup from '@/components/pause_sets/forms/EditGroup';

export default {
    data () {
        return {
            showModalEdit: false,
            group: {}
        };
    },
    components: {
        PauseSetsTable,
        EditGroup
    },
    async created () {
        await this.initData();
    },
    methods: {
        editGroup (group) {
            this.group = group;
            this.showModalEdit = true;
        },
        newPauseGroup () {
            this.$router.push({ name: 'pause_sets_new' });
        },
        handleEditModal (show) {
            this.showModalEdit = show;
        },
        async initData () {
            await this.initPauseSets();
            await this.initPauses();
        },
        ...mapActions(['initPauseSets', 'initPauses'])
    },
    computed: {
        ...mapState(['pauseSets', 'pauses'])
    }
};
</script>
