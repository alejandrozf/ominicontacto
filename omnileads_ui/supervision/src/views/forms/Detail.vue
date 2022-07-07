<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>
          {{ $t("globals.form") + ": " + formDetail.nombre }}
        </h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.back')"
          icon="pi pi-arrow-left"
          class="p-button-info mr-2"
          @click="toFormsList"
        />
      </template>
    </Toolbar>
    <div class="grid formgrid">
      <div
        v-for="campo in formDetail.campos"
        :key="campo.id"
        class="field col-6 mt-4"
      >
        <label
          >{{ campo.nombre_campo }} {{ campo.is_required ? "*" : "" }}</label
        >
        <br />
        <InputText class="mt-2 w-full" v-if="campo.tipo == 1" type="text" />
        <Calendar class="mt-2 w-full" v-else-if="campo.tipo == 2" />
        <Dropdown
          class="mt-2 w-full"
          v-else-if="campo.tipo == 3"
          :options="JSON.parse(campo.values_select)"
        />
        <Textarea class="mt-2 w-full" v-else rows="5" cols="30" />
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';

export default {
    async created () {
        await this.initFormDetail(this.$route.params.id);
    },
    methods: {
        toFormsList () {
            this.$router.push({ name: 'forms' });
        },
        ...mapActions(['initFormDetail'])
    },
    computed: {
        ...mapState(['formDetail'])
    }
};
</script>
