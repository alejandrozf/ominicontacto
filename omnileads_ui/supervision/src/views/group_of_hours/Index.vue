<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $tc("globals.group_of_hour", 2) }}</h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.new')"
          icon="pi pi-plus"
          @click="newOutboundRoute"
        />
      </template>
    </Toolbar>
    <GroupOfHoursTable :groupOfHours="groupOfHours" />
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import GroupOfHoursTable from '@/components/group_of_hours/GroupOfHoursTable';

export default {
    components: {
        GroupOfHoursTable
    },
    async created () {
        await this.initGroupOfHours();
    },
    methods: {
        newOutboundRoute () {
            this.$router.push({ name: 'group_of_hours_new' });
        },
        ...mapActions(['initGroupOfHours'])
    },
    computed: {
        ...mapState(['groupOfHours'])
    }
};
</script>
