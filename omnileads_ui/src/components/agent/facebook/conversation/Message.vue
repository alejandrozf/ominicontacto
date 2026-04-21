<template>
  <Card class="border-round-xl" :class="getClasses(message?.itsMine)" style="max-width:65%">
    <template #content>
      <div class="py-0 my-0">
        {{ message?.content }}
        <div v-if="message.type==='message' || message.type==='quick_reply'">
          <p class="mt-2 mb-3 message-text">
            {{ message?.message.text }}
          </p>
        </div>
        <div v-if="message.type==='template'">
          <p class="mt-2 mb-3 message-text">
            {{ message?.message }}
          </p>
        </div>

        <div v-if="message.type==='image'">
          <a :href="message.message.image.url" style="text-decoration: none; color: inherit;" target="_blank" download>
            <Image :src="message.message.image.url" width="250" />
          </a>
        </div>
        <div v-if="message.type==='file'">
          <a :href="message.message.file.url" style="text-decoration: none; color: inherit;" target="_blank" download>
            <iframe :src="message.message.file.url" frameBorder="0" scrolling="auto" height="100%" width="100%"></iframe>
          </a>
        </div>
        <div v-if="message.type==='document' || message.type==='application'">
          <a :href="message.message.document.url" style="text-decoration: none; color: inherit;" target="_blank" download>
            <iframe :src="message.message.document.url" frameBorder="0" scrolling="auto" height="100%" width="100%"></iframe>
          </a>
        </div>
        <div v-if="message.type==='audio'">
          <audio controls>
            <source :src="message.message.audio.url" type="audio/ogg">
          </audio>
        </div>
        <div v-if="message.type==='video'">
          <video width="320" height="240" controls>
            <source :src="message.message.video.url" type="video/mp4">
          </video>
        </div>
        <div v-if="message.type==='list'">
          <p class="mt-2 mb-3 message-text">
            {{ message?.message.text }}
          </p>
          <button class="btn btn-primary"
            v-for="button in message?.message?.buttons"
            :key="button.payload"
          >
            {{ button.title }}
          </button>
        </div>
        <div v-if="message?.fail_reason" class="flex justify-content-end flex-wrap">
          <Tag severity="danger" :value="message?.fail_reason"></Tag>
        </div>
        <div class="flex justify-content-end flex-wrap">
          <div class="flex align-items-center justify-content-center">
            <small class="font-italic">
              {{ message?.date?.toLocaleString() }}
            </small>
            <i v-if="message?.itsMine" class="ml-2" :class="getIconMessageStatus(message?.status)" :style="{color: getIconStatusColor(message?.status)}" ></i>
          </div>
        </div>
      </div>
    </template>
  </Card>
</template>

<script>
import { FACEBOOK_MESSAGE } from '@/globals/agent/facebook';
import Image from 'primevue/image';
export default {
    props: {
        message: {
            type: Object,
            default: () => {}
        }
    },
    components: {
        Image
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
            if (status === FACEBOOK_MESSAGE.STATUS.READ) {
                return 'slateblue';
            } else if (status === FACEBOOK_MESSAGE.STATUS.ERROR) {
                return 'red';
            }
        },
        getIconMessageStatus (status) {
            if (status === FACEBOOK_MESSAGE.STATUS.SENT) {
                return 'pi pi-check';
            } else if (status === FACEBOOK_MESSAGE.STATUS.DELIVERED) {
                return 'pi pi-check-circle';
            } else if (status === FACEBOOK_MESSAGE.STATUS.READ) {
                return 'pi pi-check-circle';
            } else if (status === FACEBOOK_MESSAGE.STATUS.ERROR) {
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
.message-text {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  word-break: break-word;
}
</style>
