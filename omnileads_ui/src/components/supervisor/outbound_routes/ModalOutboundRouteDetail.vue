<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '50vw' }"
    :closable="false"
    :modal="false"
  >
    <template #header>
      <h1>{{ $t("views.outbound_route.detail_title") }}</h1>
    </template>
    <div class="card">
      <div class="grid">
        <div class="field col-12">
          <ul>
            <li class='mb-2'>
              <b>{{ $t('models.outbound_route.name') }}: </b> {{outboundRoute.nombre}}
            </li>
            <li class='mb-2'>
              <b>{{ $t('models.outbound_route.ring_time') }}: </b> {{outboundRoute.ring_time}} {{ $tc('globals.second', 2) }}
            </li>
            <li>
              <b>{{ $t('models.outbound_route.dial_options') }}: </b> {{outboundRoute.dial_options}}
            </li>
          </ul>
        </div>
        <div class="field col-12">
          <h2>{{ $tc('globals.dial_pattern', 2) }}</h2>
          <DialPatternsTable
            :dialPatterns="outboundRoute.patrones_de_discado"
            :showOptions="false"
          />
        </div>
        <div class="field col-12">
          <h2>{{ $tc('globals.trunk', 2) }}</h2>
          <SipTrunksTable
            :trunks="filteredTrunks"
            :showOptions="false"
          />
        </div>
      </div>
    </div>
    <template #footer>
      <div class="flex justify-content-end flex-wrap">
        <Button
          class="p-button-info"
          :label="$t('globals.close')"
          @click="closeModal"
        />
      </div>
    </template>
  </Dialog>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import DialPatternsTable from '@/components/supervisor/outbound_routes/DialPatternsTable';
import SipTrunksTable from '@/components/supervisor/outbound_routes/SipTrunksTable';

export default {
    components: {
        DialPatternsTable,
        SipTrunksTable
    },
    data () {
        return {
            filteredTrunks: []
        };
    },
    props: {
        showModal: {
            type: Boolean,
            default: false
        },
        outboundRoute: {
            type: Object,
            default: () => {}
        }
    },
    computed: {
        ...mapState(['sipTrunks'])
    },
    async created () {
        await this.initOutboundRouteSipTrunks();
    },
    methods: {
        ...mapActions(['initOutboundRouteSipTrunks']),
        closeModal () {
            this.$emit('handleModalDetailEvent', false);
        },
        filterTrunks () {
            if (this.outboundRoute.troncales) {
                const ids = this.outboundRoute.troncales.map(t => t.troncal);
                this.filteredTrunks = this.sipTrunks.filter(t => ids.includes(t.id));
            }
        }
    },
    watch: {
        outboundRoute: {
            handler () {
                this.filterTrunks();
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
