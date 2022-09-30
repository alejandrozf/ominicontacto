<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '35vw' }"
    :closable="false"
    :modal="false"
  >
    <template #header>
      <h2>{{ formToCreate ? $t("views.trunk.new_title") : $t("views.trunk.edit_title") }}</h2>
    </template>
    <div class="card">
      <div class="grid formgrid">
        <div class="field col-12">
          <label
            id="pause_type"
            :class="{
              'p-error': v$.trunkForm.troncal.$invalid && submitted || trunkAlreadyExists,
            }"
            >{{ $t("globals.trunk") }}*</label
          >
          <Dropdown
            v-model="trunkForm.troncal"
            class="w-full mt-2"
            :class="{
              'p-invalid': v$.trunkForm.troncal.$invalid && submitted || trunkAlreadyExists,
            }"
            :options="trunks"
            placeholder="-----"
            optionLabel="nombre"
            optionValue="id"
            @change='trunkChangeEvent'
            :emptyFilterMessage="$t('globals.without_data')"
            :filter="true"
            v-bind:filterPlaceholder="
              $t('globals.find_by', { field: $tc('globals.name') }, 1)
            "
          />
          <small
            v-if="
              (v$.trunkForm.troncal.$invalid && submitted) || v$.trunkForm.troncal.$pending.$response
            "
            class="p-error"
            >{{
              v$.trunkForm.troncal.required.$message.replace("Value", $t("globals.trunk"))
            }}</small
          >
          <small
            v-if="trunkAlreadyExists"
            class="p-error"
            >{{
                $t('forms.outbound_route.validations.trunk_already_exists')
            }}</small
          >
        </div>
      </div>
    </div>
    <template #footer>
      <div class="flex justify-content-end flex-wrap">
        <Button
          class="p-button-danger p-button-outlined mr-2"
          :label="$t('globals.cancel')"
          @click="closeModal"
        />
        <Button :label="$t('globals.save')" @click="save(!v$.$invalid)" />
      </div>
    </template>
  </Dialog>
</template>

<script>
import { useVuelidate } from '@vuelidate/core';
import { required } from '@vuelidate/validators';
import { mapActions, mapState } from 'vuex';

export default {
    setup: () => ({ v$: useVuelidate({ $scope: false }) }),
    validations () {
        return {
            trunkForm: {
                troncal: { required }
            }
        };
    },
    inject: ['$helpers'],
    props: {
        trunks: {
            type: Array,
            default: () => []
        },
        trunk: {
            type: Object,
            default: () => null
        },
        formToCreate: {
            type: Boolean,
            default: true
        },
        showModal: {
            type: Boolean,
            default: false
        }
    },
    data () {
        return {
            submitted: false,
            trunkAlreadyExists: false,
            trunkForm: {
                id: null,
                troncal: null
            }
        };
    },
    async created () {
        await this.initializeData();
    },
    computed: {
        ...mapState(['outboundRoute'])
    },
    methods: {
        ...mapActions(['addTrunk', 'editTrunk']),
        initializeData () {
            this.submitted = false;
            this.trunkAlreadyExists = false;
            this.trunkForm = {
                id: null,
                troncal: null
            };
        },
        closeModal () {
            this.$emit('handleTrunkModalEvent', false, true, null);
            this.initializeData();
        },
        trunkChangeEvent () {
            this.trunkAlreadyExists = this.outboundRoute.troncales.find((t) => t.troncal === this.trunkForm.troncal);
        },
        initTrunkForm () {
            if (this.trunk) {
                this.trunkForm.id = this.trunk.id;
                this.trunkForm.troncal = this.trunk.troncal;
            }
        },
        async save (isFormValid) {
            this.submitted = true;
            if (!isFormValid || this.trunkAlreadyExists) {
                return null;
            }
            if (this.formToCreate) {
                this.addTrunk(this.trunkForm);
            } else {
                this.editTrunk(this.trunkForm);
            }
            this.closeModal();
        }
    },
    watch: {
        trunks: {
            handler () {},
            deep: true,
            immediate: true
        },
        trunk: {
            handler () {
                this.initTrunkForm();
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
