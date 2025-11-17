<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '70vw' }"
    :closable="false"
    :modal="false"
  >
    <template #header>
      <h2>
        {{
          formToCreate
            ? $t("views.facebook.page.option_form.new_title")
            : $t("views.facebook.page.option_form.edit_title")
        }}
      </h2>
    </template>
    <Form @closeModalEvent="closeModal" :formToCreate="formToCreate" :menuId="menuId"/>
  </Dialog>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import Form from '@/components/supervisor/facebook/pages/options_form/Form';

export default {
    props: {
        showModal: {
            type: Boolean,
            default: false
        },
        formToCreate: {
            type: Boolean,
            default: false
        },
        option: {
          type: Array,
          default:[]
        },
        menuId: {
          type: Number
        }
    },
    components: {
        Form
    },
    computed: {
        ...mapState([])
    },
    methods: {
        ...mapActions([]),
        closeModal () {
          this.$emit('handleModalEvent',{
                showModal: false,
                formToCreate: false
          });
        }
    },
    watch: {
        formToCreate: {
            handler () {},
            deep: true,
            immediate: true
        },
        showModal: {
          handler () {},
          deep: true,
          immediate: true
        }
    }
};
</script>
