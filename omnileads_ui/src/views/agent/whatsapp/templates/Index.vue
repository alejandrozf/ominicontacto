<template>
  <div>
    <Header @handleClearFiltersEvent="clearFiltersEvent" />
    <Table ref="tableRef" />
  </div>
</template>

<script>
import Header from '@/components/agent/whatsapp/templates/Header';
import Table from '@/components/agent/whatsapp/templates/Table';
import { mapState } from 'vuex';
export default {
    components: {
        Header,
        Table
    },
    computed: {
        ...mapState(['agtWhatsMessages'])
    },
    data () {
        return {
            newMessages: [],
            answeredMessages: []
        };
    },
    methods: {
        clearFiltersEvent () {
            this.$refs.tableRef.clearFilter();
        }
    },
    watch: {
        agtWhatsMessages: {
            handler () {
                this.newMessages = this.agtWhatsMessages.filter(
                    (m) => m.isNew === true
                );
                this.answeredMessages = this.agtWhatsMessages.filter(
                    (m) => m.isNew === false
                );
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
