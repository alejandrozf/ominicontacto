<template>
    <div>
        <div class="p-fluid p-formgrid p-grid">
            <div class="p-field p-col-4">
                <Calendar id="range" 
                    v-model="dateRange" 
                    selectionMode="range" 
                    :manualInput="false"
                    dateFormat="dd/mm/yy"    
                >
                </Calendar>
            </div>
            <div class="p-col-2">
                <Button label="Filtrar"  icon="pi pi-search" class="p-button-success p-mr-2" @click="applyFilter" />
            </div>
        </div>
    </div>
</template>
<script>
import Calendar from 'primevue/calendar';
import Button from 'primevue/button';

import { ref } from 'vue';
export default {
    emits: ["filterChange"],
    components: {
        Calendar,
        Button,
    },

    setup(props,{emit}) {

        const dateRange = ref([new Date(), new Date()])

        const applyFilter = () => {
            emit("filterChange", {
                date_start: dateRange.value[0].toISOString().slice(0, 10),
                date_end: dateRange.value[1].toISOString().slice(0, 10),
            });
        }
        return {
            dateRange,
            applyFilter
        }
    },
}
</script>
