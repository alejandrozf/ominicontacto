<template>
  <div class="card mt-2">
    <div class="grid formgrid">
      <div class="field sm:col-12 md:col-12 lg:col-12 xl:col-12">
        <label>{{ $t("globals.transfer") }}</label>
        <SelectButton
          v-model="form.targetType"
          class="mt-2"
          :options="targetTypes"
          optionLabel="label"
          optionValue="value"
          :allowEmpty="false"
        />
      </div>
      <div class="field sm:col-12 md:col-12 lg:col-12 xl:col-12">
        <label
          id="message_transfer_to"
          :class="{
            'p-error': v$.form.to.$invalid && submitted,
          }"
          >{{ targetLabel }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i :class="targetIcon"></i>
          </span>
          <Dropdown
            id="message_transfer_to"
            v-model="v$.form.to.$model"
            class="w-full"
            :class="{
              'p-invalid': v$.form.to.$invalid && submitted,
            }"
            :options="targetOptions"
            placeholder="-----"
            :optionLabel="targetOptionLabel"
            :optionValue="targetOptionValue"
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
              targetLabel
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
import { notificationEvent, NOTIFICATION, WHATSAPP_LOCALSTORAGE_EVENTS } from '@/globals/agent/whatsapp';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            form: {
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
                targetType: 'agent',
                to: null
            },
            agents: [],
            campaigns: [],
            submitted: false,
            filters: null,
            fromLabel: '',
            targetTypes: [
                { label: 'Agente', value: 'agent' },
                { label: 'Campaña', value: 'campaign' }
            ]
        };
    },
    created () {
        this.initializeData();
    },
    computed: {
        ...mapState([
            'agtWhatsTransferChatAgents',
            'agtWhatsTransferChatCampaigns',
            'agtWhatsCoversationInfo'
        ]),
        targetOptions () {
            return this.form.targetType === 'campaign' ? this.campaigns : this.agents;
        },
        targetOptionLabel () {
            return this.form.targetType === 'campaign'
                ? 'campaign_name'
                : 'agent_full_name';
        },
        targetOptionValue () {
            return this.form.targetType === 'campaign'
                ? 'campaign_id'
                : 'agent_id';
        },
        targetLabel () {
            return this.form.targetType === 'campaign' ? 'Campaña' : this.$t("models.whatsapp.message_transfer.to");
        },
        targetIcon () {
            return this.form.targetType === 'campaign' ? 'pi pi-sitemap' : 'pi pi-users';
        }
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
            this.form.targetType = 'agent';
            this.form.to = null;
            this.form.conversationId = null;
            this.submitted = false;
        },
        initFormData () {
            this.form.targetType = this.agtWhatsTransferChatForm?.targetType || 'agent';
            this.form.to = this.agtWhatsTransferChatForm?.to;
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
                const conversationId = JSON.parse(
                    localStorage.getItem('agtWhatsCoversationInfo')
                ).id;
                const to = this.form?.to || null;
                const { status, message } = await this.agtWhatsTransferChatSend({
                    targetType: this.form.targetType,
                    to: to,
                    conversationId: conversationId
                });
                this.closeModal();
                if (status === HTTP_STATUS.SUCCESS) {
                    const event = new CustomEvent(WHATSAPP_LOCALSTORAGE_EVENTS.TRANSFER.DONE, { detail: {
                        to,
                        conversationId,
                    }});
                    window.parent.document.dispatchEvent(event);
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
                console.error('ERROR AL TRANSFERIR');
                console.error(error);
                await notificationEvent(
                    NOTIFICATION.TITLES.ERROR,
                    'Error al transferir chat',
                    NOTIFICATION.TITLES.ERROR
                );
            }
        }
    },
    watch: {
        agtWhatsTransferChatAgents: {
            handler () {
                if (this.agtWhatsTransferChatAgents) {
                    this.agents = this.agtWhatsTransferChatAgents;
                }
            },
            deep: true,
            immediate: true
        },
        agtWhatsTransferChatCampaigns: {
            handler () {
                if (this.agtWhatsTransferChatCampaigns) {
                    this.campaigns = this.agtWhatsTransferChatCampaigns;
                }
            },
            deep: true,
            immediate: true
        },
        'form.targetType' () {
            this.form.to = null;
        }
    }
};
</script>
