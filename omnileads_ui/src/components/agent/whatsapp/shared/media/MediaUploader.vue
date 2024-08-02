<template>
  <div>
    <Toast />
    <FileUpload
      :multiple="multiple"
      :customUpload="customUpload"
      :maxFileSize="maxFileSize"
      :fileLimit="fileLimit"
      :accept="getFileType()"
      ref="fileUpload"
      @select="onSelectedFiles($event)"
      @uploader="customUploader($event)"
      @error="errorToUpload($event)"
      :invalidFileLimitMessage="
        $t('globals.media.uploaderForm.invalid_file_limit_message', {
          num: fileLimit,
        })
      "
      :invalidFileSizeMessage="
        $t('globals.media.uploaderForm.invalid_file_size_message', {
          num: maxFileSize,
        })
      "
      :invalidFileTypeMessage="
        $t('globals.media.uploaderForm.invalid_file_type_message')
      "
      :cancelLabel="$t('globals.cancel')"
      :chooseLabel="$t('globals.select')"
      :uploadLabel="$t('globals.upload')"
    >
      <template #empty>
        <div class="flex align-items-center justify-content-center flex-column">
          <i
            class="pi pi-cloud-upload border-2 border-circle p-5 text-6xl text-400 border-400"
          />
          <p class="mt-4 mb-0">
            {{ $t("globals.media.uploaderForm.drag_and_drop") }}
          </p>
        </div>
      </template>
    </FileUpload>
  </div>
</template>

<script>
import { HTTP_STATUS } from '@/globals';
import { notificationEvent, NOTIFICATION } from '@/globals/agent/whatsapp';
import { mapActions, mapState } from 'vuex';
export default {
    props: {
        fileType: {
            type: String,
            default: 'img'
        },
        multiple: {
            type: Boolean,
            default: false
        },
        customUpload: {
            type: Boolean,
            default: true
        },
        maxFileSize: {
            type: Number,
            default: 1000000
        },
        fileLimit: {
            type: Number,
            default: 1
        }
    },
    data () {
        return {
            files: [],
            totalSize: 0,
            totalSizePercent: 0
        };
    },
    computed: {
        ...mapState(['agtWhatsCoversationInfo'])
    },
    methods: {
        ...mapActions(['agtWhatsCoversationSendAttachmentMessage']),
        getFileType () {
            return this.fileType === 'img' ? 'image/*' : 'application/pdf,audio/*,video/*,text/*';
        },
        onSelectedFiles (event) {
            this.files = event.files;
            this.files.forEach((file) => {
                this.totalSize += parseInt(this.formatSize(file.size));
            });
        },
        async customUploader ($event) {
            try {
                const messages = JSON.parse(
                    localStorage.getItem('agtWhatsappConversationMessages')
                );
                const agtWhatsCoversationInfo = JSON.parse(
                    localStorage.getItem('agtWhatsCoversationInfo')
                );
                const file = this.files[0];
                let formData = new FormData();
                formData.append('file', file)
                var data = {
                    conversationId: agtWhatsCoversationInfo.id,
                    formData: formData,
                    phoneLine: agtWhatsCoversationInfo.line.number,
                    messages: messages,
                    $t: this.$t
                }
                const { status, message } = await this.agtWhatsCoversationSendAttachmentMessage(data);
                if (status === HTTP_STATUS.SUCCESS) {
                    this.clearData();
                    await notificationEvent(
                        NOTIFICATION.TITLES.SUCCESS,
                        message,
                        NOTIFICATION.ICONS.SUCCESS
                    );
                } else {
                    await notificationEvent(
                        NOTIFICATION.TITLES.ERROR,
                        message,
                        NOTIFICATION.ICONS.ERROR
                    );
                }
            } catch (error) {
                console.error(error);
                this.clearData();
                await notificationEvent(
                    NOTIFICATION.TITLES.ERROR,
                    'Error al enviar template',
                    NOTIFICATION.ICONS.ERROR
                );
            }
        },
        clearData () {
            this.files = [];
            this.totalSize = 0;
            this.totalSizePercent = 0;
            this.$refs.fileUpload.clear();
            this.$refs.fileUpload.uploadedFileCount = 0;
        },
        errorToUpload ($event) {
            console.error('Error to upload file');
            console.error($event);
        },
        formatSize (bytes) {
            if (bytes === 0) {
                return '0 B';
            }
            const k = 1000;
            const dm = 3;
            const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
        }
    }
};
</script>
