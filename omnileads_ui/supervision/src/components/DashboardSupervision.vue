<template>
    <DashboardSupervisionDetail v-if="reportData.data!=null"
        :reportData="reportData.data">
    </DashboardSupervisionDetail>
</template>
<script>
import { watch, ref } from 'vue';
import apiUrls from '@/const/api-urls';
import { apiCall } from '@/hooks/apiCall'
import DashboardSupervisionDetail from '@/components/DashboardSupervisionDetail'

export default {
    components: {
        DashboardSupervisionDetail,
    },
    setup() {
        const loadingData = ref(false);
        const reportData = ref({data:null});
        const {loading, response} = apiCall(apiUrls.DashboardSupervision)
            watch(loading, () => {
                loadingData.value = loading.value;
                reportData.value = response.value;
                  
            })

        return {
          loadingData,
          reportData
        }
        
    },
}
</script>
