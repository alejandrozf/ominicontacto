<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("globals.edit") }} {{ $tc("globals.external_site") }}</h1>
      </template>
      <template #end>
        <Button
          :label="$t('globals.back')"
          icon="pi pi-arrow-left"
          class="p-button-info mr-2"
          @click="backToExternalSitesList"
        />
      </template>
    </Toolbar>
    <Form :externalSite="externalSiteDetail" :formToCreate="false" />
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import Form from '@/components/external_sites/Form';

export default {
    inject: ['$helpers'],
    data () {
        return {
            externalSite: {
                nombre: '',
                url: '',
                metodo: '',
                disparador: '',
                formato: '',
                objetivo: ''
            }
        };
    },
    components: {
        Form
    },
    async created () {
        const id = this.$route.params.id;
        await this.initExternalSiteDetail(id);
    },
    methods: {
        ...mapActions(['initExternalSiteDetail']),
        backToExternalSitesList () {
            this.$router.push({ name: 'external_sites' });
        }
    },
    computed: {
        ...mapState(['externalSiteDetail'])
    }
};
</script>
