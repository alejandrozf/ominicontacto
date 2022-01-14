<template>
    <Card>
        <template #title>
            Auditoría Administrativa
        </template>
        <template #content>
            <FilterAuditSupervisor @filterChange="loadData"></FilterAuditSupervisor>
            <DataTableAuditSupervisor :tableData="tableData.data" :loading="loadingData"></DataTableAuditSupervisor>
        </template>
    </Card>
</template>
<script>
import { reactive, toRefs, watch, ref } from 'vue';
import apiUrls from '@/const/api-urls';
import { apiCall, httpMethods } from '@/hooks/apiCall'
import DataTableAuditSupervisor from '@/components/DataTableAuditSupervisor'
import FilterAuditSupervisor from '@/components/FilterAuditSupervisor'
import Card from 'primevue/card';
export default {
    components: {
        DataTableAuditSupervisor,
        FilterAuditSupervisor,
        Card
    },
    setup() {
        const loadingData = ref(false);
        const tableData = ref({data:null});

        const {loading, response} = apiCall(apiUrls.AuditSupervisor)
                watch(loading, () => {
                    loadingData.value = loading.value;
                    tableData.value = response.value;
        });

    
        const state = reactive({
            loadData: (data) => {
                const params = {...data}
                const {loading, response} = apiCall(apiUrls.AuditSupervisor, httpMethods.POST, params)
                watch(loading, () => {
                    loadingData.value = loading.value;
                    tableData.value = response.value;
                })
            }
        });
        return {
          ...toRefs(state),
          loadingData,
          tableData
        }
        
    },

}
</script>
