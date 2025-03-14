<template>
  <div class="card">
    <div class="grid formgrid mt-4">
      <div class="field col-6">
        <label
          id="inbound_route_name"
          :class="{
            'p-error': v$.inboundRouteForm.nombre.$invalid && submitted,
          }"
          >{{ $t("models.inbound_route.name") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <InputText
            id="inbound_route_name"
            :class="{
              'p-invalid': v$.inboundRouteForm.nombre.$invalid && submitted,
            }"
            :placeholder="$t('forms.inbound_route.enter_name')"
            v-model="v$.inboundRouteForm.nombre.$model"
          />
        </div>
        <small
          v-if="
            (v$.inboundRouteForm.nombre.$invalid && submitted) ||
            v$.inboundRouteForm.nombre.$pending.$response
          "
          class="p-error"
          >{{
            v$.inboundRouteForm.nombre.required.$message.replace(
              "Value",
              $t("models.inbound_route.name")
            )
          }}</small
        >
      </div>
      <div class="field col-6">
        <label
          id="inbound_route_phone"
          :class="{
            'p-error': v$.inboundRouteForm.telefono.$invalid && submitted,
          }"
          >{{ $t("models.inbound_route.phone") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-phone"></i>
          </span>
          <InputText
            id="inbound_route_phone"
            :class="{
              'p-invalid': v$.inboundRouteForm.telefono.$invalid && submitted,
            }"
            :placeholder="$t('forms.inbound_route.enter_phone')"
            v-model="v$.inboundRouteForm.telefono.$model"
          />
        </div>
        <small
          v-if="
            (v$.inboundRouteForm.telefono.$invalid && submitted) ||
            v$.inboundRouteForm.telefono.$pending.$response
          "
          class="p-error"
          >{{
            v$.inboundRouteForm.telefono.required.$message.replace(
              "Value",
              $t("models.inbound_route.phone")
            )
          }}</small
        >
      </div>
      <div class="field col-12">
        <label id="inbound_route_is_direct">{{ $t("models.inbound_route.is_direct") }}</label>
        <div class="p-inputgroup mt-2">
          <InputSwitch id="inbound_route_is_direct" v-bind:modelValue="isDirect" v-on:change="isDirectOnChange" />
        </div>
      </div>
      <div class="field col-6">
        <label
          id="inbound_route_caller_id"
          >{{ $t("models.inbound_route.caller_id") }}</label
        >
        <div class="p-inputgroup mt-2">
          <InputText
            id="inbound_route_caller_id"
            :placeholder="$t('forms.inbound_route.enter_caller_id')"
            v-model="inboundRouteForm.prefijo_caller_id"
          />
        </div>
      </div>
      <div class="field col-6">
          <label
            id="pause_type"
            :class="{
              'p-error': v$.inboundRouteForm.idioma.$invalid && submitted,
            }"
            >{{ $t("models.inbound_route.idiom") }}*</label
          >
          <Dropdown
            v-model="inboundRouteForm.idioma"
            class="w-full mt-2"
            :class="{
              'p-invalid': v$.inboundRouteForm.idioma.$invalid && submitted,
            }"
            :options="languages"
            placeholder="-----"
            optionLabel="language"
            optionValue="id"
            :emptyFilterMessage="$t('globals.without_data')"
          />
          <small
            v-if="
              (v$.inboundRouteForm.idioma.$invalid && submitted) ||
              v$.inboundRouteForm.idioma.$pending.$response
            "
            class="p-error"
            >{{
              v$.inboundRouteForm.idioma.required.$message.replace(
                "Value",
                $t("models.inbound_route.idiom")
              )
            }}</small
          >
      </div>
      <div class="field col-6">
          <label
            id="pause_type"
            :class="{
              'p-error': v$.inboundRouteForm.tipo_destino.$invalid && submitted,
            }"
            >{{ $t("models.inbound_route.destiny_type") }}*</label
          >
          <Dropdown
            v-model="inboundRouteForm.tipo_destino"
            class="w-full mt-2"
            :class="{
              'p-invalid': v$.inboundRouteForm.tipo_destino.$invalid && submitted,
            }"
            :options="destination_types"
            placeholder="-----"
            optionLabel="option"
            optionValue="value"
            optionDisabled="disabled"
            :emptyFilterMessage="$t('globals.without_data')"
          />
          <small
            v-if="
              (v$.inboundRouteForm.tipo_destino.$invalid && submitted) ||
              v$.inboundRouteForm.tipo_destino.$pending.$response
            "
            class="p-error"
            >{{
              v$.inboundRouteForm.tipo_destino.required.$message.replace(
                "Value",
                $t("models.inbound_route.destiny_type")
              )
            }}</small
          >
      </div>
      <div class="field col-6">
          <label
            id="pause_type"
            :class="{
              'p-error': v$.inboundRouteForm.destino.$invalid && submitted,
            }"
            >{{ $t("models.inbound_route.destiny") }}*</label
          >
          <Dropdown
            v-model="inboundRouteForm.destino"
            class="w-full mt-2"
            :class="{
              'p-invalid': v$.inboundRouteForm.destino.$invalid && submitted,
            }"
            :options="destinations_filter"
            placeholder="-----"
            optionLabel="nombre"
            optionValue="id"
            :emptyFilterMessage="$t('globals.without_data')"
          />
          <small
            v-if="
              (v$.inboundRouteForm.destino.$invalid && submitted) ||
              v$.inboundRouteForm.destino.$pending.$response
            "
            class="p-error"
            >{{
              v$.inboundRouteForm.destino.required.$message.replace(
                "Value",
                $t("models.inbound_route.destiny")
              )
            }}</small
          >
      </div>
    </div>
    <div class="flex justify-content-end flex-wrap">
      <div class="flex align-items-center justify-content-center">
        <Button
          :label="$t('globals.save')"
          icon="pi pi-save"
          class="mt-4"
          @click="save(!v$.$invalid)"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { useVuelidate } from '@vuelidate/core';
import { required } from '@vuelidate/validators';
import { mapActions, mapState } from 'vuex';
import { HTTP_STATUS } from '@/globals';
import {
    AGENT,
    CAMPAIGN,
    CUSTOM_DST,
    HANGUP,
    ID_CLIENT,
    IVR,
    VALIDATION_DATE
} from '@/globals/supervisor/ivr';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            inboundRouteForm: {
                nombre: { required },
                telefono: { required },
                tipo_destino: { required },
                destino: { required },
                idioma: { required }
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
            submitted: false,
        };
    },
    computed: {
        destination_types () {
            return [
                { option: this.$t('forms.inbound_route.destination_types.campaign'), value: CAMPAIGN, disabled: this.isDirect },
                { option: this.$t('forms.inbound_route.destination_types.validation_date'), value: VALIDATION_DATE, disabled: this.isDirect },
                { option: this.$t('forms.inbound_route.destination_types.ivr'), value: IVR, disabled: this.isDirect },
                { option: this.$t('forms.inbound_route.destination_types.hangup'), value: HANGUP, disabled: this.isDirect },
                { option: this.$t('forms.inbound_route.destination_types.id_client'), value: ID_CLIENT, disabled: this.isDirect },
                { option: this.$t('forms.inbound_route.destination_types.agent'), value: AGENT, disabled: !this.isDirect },
                { option: this.$t('forms.inbound_route.destination_types.custom_dst'), value: CUSTOM_DST, disabled: this.isDirect }
            ];
        },
        destinations_filter () {
            return this.inboundRouteForm.tipo_destino !== null ? this.destinations[`${this.inboundRouteForm.tipo_destino}`] : [];
        },
        isDirect () {
            return this.inboundRouteForm.tipo_destino === AGENT;
        },
        ...mapState(['inboundRouteForm', 'destinations', 'languages'])
    },
    async created () {
        await this.initInboundRoutesDestinations();
        await this.initInboundRoutesLanguages();
        this.initializeData();
    },
    methods: {
        ...mapActions([
            'createInboundRoute',
            'updateInboundRoute',
            'initInboundRoutes',
            'initInboundRoutesDestinations',
            'initInboundRoutesLanguages'
        ]),
        initializeData () {
            this.submitted = false;
        },
        isDirectOnChange ($event) {
            if (this.isDirect) {
                this.inboundRouteForm.tipo_destino = null;
                this.inboundRouteForm.destino = null;
            } else {
                this.inboundRouteForm.tipo_destino = AGENT;
            }
        },
        async save (isFormValid) {
            this.submitted = true;
            if (!isFormValid) {
                return null;
            }
            const idDestino = this.inboundRouteForm.destino;
            this.inboundRouteForm.destino = this.destinations_filter.find(d => d.id === idDestino);
            var response = null;
            if (this.formToCreate) {
                response = await this.createInboundRoute(this.inboundRouteForm);
            } else {
                response = await this.updateInboundRoute({
                    id: this.inboundRouteForm.id,
                    data: this.inboundRouteForm
                });
            }
            const { status, message } = response;
            if (status === HTTP_STATUS.SUCCESS) {
                await this.initInboundRoutes();
                this.$router.push({ name: 'supervisor_inbound_routes' });
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.success_notification'),
                        message,
                        this.$t('globals.icon_success')
                    )
                );
            } else {
                this.inboundRouteForm.destino = idDestino;
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.error_notification'),
                        message,
                        this.$t('globals.icon_error')
                    )
                );
            }
        }
    },
    watch: {
        formToCreate: {
            handler () {},
            deep: true,
            immediate: true
        },
    }
};
</script>
