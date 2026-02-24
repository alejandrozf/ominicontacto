<template>
  <div>
    <HeaderMediaUploader @handleCloseEvent="closeEvent" />
    <MediaUploader ref="mediaFormRef" :fileType="'img'" />
  </div>
</template>

<script>
import HeaderMediaUploader from '@/components/agent/facebook/conversation/HeaderMediaUploader';
import MediaUploader from '@/components/agent/facebook/shared/media/MediaUploader';
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
