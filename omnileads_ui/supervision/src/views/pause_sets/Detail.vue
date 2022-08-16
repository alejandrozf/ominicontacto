<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("globals.pause_set_info", { name: setName }) }}</h1>
      </template>
      <template #end>
        <Button
          :label="$t('globals.back')"
          icon="pi pi-arrow-left"
          class="p-button-info mr-2"
          @click="backToPauseSetsList"
        />
      </template>
    </Toolbar>
    <br />
    <hr class="mt-4" />
    <h2>{{ $t("views.pause_sets.configured_pauses") }}</h2>
    <PauseConfigurationsTable
      :pausas="pauseSetDetail.pausas"
      @editPauseConfigEvent="editPauseConfig"
      @handleModal="handleModalNewPause"
      @initDataEvent="initData"
    />
    <EditPause
      :showModal="showModal"
      :pauseConfig="pauseConfig"
      @handleModal="handleModal"
      @initDataEvent="initData"
    />
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
import PauseConfigurationsTable from '@/components/pause_sets/PauseConfigurationsTable';
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
        PauseConfigurationsTable,
        EditPause,
        NewConfigPauseDetail
    },
    async created () {
        await this.initData();
    },
    methods: {
        ...mapActions(['initPauseSetDetail', 'initActivePauses']),
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
            await this.initActivePauses();
            await this.initPauseSetDetail(idPauseSet);
            this.setName = this.pauseSetDetail.conjunto.nombre;
        }
    },
    computed: {
        ...mapState(['pauseSetDetail', 'activePauses']),
        filterPauses () {
            const pauses = this.activePauses.filter(
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
