<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("views.ivr.new_title") }}</h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.back')"
          icon="pi pi-arrow-left"
          class="p-button-info mr-2"
          @click="back"
        />
      </template>
    </Toolbar>
    <Form />
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import Form from '@/components/ivrs/Form';

export default {
    components: {
        Form
    },
    created () {
        this.initIVR();
    },
    methods: {
        ...mapActions(['initIVR']),
        back () {
            this.$router.push({ name: 'ivrs' });
        }
    }
};
</script>
