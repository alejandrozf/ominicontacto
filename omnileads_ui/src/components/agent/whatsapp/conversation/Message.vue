<template>
  <Card class="shadow-6 border-round-xl" :class="getClasses(message.itsMine)">
    <template #content>
      <div class="py-0 my-0">
        <span
          ><b class="text-lg">{{ message.from }}</b></span
        >
        <p class="mt-2 mb-3">
          {{ message.message }}
        </p>
        <div class="flex justify-content-end flex-wrap">
          <div class="flex align-items-center justify-content-center">
            <small class="font-italic">
              {{ message.date.toLocaleString() }}
            </small>
          </div>
        </div>
      </div>
    </template>
  </Card>
</template>

<script>
export default {
    props: {
        message: {
            type: Object,
            default: () => {}
        }
    },
    methods: {
        getClasses (itsMine) {
            if (itsMine) {
                return {
                    'bg-green-200': true,
                    'message-r': true
                };
            } else {
                return {
                    'bg-gray-200': true,
                    'message-l': true
                };
            }
        }
    }
};
</script>

<style scoped>
.message-r {
  float: right;
}
.message-l {
  float: left;
}
</style>
