<template>
  <div class="card">
    <Toolbar class="p-mb-4">
      <template #start>
        <h1>{{ $t("globals.pause_set_info", { name: setName }) }}</h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.back_to', { type: $t('globals.pause_set') })"
          icon="pi pi-arrow-left"
          class="p-button-info p-mr-2"
          @click="backToPauseSetsList"
        />
      </template>
    </Toolbar>
    <br />
    <hr class="p-mt-4" />
    <h2>{{ $t("views.pause_sets.configured_pauses") }}</h2>
    <PausesTable
      :pausas="pauseSetDetail.pausas"
      @editPauseConfigEvent="editPauseConfig"
      @handleModal="handleModalNewPause"
      @initDataEvent="initData"
    ></PausesTable>
    <EditPause
      :showModal="showModal"
      :pauseConfig="pauseConfig"
      @handleModal="handleModal"
      @initDataEvent="initData"
    ></EditPause>
    <NewConfigPauseDetail
      :showModal="showModalNewPause"
      :pauses="filterPauses"
      @handleModal="handleModalNewPause"
      @initDataEvent="initData"
      @filterPausesEvent="changePauseType"
    ></NewConfigPauseDetail>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import PausesTable from '@/components/pause_sets/PausesTable';
import EditPause from '@/components/pause_sets/forms/EditPause';
import NewConfigPauseDetail from '@/components/pause_sets/forms/NewConfigPauseDetail';

export default {
    data () {
        return {
            showModal: false,
            showModalNewPause: false,
            pauseConfig: {},
            pausesTypeSelected: 1,
            setName: ''
        };
    },
    components: {
        PausesTable,
        EditPause,
        NewConfigPauseDetail
    },
    async created () {
        await this.initData();
    },
    methods: {
        ...mapActions(['initPauseSetDetail', 'initPauses']),
        backToPauseSetsList () {
            this.$router.push({ name: 'pause_sets' });
        },
        editPauseConfig (pauseConfig) {
            this.pauseConfig = pauseConfig;
            this.showModal = true;
        },
        handleModal (show) {
            this.showModal = show;
        },
        handleModalNewPause (show) {
            this.showModalNewPause = show;
        },
        changePauseType (type) {
            this.pausesTypeSelected = type;
        },
        async initData () {
            const idPauseSet = this.$route.params.id;
            await this.initPauses();
            await this.initPauseSetDetail(idPauseSet);
            this.setName = this.pauseSetDetail.conjunto.nombre;
        }
    },
    computed: {
        ...mapState(['pauseSetDetail', 'pauses']),
        filterPauses () {
            const pauses = this.pauses.filter(
                (p) => p.es_productiva === (this.pausesTypeSelected === 1)
            );
            if (this.pauseSetDetail.pausas !== undefined) {
                if (this.pauseSetDetail.pausas.length > 0) {
                    const groupPausesId = this.pauseSetDetail.pausas.map(
                        (p) => p.pause_id
                    );
                    return pauses.filter((p) => !groupPausesId.includes(p.id));
                }
            }
            return pauses;
        }
    }
};
</script>
