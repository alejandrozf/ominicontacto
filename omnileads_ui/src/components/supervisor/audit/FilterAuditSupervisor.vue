<template>
  <Toolbar class="mb-4">
    <template #start>
      <Calendar
        id="date"
        v-model="dateStart"
        :manualInput="false"
        dateFormat="dd/mm/yy"
      />
    </template>
    <template #end>
      <Button
        :label="$t('globals.filter')"
        icon="pi pi-search"
        class="mr-2"
        @click="applyFilter"
        v-bind:disabled="loading"
      />
    </template>
  </Toolbar>
</template>
<script>
import { ref } from 'vue';
export default {
    emits: ['filterChange'],
    props: {
        loading: Boolean
    },
    setup (props, { emit }) {
        const dateStart = ref(new Date());
        const applyFilter = () => {
            if (dateStart.value) {
              emit('filterChange', {
                date_start: new Date(Date.UTC(dateStart.value.getFullYear(), dateStart.value.getMonth(), dateStart.value.getDate())).toISOString().slice(0, 10)
              });
            }
        };
        return {
            dateStart,
            applyFilter
        };
    }
};
</script>
