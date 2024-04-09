<template>
  <div class="grid">
    <div class="col-12">
      <RegistrationForm
        v-if="!registerServerStatus"
      />
      <CardInfo v-else />
    </div>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import RegistrationForm from '@/components/supervisor/register_server/Form';
import CardInfo from '@/components/supervisor/register_server/Info';

export default {
    data () {
        return {
            formToCreate: true
        };
    },
    components: {
        RegistrationForm,
        CardInfo
    },
    async created () {
        const element = window.parent.document.getElementById(
            'registerPopUpIsAdmin'
        );
        const isAdmin = element.value;
        await this.initRegisterServer(isAdmin === 'True');
    },
    computed: {
        ...mapState(['registerServerStatus'])
    },
    methods: {
        ...mapActions(['initRegisterServer'])
    },
    watch: {
        registerServerStatus: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
