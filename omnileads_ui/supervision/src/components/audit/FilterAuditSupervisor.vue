<template>
  <Toolbar class="p-mb-4">
    <template #start>
      <Calendar
        id="range"
        v-model="dateRange"
        selectionMode="range"
        :manualInput="false"
        dateFormat="dd/mm/yy"
      />
    </template>
    <template #end>
      <Button
        :label="$t('globals.filter')"
        icon="pi pi-search"
        class="p-button-success p-mr-2"
        @click="applyFilter"
      />
    </template>
  </Toolbar>
</template>
<script>
import { ref } from 'vue';
export default {
    emits: ['filterChange'],
    setup (props, { emit }) {
        const dateRange = ref([new Date(), new Date()]);

        const applyFilter = () => {
            emit('filterChange', {
                date_start: dateRange.value[0].toISOString().slice(0, 10),
                date_end: dateRange.value[1].toISOString().slice(0, 10)
            });
        };
        return {
            dateRange,
            applyFilter
        };
    }
};
</script>
