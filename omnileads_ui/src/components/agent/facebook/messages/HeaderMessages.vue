<template>
  <Toolbar class="mb-4" :style="{ border: `4px solid ${facebook_color}` }">
    <template #start>
      <i
        class="pi pi-facebook mr-2"
        :style="{ color: facebook_color, 'font-size': '3rem' }"
      ></i>
      <h2 class="font-bold">{{ $t("globals.facebook.title") }}</h2>
    </template>
    <template #end>
      <Button
        icon="pi pi-times"
        class="p-button-danger"
        @click="close"
        v-tooltip.top="$t('globals.close')"
      />
    </template>
  </Toolbar>
</template>

<script>
import { COLORS } from '@/globals';
export default {
    data () {
        return {
            facebook_color: COLORS.FACEBOOK.Blue
        };
    },
    methods: {
        close () {
            const event = new CustomEvent('onFacebookCloseContainerEvent', {
                detail: {
                    facebook_container: false
                }
            });
            window.parent.document.dispatchEvent(event);
        }
    }
};
</script>
