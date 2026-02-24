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
        icon="pi pi-plus"
        class="p-button-success"
        @click="newConversation"
        v-tooltip.top="$t('models.whatsapp.conversation.new.title')"
      />
      <Button
        icon="pi pi-times"
        class="p-button-danger ml-2"
        @click="close"
        v-tooltip.top="$t('globals.close')"
      />
    </template>
  </Toolbar>
</template>

<script>
import { COLORS } from '@/globals';
import { FACEBOOK_LOCALSTORAGE_EVENTS } from '@/globals/agent/facebook';
export default {
    inject: ['$helpers'],
    data () {
        return {
            facebook_color: COLORS.FACEBOOK.Blue
        };
    },
    methods: {
        newConversation () {
            if (this.$helpers.isSocketConnected(this.$t)) {
                localStorage.setItem('agtFacebookConversationNewResetForm', true);
                const modalEvent = new CustomEvent('onFacebookConversationNewEvent', {
                    detail: {
                        conversation_new: true
                    }
                });
                window.parent.document.dispatchEvent(modalEvent);
                const event = new Event(
                    FACEBOOK_LOCALSTORAGE_EVENTS.CONVERSATION.NEW_INIT_DATA
                );
                window.parent.document.dispatchEvent(event);
            }
        },
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
