<template>
  <div>
    <div class="card">
      <Steps :model="steps" />
    </div>
    <br />
    <br />
    <router-view
      class="mx-6"
      :formData="supWhatsappLine"
      @prevPage="prevPage($event)"
      @nextPage="nextPage($event)"
    >
    </router-view>
  </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
    props: {
        formToEdit: {
            type: Boolean,
            default: false
        },
        steps: {
            type: Array,
            default: () => []
        }
    },
    computed: {
        ...mapState(['supWhatsappLine'])
    },
    methods: {
        nextPage (event) {
            this.$router.push(this.steps[event.pageIndex + 1].to);
        },
        prevPage (event) {
            this.$router.push(this.steps[event.pageIndex - 1].to);
        }
    },
    watch: {
        steps: {
            handler () {},
            deep: true,
            immediate: true
        },
        supWhatsappLine: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
