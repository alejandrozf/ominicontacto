<template>
  <div class="card">
    <Toolbar class="p-mb-4">
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
    <GroupsTable
      :pauseSets="pauseSets"
      @editGroupEvent="editGroup"
    ></GroupsTable>
    <EditGroup
      :showModal="showModalEdit"
      :group="group"
      @handleModal="handleEditModal"
      @initDataEvent="initData"
    ></EditGroup>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import GroupsTable from '@/components/pause_sets/GroupsTable';
import EditGroup from '@/components/pause_sets/forms/EditGroup';

export default {
    data () {
        return {
            showModalEdit: false,
            group: {}
        };
    },
    components: {
        GroupsTable,
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
