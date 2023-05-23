<template>
  <div>
    <div class="flex justify-content-between flex-wrap">
      <div class="flex align-items-center justify-content-center">
        <Avatar
          image="https://www.primefaces.org/wp-content/uploads/2020/05/placeholder.png"
          size="large"
          shape="circle"
        />
        <span class="pl-2">{{ from }}</span>
      </div>
      <div v-if="numMessages > 0" class="flex align-items-center justify-content-center">
        <Badge :value="numMessages" />
      </div>
    </div>
    <div class="flex justify-content-end flex-wrap">
      <div class="flex align-items-center justify-content-center">
        <small class="font-italic">
          {{ date }}
        </small>
      </div>
    </div>
  </div>
</template>

<script>
export default {
    props: {
        from: {
            type: String,
            default: '-----'
        },
        date: {
            type: String,
            default: '-----'
        },
        numMessages: {
            type: Number,
            default: 2
        }
    }
};
</script>
