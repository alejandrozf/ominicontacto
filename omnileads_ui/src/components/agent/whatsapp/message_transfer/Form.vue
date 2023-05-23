<template>
  <div class="card mt-2">
    <div class="grid formgrid">
      <div class="field sm:col-12 md:col-12 lg:col-12 xl:col-12">
        <label id="message_transfer_from"
        :class="{
            'p-error': v$.form.from.$invalid && submitted,
          }"
          >{{ $t("models.whatsapp.message_transfer.from") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-user"></i>
          </span>
          <InputText
            disabled
            :class="{
              'p-invalid': v$.form.from.$invalid && submitted,
            }"
            :placeholder="fromLabel"
          />
        </div>
        <small
          v-if="
            (v$.form.from.$invalid && submitted) || v$.form.from.$pending.$response
          "
          class="p-error"
        >
          {{
            v$.form.from.required.$message.replace(
              "Value",
              $t("models.whatsapp.message_transfer.from")
            )
          }}
        </small>
      </div>
    </div>
    <div class="grid formgrid">
      <div class="field sm:col-12 md:col-12 lg:col-12 xl:col-12">
        <label
          id="message_transfer_to"
          :class="{
            'p-error': v$.form.to.$invalid && submitted,
          }"
          >{{ $t("models.whatsapp.message_transfer.to") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-users"></i>
          </span>
          <Dropdown
            id="message_transfer_to"
            v-model="v$.form.to.$model"
            class="w-full"
            :class="{
              'p-invalid': v$.form.to.$invalid && submitted,
            }"
            :options="agents"
            placeholder="-----"
            optionLabel="agent_full_name"
            optionValue="agent_id"
            :emptyFilterMessage="$t('globals.without_data')"
            :filter="true"
            v-bind:filterPlaceholder="
              $t('globals.find_by', { field: $tc('globals.name') }, 1)
            "
          />
        </div>
        <small
          v-if="
            (v$.form.to.$invalid && submitted) || v$.form.to.$pending.$response
          "
          class="p-error"
        >
          {{
            v$.form.to.required.$message.replace(
              "Value",
              $t("models.whatsapp.message_transfer.to")
            )
          }}
        </small>
      </div>
    </div>
    <div class="flex justify-content-end flex-wrap mt-2">
      <div class="flex align-items-center">
        <Button
          class="p-button-danger p-button-outlined mr-2"
          :label="$t('globals.cancel')"
          @click="closeModal"
        />
        <Button
          :label="$t('globals.transfer')"
          icon="pi pi-arrows-h"
          @click="transfer(!v$.$invalid)"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { FilterMatchMode } from 'primevue/api';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { mapActions, mapState } from 'vuex';
import { HTTP_STATUS } from '@/globals';
import { notificationEvent } from '@/globals/agent/whatsapp';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            form: {
                conversationId: { required },
                from: { required },
                to: { required }
            }
        };
    },
    inject: ['$helpers'],
    props: {
        formToCreate: {
            type: Boolean,
            default: true
        }
    },
    data () {
        return {
            form: {
                from: null,
                to: null,
                conversationId: null
            },
            agents: [],
            submitted: false,
            filters: null,
            fromLabel: ''
        };
    },
    created () {
        this.initializeData();
    },
    computed: {
        ...mapState(['agtWhatsTransferChatAgents', 'agtWhatsTransferChatForm'])
    },
    methods: {
        ...mapActions(['agtWhatsTransferChatSend']),
        closeModal () {
            this.clearData();
            const event = new CustomEvent('onWhatsappTransferChatEvent', {
                detail: {
                    transfer_chat: false
                }
            });
            window.parent.document.dispatchEvent(event);
        },
        initializeData () {
            this.initFormData();
            this.submitted = false;
        },
        clearData () {
            this.fromLabel = '';
            this.form.from = null;
            this.form.to = null;
            this.form.conversationId = null;
            this.submitted = false;
        },
        initFormData () {
            this.form.from = this.agtWhatsTransferChatForm?.from;
            this.form.to = this.agtWhatsTransferChatForm?.to;
            this.form.conversationId = this.agtWhatsTransferChatForm?.conversationId;
        },
        clearFilter () {
            this.initFilters();
        },
        initFilters () {
            this.filters = {
                global: { value: null, matchMode: FilterMatchMode.CONTAINS }
            };
        },
        async transfer (isFormValid) {
            try {
                this.submitted = true;
                if (!isFormValid) {
                    return null;
                }
                const { status, message } = await this.agtWhatsTransferChatSend(
                    this.form
                );
                this.closeModal();
                if (status === HTTP_STATUS.SUCCESS) {
                    await notificationEvent(
                        this.$t('globals.success_notification'),
                        message,
                        this.$t('globals.icon_success')
                    );
                } else {
                    await notificationEvent(
                        this.$t('globals.error_notification'),
                        message,
                        this.$t('globals.icon_error')
                    );
                }
            } catch (error) {
                console.error('ERROR AL TRANSFERIR');
                console.error(error);
                await notificationEvent(
                    this.$t('globals.error_notification'),
                    'Error al transferir chat',
                    this.$t('globals.icon_error')
                );
            }
        }
    },
    watch: {
        agtWhatsTransferChatForm: {
            handler () {
                this.initFormData();
                if (this.agents.length > 0) {
                    this.fromLabel = this.agents.find(a => a.agent_id === this.form?.from)?.agent_full_name || '';
                } else {
                    this.fromLabel = '';
                }
            },
            deep: true,
            immediate: true
        },
        agtWhatsTransferChatAgents: {
            handler () {
                if (this.agtWhatsTransferChatAgents) {
                    this.agents = this.agtWhatsTransferChatAgents;
                    if (this.agents.length > 0) {
                        this.fromLabel = this.agents.find(a => a.agent_id === this.form?.from)?.agent_full_name || '';
                    } else {
                        this.fromLabel = '';
                    }
                }
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
