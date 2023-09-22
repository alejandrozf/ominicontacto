<template>
    <div>
        <HeaderConversation class="mb-3"/>
        <ListMessages id="listMessages" class="scroll" />
        <TextBox class="footer" :conversationId="id" @scrollDownEvent="scrollDown" />
    </div>
</template>

<script>
import HeaderConversation from '@/components/agent/whatsapp/conversation/HeaderConversation';
import TextBox from '@/components/agent/whatsapp/conversation/TextBox';
import ListMessages from '@/components/agent/whatsapp/conversation/ListMessages';
import { mapActions } from 'vuex';
export default {
    components: {
        HeaderConversation,
        ListMessages,
        TextBox
    },
    data () {
        return {
            id: parseInt(this.$route.params.id)
        };
    },
    async created () {
        await this.agtWhatsConversationDetail(this.id);
    },
    methods: {
        ...mapActions(['agtWhatsConversationDetail']),
        scrollDown () {
            const scroll = document.getElementById('listMessages');
            scroll.scrollTop = scroll.scrollHeight;
        }
    }
};
</script>

<style scoped>
.scroll {
    overflow-y: scroll;
    height: calc(100vh - 160px);
}

.footer {
    bottom: 0px;
    position: fixed;
    width: 100%;
}
</style>
