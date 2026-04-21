<template>
  <Card class="border-round-xl" :class="getClasses(message?.itsMine)" style="max-width:65%">
    <template #content>
      <div class="py-0 my-0">
        <div v-if="isForwarded(message?.message)" class="mb-2">
          <Tag severity="info" :value="getForwardedLabel(message?.message)"></Tag>
        </div>
        <!-- <span
          >{{ message?.from }}</span
        > -->
        <div v-if="message.type==='text' || message.type==='buttons'">
          <h5 v-if="message?.message.header" class="mb-1 message-text" :style="{ 'font-weight': 'bold' }">
            {{ message?.message.header }}
          </h5>
          <p class="mt-2 mb-3 message-text">
            {{ message?.message.text }}
          </p>
          <div
            v-if="message.type === 'buttons' && message?.message.buttons"
            class="flex flex-column gap-2 mt-2"
          >
            <button
              v-for="(btn, index) in message?.message.buttons"
              :key="index"
              class="w-full text-center py-2 px-3
                    bg-white
                    border-1 border-300
                    border-round-xl
                    text-blue-600
                    cursor-default"
              disabled
            >
              {{ btn.text }}
            </button>
          </div>
        </div>
        <div v-if="message.type==='template'">
          <p class="mt-2 mb-3 message-text">
            {{ message?.message.text }}
          </p>
        </div>
        <div v-if="message.type==='image'">
          <a :href="message?.message.url" style="text-decoration: none; color: inherit;" target="_blank" download>
            <Image :src=message?.message.url :alt=message?.message.name width="250" />
            <div class="display-middle">
              <p>{{ message?.message.name }}</p>
            </div>
          </a>
        </div>
        <div v-if="message.type==='file'">
          <a :href="message?.message.url" style="text-decoration: none; color: inherit;" target="_blank" download>
            <iframe :src="message?.message.url" frameBorder="0" scrolling="auto" height="100%" width="100%"></iframe>
            {{ message?.message.name }}
          </a>
        </div>
        <div v-if="message.type==='document' || message.type==='application'">
          <a :href="message?.message.url" style="text-decoration: none; color: inherit;" target="_blank" download>
            <iframe :src="message?.message.url" frameBorder="0" scrolling="auto" height="100%" width="100%"></iframe>
            {{ message?.message.name }}
          </a>
        </div>
        <div v-if="message.type==='audio'">
          <audio controls>
            <source :src="message?.message.url" type="audio/ogg">
          </audio>
        </div>
        <div v-if="message.type==='video'">
          <video width="320" height="240" controls>
            <source :src="message?.message.url" type="video/mp4">
          </video>
        </div>
        <div v-if="message.type==='contact'">
          <pre>{{message?.message.contacts}}</pre>
        </div>
        <div v-if="message.type==='list-gupshup' || message.type==='list-meta'">
          <p class="mt-2 mb-3 message-text">
            {{ message?.message.text }}
          </p>
        </div>
        <div v-if="message.type==='list_reply'">
          <p class="mt-2 mb-3 message-text">
            {{ message?.message.text }}
          </p>
        </div>
        <div v-if="message.type==='button_reply'">
          <p class="mt-2 mb-3 message-text">
            {{ message?.message.title }}
          </p>
        </div>
        <div v-if="message.type === 'button'" class="wa-message">
          <div v-if="message.message.context" class="wa-reply-preview">
            <div class="wa-reply-bar"></div>
            <div class="wa-reply-content">
              <h5>
                {{ message.message.context.header }}
              </h5>
              <p>{{ message.message.context.text }}</p>
            </div>
          </div>
          <div class="wa-bubble">
            {{ message.message.text }}
          </div>

        </div>
        <div v-if="message.type === 'reply_text'" class="wa-message">
          <!-- REPLY PREVIEW -->
          <div v-if="message.message.context" class="wa-reply-preview">

            <div class="wa-reply-bar"></div>

            <div class="wa-reply-content">

              <h5 class="m-0 text-sm">
                {{ message.message.context.header }}
              </h5>

              <p class="m-0 text-xs text-500">
                {{ message.message.context.name }}
              </p>

              <!-- ===== TEXTO ===== -->
              <p
                v-if="message.message.context.text"
                class="m-0 text-sm mt-1"
              >
                {{ message.message.context.text }}
              </p>

              <!-- ===== IMAGE ===== -->
              <img
                v-else-if="message.message.context?.type === 'image'"
                :src="message.message.context.previewUrl"
                class="wa-reply-media"
              />

              <!-- ===== VIDEO ===== -->
              <video
                v-else-if="message.message.context?.type === 'video'"
                :src="message.message.context.previewUrl"
                class="wa-reply-media"
                muted
              ></video>

              <!-- ===== DOCUMENT ===== -->
              <div
                v-else-if="message.message.context?.type === 'document'"
                class="wa-reply-document"
              >
                <i class="pi pi-file"></i>
                <iframe :src="message?.message.previewUrl" frameBorder="0" scrolling="auto" height="100%" width="100%"></iframe>
              </div>

              <!-- ===== AUDIO ===== -->
              <div
                v-else-if="message.message.context?.type === 'audio'"
                class="wa-reply-document"
              >
                <i class="pi pi-volume-up"></i>
                <span>Mensaje de voz</span>
              </div>

            </div>
          </div>

          <!-- MENSAJE ACTUAL -->
          <div class="wa-bubble">
            {{ message.message.text }}
          </div>

        </div>
        <div v-if="message.type === 'reply_image'" class="wa-message">
          <!-- REPLY PREVIEW -->
          <div v-if="message.message.context" class="wa-reply-preview">

            <div class="wa-reply-bar"></div>

            <div class="wa-reply-content">

              <h5 class="m-0 text-sm">
                {{ message.message.context.header }}
              </h5>

              <p class="m-0 text-xs text-500">
                {{ message.message.context.name }}
              </p>

              <!-- ===== TEXTO ===== -->
              <p
                v-if="message.message.context.text"
                class="m-0 text-sm mt-1"
              >
                {{ message.message.context.text }}
              </p>

              <!-- ===== IMAGE ===== -->
              <img
                v-else-if="message.message.context?.type === 'image'"
                :src="message.message.context.previewUrl"
                class="wa-reply-media"
              />

              <!-- ===== VIDEO ===== -->
              <video
                v-else-if="message.message.context?.type === 'video'"
                :src="message.message.context.previewUrl"
                class="wa-reply-media"
                muted
              ></video>

              <!-- ===== DOCUMENT ===== -->
              <div
                v-else-if="message.message.context?.type === 'document'"
                class="wa-reply-document"
              >
                <i class="pi pi-file"></i>
                <iframe :src="message?.message.previewUrl" frameBorder="0" scrolling="auto" height="100%" width="100%"></iframe>
              </div>

              <!-- ===== AUDIO ===== -->
              <div
                v-else-if="message.message.context?.type === 'audio'"
                class="wa-reply-document"
              >
                <i class="pi pi-volume-up"></i>
                <span>Mensaje de voz</span>
              </div>

            </div>
          </div>
          <!-- MENSAJE ACTUAL -->
          <div class="wa-bubble">
            <a :href="message?.message.url" style="text-decoration: none; color: inherit;" target="_blank" download>
              <Image :src=message?.message.url :alt=message?.message.name width="250" />
              <div class="display-middle">
                <p>{{ message?.message.name }}</p>
              </div>
            </a>
          </div>
        </div>
        <div v-if="message.type === 'reply_document'" class="wa-message">
          <!-- REPLY PREVIEW -->
          <div v-if="message.message.context" class="wa-reply-preview">

            <div class="wa-reply-bar"></div>

            <div class="wa-reply-content">

              <h5 class="m-0 text-sm">
                {{ message.message.context.header }}
              </h5>

              <p class="m-0 text-xs text-500">
                {{ message.message.context.name }}
              </p>

              <!-- ===== TEXTO ===== -->
              <p
                v-if="message.message.context.text"
                class="m-0 text-sm mt-1"
              >
                {{ message.message.context.text }}
              </p>

              <!-- ===== IMAGE ===== -->
              <img
                v-else-if="message.message.context?.type === 'image'"
                :src="message.message.context.previewUrl"
                class="wa-reply-media"
              />

              <!-- ===== VIDEO ===== -->
              <video
                v-else-if="message.message.context?.type === 'video'"
                :src="message.message.context.previewUrl"
                class="wa-reply-media"
                muted
              ></video>

              <!-- ===== DOCUMENT ===== -->
              <div
                v-else-if="message.message.context?.type === 'document'"
                class="wa-reply-document"
              >
                <i class="pi pi-file"></i>
                <iframe :src="message?.message.previewUrl" frameBorder="0" scrolling="auto" height="100%" width="100%"></iframe>
              </div>

              <!-- ===== AUDIO ===== -->
              <div
                v-else-if="message.message.context?.type === 'audio'"
                class="wa-reply-document"
              >
                <i class="pi pi-volume-up"></i>
                <span>Mensaje de voz</span>
              </div>

            </div>
          </div>
          <!-- MENSAJE ACTUAL -->
          <div class="wa-bubble">
            <a :href="message?.message.url" style="text-decoration: none; color: inherit;" target="_blank" download>
              <iframe :src="message?.message.url" frameBorder="0" scrolling="auto" height="100%" width="100%"></iframe>
              {{ message?.message.name }}
            </a>
          </div>
        </div>
        <div v-if="message.type === 'reply_video'" class="wa-message">
          <!-- REPLY PREVIEW -->
          <div v-if="message.message.context" class="wa-reply-preview">

            <div class="wa-reply-bar"></div>

            <div class="wa-reply-content">

              <h5 class="m-0 text-sm">
                {{ message.message.context.header }}
              </h5>

              <p class="m-0 text-xs text-500">
                {{ message.message.context.name }}
              </p>

              <!-- ===== TEXTO ===== -->
              <p
                v-if="message.message.context.text"
                class="m-0 text-sm mt-1"
              >
                {{ message.message.context.text }}
              </p>

              <!-- ===== IMAGE ===== -->
              <img
                v-else-if="message.message.context?.type === 'image'"
                :src="message.message.context.previewUrl"
                class="wa-reply-media"
              />

              <!-- ===== VIDEO ===== -->
              <video
                v-else-if="message.message.context?.type === 'video'"
                :src="message.message.context.previewUrl"
                class="wa-reply-media"
                muted
              ></video>

              <!-- ===== DOCUMENT ===== -->
              <div
                v-else-if="message.message.context?.type === 'document'"
                class="wa-reply-document"
              >
                <i class="pi pi-file"></i>
                <iframe :src="message?.message.previewUrl" frameBorder="0" scrolling="auto" height="100%" width="100%"></iframe>
              </div>

              <!-- ===== AUDIO ===== -->
              <div
                v-else-if="message.message.context?.type === 'audio'"
                class="wa-reply-document"
              >
                <i class="pi pi-volume-up"></i>
                <span>Mensaje de voz</span>
              </div>

            </div>
          </div>
          <!-- MENSAJE ACTUAL -->
          <div class="wa-bubble">
            <a :href="message?.message.url" style="text-decoration: none; color: inherit;" target="_blank" download>
              <video width="320" height="240" controls>
                <source :src="message?.message.url" type="video/mp4">
              </video>
            </a>
          </div>
        </div>
        <div v-if="message?.fail_reason" class="flex justify-content-end flex-wrap">
          <Tag severity="danger" :value="message?.fail_reason"></Tag>
        </div>
        <div class="flex justify-content-end flex-wrap" style="
          margin-top: 10px;">
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
import { WHATSAPP_MESSAGE } from '@/globals/agent/whatsapp';
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
            if (status === WHATSAPP_MESSAGE.STATUS.READ) {
                return 'slateblue';
            } else if (status === WHATSAPP_MESSAGE.STATUS.ERROR) {
                return 'red';
            }
        },
        getIconMessageStatus (status) {
            if (status === WHATSAPP_MESSAGE.STATUS.SENT) {
                return 'pi pi-check';
            } else if (status === WHATSAPP_MESSAGE.STATUS.DELIVERED) {
                return 'pi pi-check-circle';
            } else if (status === WHATSAPP_MESSAGE.STATUS.READ) {
                return 'pi pi-check-circle';
            } else if (status === WHATSAPP_MESSAGE.STATUS.ERROR) {
                return 'pi pi-times-circle';
            }
        },
        isForwarded (content) {
            return content?.forwarded === true || content?.frequently_forwarded === true;
        },
        getForwardedLabel (content) {
            return content?.frequently_forwarded === true
                ? 'Reenviado muchas veces'
                : 'Reenviado';
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
.wa-message {
  display: flex;
  flex-direction: column;
  max-width: 75%;
}

.wa-reply-preview {
  display: flex;
  background: #f0f0f0;
  border-radius: 8px;
  margin-bottom: 4px;
  overflow: hidden;
}

.wa-reply-content {
  padding: 6px 8px;
  font-size: 13px;
  color: #555;
  white-space: pre-wrap;
}

.wa-bubble {
  background-color: #dcf8c6; /* burbuja enviada */
  padding: 8px 12px;
  border-radius: 12px;
  font-size: 14px;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.wa-reply-bar {
  width: 4px;
  background: #25D366;
  border-radius: 4px;
  margin-right: 6px;
}

.wa-reply-media {
  width: 120px;
  height: 70px;
  object-fit: cover;
  border-radius: 6px;
  margin-top: 4px;
}

.wa-reply-document {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  margin-top: 4px;
  color: #555;
}
</style>
