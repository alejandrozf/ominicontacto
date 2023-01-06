<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("views.group_of_hour.new_title") }}</h1>
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
import Form from '@/components/group_of_hours/Form';

export default {
    components: {
        Form
    },
    created () {
        this.initGroupOfHour();
    },
    methods: {
        ...mapActions(['initGroupOfHour']),
        back () {
            this.$router.push({ name: 'group_of_hours' });
        }
    }
};
</script>
