<template>
  <div class="card">
    <div class="grid formgrid mt-4">
      <div class="field col-4">
        <label
          id="outbound_route_name"
          :class="{
            'p-error': v$.outboundRoute.nombre.$invalid && submitted || repeatedRouteName || invalidRouteName,
          }"
          >{{ $t("models.outbound_route.name") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <InputText
            id="outbound_route_name"
            :class="{
              'p-invalid': v$.outboundRoute.nombre.$invalid && submitted || repeatedRouteName || invalidRouteName,
            }"
            @input="inputRouteNameEvent"
            :placeholder="$t('forms.outbound_route.enter_name')"
            v-model="v$.outboundRoute.nombre.$model"
          />
        </div>
        <small
          v-if="
            (v$.outboundRoute.nombre.$invalid && submitted) ||
            v$.outboundRoute.nombre.$pending.$response
          "
          class="p-error"
          >{{
            v$.outboundRoute.nombre.required.$message.replace(
              "Value",
              $t("models.outbound_route.name")
            )
          }}</small
        >
        <small
          v-if="repeatedRouteName"
          class="p-error"
          >{{
            $t('forms.outbound_route.validations.repeated_route_name')
          }}</small
        >
        <small
          v-if="invalidRouteName"
          class="p-error"
          >{{
            $t('forms.outbound_route.validations.invalid_route_name')
          }}</small
        >
      </div>
      <div class="field col-4">
        <label
          id="outbound_route_ring_time"
          :class="{
            'p-error': v$.outboundRoute.ring_time.$invalid && submitted,
          }"
          >{{ $t("models.outbound_route.ring_time") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-bell"></i>
          </span>
          <InputText
            id="outbound_route_ring_time"
            :class="{
              'p-invalid': v$.outboundRoute.ring_time.$invalid && submitted,
            }"
            :placeholder="$t('forms.outbound_route.enter_ring_time')"
            v-model="v$.outboundRoute.ring_time.$model"
          />
        </div>
        <small>
          {{ $t('globals.in_seconds')}}
        </small>
        <small
          v-if="
            (v$.outboundRoute.ring_time.$invalid && submitted) ||
            v$.outboundRoute.ring_time.$pending.$response
          "
          class="p-error"
          >{{
            v$.outboundRoute.ring_time.required.$message.replace(
              "Value",
              $t("models.outbound_route.ring_time")
            )
          }}</small
        >
      </div>
      <div class="field col-4">
        <label
          id="outbound_route_dial_options"
          :class="{
            'p-error': v$.outboundRoute.dial_options.$invalid && submitted,
          }"
          >{{ $t("models.outbound_route.dial_options") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <InputText
            id="outbound_route_dial_options"
            :class="{
              'p-invalid': v$.outboundRoute.dial_options.$invalid && submitted,
            }"
            :placeholder="$t('forms.outbound_route.enter_dial_option')"
            v-model="v$.outboundRoute.dial_options.$model"
          />
        </div>
        <small
          v-if="
            (v$.outboundRoute.dial_options.$invalid && submitted) ||
            v$.outboundRoute.dial_options.$pending.$response
          "
          class="p-error"
          >{{
            v$.outboundRoute.dial_options.required.$message.replace(
              "Value",
              $t("models.outbound_route.dial_options")
            )
          }}</small
        >
      </div>
    </div>
    <div class="grid formgrid mt-4">
      <div class="field col-8">
        <h2>{{ $tc('globals.dial_pattern', 2) }}</h2>
        <InlineMessage v-if="emptyDialPatterns" severity="warn" class="mb-3">{{
          $t("forms.outbound_route.validations.not_empty_dial_patterns")
        }}</InlineMessage>
        <DialPatternsTable
          :dialPatterns="outboundRoute.patrones_de_discado"
          @handleDialPatternModalEvent="handleDialPatternModal"
        />
      </div>
      <div class="field col-4">
        <h2>{{ $tc('globals.trunk', 2) }}</h2>
        <InlineMessage v-if="emptyTrunks" severity="warn" class="mb-3">{{
          $t("forms.outbound_route.validations.not_empty_trunks")
        }}</InlineMessage>
        <SipTrunksTable
          :trunks="filteredTrunksToList"
          @handleTrunkModalEvent="handleTrunkModal"
          @initTrunksEvent="filterTrunksToList"
        />
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
    <ModalToAddDialPattern
      :dialPatterns="outboundRoute.patrones_de_discado"
      :dialPattern='dialPattern'
      :showModal="showDialPatternModal"
      :formToCreate='formToCreateDialPattern'
      @handleDialPatternModalEvent="handleDialPatternModal"
    />
    <ModalToAddTrunk
      :trunks="sipTrunks"
      :trunk='trunk'
      :showModal="showTrunkModal"
      :formToCreate='formToCreateTrunk'
      @handleTrunkModalEvent="handleTrunkModal"
    />
  </div>
</template>

<script>
import { useVuelidate } from '@vuelidate/core';
import { required } from '@vuelidate/validators';
import { mapActions, mapState } from 'vuex';
import DialPatternsTable from '@/components/supervisor/outbound_routes/DialPatternsTable';
import SipTrunksTable from '@/components/supervisor/outbound_routes/SipTrunksTable';
import ModalToAddDialPattern from '@/components/supervisor/outbound_routes/ModalToAddDialPattern';
import ModalToAddTrunk from '@/components/supervisor/outbound_routes/ModalToAddTrunk';
import { HTTP_STATUS } from '@/globals';

export default {
    setup: () => ({ v$: useVuelidate({ $scope: false }) }),
    validations () {
        return {
            outboundRoute: {
                nombre: { required },
                ring_time: { required },
                dial_options: { required }
            }
        };
    },
    components: {
        DialPatternsTable,
        SipTrunksTable,
        ModalToAddDialPattern,
        ModalToAddTrunk
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
            showDialPatternModal: false,
            emptyDialPatterns: false,
            emptyTrunks: false,
            showTrunkModal: false,
            invalidRouteName: false,
            repeatedRouteName: false,
            filteredTrunks: [],
            filteredTrunksToList: [],
            formToCreateDialPattern: true,
            dialPattern: null,
            formToCreateTrunk: true,
            trunk: null
        };
    },
    computed: {
        ...mapState(['outboundRoute', 'sipTrunks', 'outboundRoutes'])
    },
    async created () {
        await this.initializeData();
        await this.initOutboundRoutes();
        await this.initOutboundRouteSipTrunks();
        await this.filterTrunksToList();
    },
    methods: {
        ...mapActions([
            'createOutboundRoute',
            'updateOutboundRoute',
            'initOutboundRoutes',
            'initOutboundRouteSipTrunks',
            'initDialPatternForm',
            'initTrunkForm'
        ]),
        initializeData () {
            this.submitted = false;
            this.showDialPatternModal = false;
            this.emptyDialPatterns = false;
            this.emptyTrunks = false;
            this.showTrunkModal = false;
            this.repeatedRouteName = false;
            this.invalidRouteName = false;
            this.filteredTrunks = [];
            this.filteredTrunksToList = [];
            this.formToCreateDialPattern = true;
            this.dialPattern = null;
            this.formToCreateTrunk = true;
            this.trunk = null;
        },
        filterTrunks () {
            const ids = this.outboundRoute.troncales.map((t) => t.troncal);
            this.filteredTrunks = this.sipTrunks.filter((t) => !ids.includes(t.id));
        },
        filterTrunksToList () {
            const ids = this.outboundRoute.troncales.map((t) => t.troncal);
            this.filteredTrunksToList = this.sipTrunks.filter((t) => ids.includes(t.id));
        },
        checkEmptyTrunks () {
            this.emptyTrunks = this.outboundRoute.troncales.length === 0;
        },
        checkEmptyDialPatterns () {
            this.emptyDialPatterns =
        this.outboundRoute.patrones_de_discado.length === 0;
        },
        inputRouteNameEvent () {
            this.repeatedRouteName = this.outboundRoutes.find(
                (or) => or.nombre === this.outboundRoute.nombre
            );
            var re = new RegExp('^[a-zA-Z0-9_]+$');
            this.invalidRouteName = !re.test(this.outboundRoute.nombre);
        },
        handleDialPatternModal (showModal, formToCreate = true, dialPattern = null) {
            this.showDialPatternModal = showModal;
            this.formToCreateDialPattern = formToCreate;
            this.dialPattern = dialPattern;
            this.initDialPatternForm(dialPattern);
        },
        handleTrunkModal (showModal, formToCreate = true, trunk = null) {
            this.showTrunkModal = showModal;
            this.formToCreateTrunk = formToCreate;
            this.trunk = trunk ? this.outboundRoute.troncales.find((t) => t.troncal === trunk.id) : null;
            this.initTrunkForm(this.trunk);
            // this.filterTrunks();
            this.filterTrunksToList();
        },
        async save (isFormValid) {
            this.submitted = true;
            this.checkEmptyTrunks();
            this.checkEmptyDialPatterns();
            if (!isFormValid || this.emptyDialPatterns || this.emptyTrunks || this.repeatedRouteName || this.invalidRouteName) {
                return null;
            }
            var response = null;
            if (this.formToCreate) {
                response = await this.createOutboundRoute(this.outboundRoute);
            } else {
                response = await this.updateOutboundRoute({
                    id: this.outboundRoute.id,
                    data: this.outboundRoute
                });
            }
            const { status, message } = response;
            if (status === HTTP_STATUS.SUCCESS) {
                await this.initOutboundRoutes();
                this.$router.push({ name: 'supervisor_outbound_routes' });
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.success_notification'),
                        message,
                        this.$t('globals.icon_success')
                    )
                );
            } else {
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
        }
    }
};
</script>
