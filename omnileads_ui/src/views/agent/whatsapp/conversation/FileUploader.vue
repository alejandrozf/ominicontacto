<template>
  <div>
    <HeaderMediaUploader @handleCloseEvent="closeEvent" />
    <MediaUploader ref="mediaFormRef" :fileType="'pdf'" />
  </div>
</template>

<script>
import HeaderMediaUploader from '@/components/agent/whatsapp/conversation/HeaderMediaUploader';
import MediaUploader from '@/components/agent/whatsapp/shared/media/MediaUploader';
export default {
    components: {
        HeaderMediaUploader,
        MediaUploader
    },
    methods: {
        closeEvent () {
            this.$refs.mediaFormRef.clearData();
        }
    }
};
</script>
