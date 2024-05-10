<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("views.audit.title") }}</h1>
      </template>
    </Toolbar>
    <FilterAuditSupervisor @filterChange="loadData"></FilterAuditSupervisor>
    <DataTableAuditSupervisor
      :tableData="tableData.data"
      :loading="loadingData"
    ></DataTableAuditSupervisor>
  </div>
</template>
<script>
import { reactive, toRefs, watch, ref } from 'vue';
import apiUrls from '@/api_urls/supervisor';
import { apiCall, httpMethods } from '@/hooks/apiCall';
import DataTableAuditSupervisor from '@/components/supervisor/audit/DataTableAuditSupervisor';
import FilterAuditSupervisor from '@/components/supervisor/audit/FilterAuditSupervisor';
export default {
    components: {
        DataTableAuditSupervisor,
        FilterAuditSupervisor
    },
    setup () {
        const loadingData = ref(false);
        const tableData = ref({ data: null });

        const { loading, response } = apiCall(apiUrls.AuditSupervisor);
        watch(loading, () => {
            loadingData.value = loading.value;
            tableData.value = response.value;
        });

        const state = reactive({
            loadData: (data) => {
                const params = { ...data };
                const { loading, response } = apiCall(
                    apiUrls.AuditSupervisor,
                    httpMethods.POST,
                    params
                );
                watch(loading, () => {
                    loadingData.value = loading.value;
                    tableData.value = response.value;
                });
            }
        });
        return {
            ...toRefs(state),
            loadingData,
            tableData
        };
    }
};
</script>
