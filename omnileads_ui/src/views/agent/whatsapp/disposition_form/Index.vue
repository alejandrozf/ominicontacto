<template>
  <div>
    <Header @handleCloseEvent="closeEvent"/>
    <Tab ref="tabRef"/>
  </div>
</template>

<script>
import Header from '@/components/agent/whatsapp/disposition_form/Header';
import Tab from '@/components/agent/whatsapp/disposition_form/Tab';
import { mapActions } from 'vuex';
export default {
    components: {
        Header,
        Tab
    },
    methods: {
        ...mapActions(['agtWhatsManagementInitData']),
        closeEvent () {
            this.$refs.tabRef.closeEvent();
        }
    },
    created () {
        this.agtWhatsManagementInitData();
    }
};
</script>
