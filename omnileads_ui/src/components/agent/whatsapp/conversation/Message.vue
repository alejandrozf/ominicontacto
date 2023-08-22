<template>
  <Card class="shadow-6 border-round-xl" :class="getClasses(message?.itsMine)">
    <template #content>
      <div class="py-0 my-0">
        <span
          ><b class="text-lg">{{ message?.from }}</b></span
        >
        <p class="mt-2 mb-3">
          {{ message?.message }}
        </p>
        <div class="flex justify-content-end flex-wrap">
          <div class="flex align-items-center justify-content-center">
            <small class="font-italic">
              {{ message?.date?.toLocaleString() }}
            </small>
            <i class="ml-2" :class="getIconMessageStatus(message?.status)" :style="{color: getIconStatusColor(message?.status)}" ></i>
          </div>
        </div>
      </div>
    </template>
  </Card>
</template>

<script>
import { WHATSAPP_MESSAGE } from '@/globals/agent/whatsapp';

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
        },
        getIconStatusColor (status) {
            if (status === WHATSAPP_MESSAGE.STATUS.READ) {
                return 'slateblue';
            } else if (status === WHATSAPP_MESSAGE.STATUS.ERROR) {
                return 'red';
            }
        },
        getIconMessageStatus (status) {
            if (status === WHATSAPP_MESSAGE.STATUS.SENDING) {
                return 'pi pi-clock';
            } else if (status === WHATSAPP_MESSAGE.STATUS.SENT) {
                return 'pi pi-check';
            } else if (status === WHATSAPP_MESSAGE.STATUS.DELIVERED) {
                return 'pi pi-check-circle';
            } else if (status === WHATSAPP_MESSAGE.STATUS.READ) {
                return 'pi pi-check-circle';
            } else if (status === WHATSAPP_MESSAGE.STATUS.ERROR) {
                return 'pi pi-times-circle';
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
