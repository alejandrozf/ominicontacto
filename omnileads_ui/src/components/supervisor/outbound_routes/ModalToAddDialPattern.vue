<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '35vw' }"
    :closable="false"
    :modal="false"
  >
    <template #header>
      <h2>{{ formToCreate ? $t("views.dial_pattern.new_title") : $t("views.dial_pattern.edit_title") }}</h2>
    </template>
    <div class="card">
      <div class="grid formgrid">
        <div class="field col-12">
          <label id="dial_pattern_prepend">{{
            $t("models.dial_pattern.prepend")
          }}</label>
          <div class="p-inputgroup mt-2">
            <InputText
              id="dial_pattern_prepend"
              :placeholder="$t('forms.dial_pattern.enter_pattern')"
              v-model="dialPatternForm.prepend"
            />
          </div>
        </div>
        <div class="field col-12">
          <label id="dial_pattern_prefix"
            :class="{
              'p-error':
                repeatedMatchPattern
            }"
          >{{
            $t("models.dial_pattern.prefix")
          }}</label>
          <div class="p-inputgroup mt-2">
            <InputText
              id="dial_pattern_prefix"
              :class="{
                'p-invalid':
                  repeatedMatchPattern
              }"
              @input="inputPatternEvent"
              :placeholder="$t('forms.dial_pattern.enter_pattern')"
              v-model="dialPatternForm.prefix"
            />
          </div>
          <small v-if="repeatedMatchPattern" class="p-error"
            >{{ $t('forms.outbound_route.validations.repeated_dial_pattern_prefix') }}</small
          >
        </div>
        <div class="field col-12">
          <label
            id="dial_pattern_match_pattern"
            :class="{
              'p-error':
                (v$.dialPatternForm.match_pattern.$invalid && submitted) ||
                repeatedMatchPattern,
            }"
            >{{ $t("models.dial_pattern.pattern") }}*</label
          >
          <div class="p-inputgroup mt-2">
            <span class="p-inputgroup-addon">
              <i class="pi pi-list"></i>
            </span>
            <InputText
              id="dial_pattern_match_pattern"
              :class="{
                'p-invalid':
                  (v$.dialPatternForm.match_pattern.$invalid && submitted) ||
                  repeatedMatchPattern,
              }"
              @input="inputPatternEvent"
              :placeholder="$t('forms.dial_pattern.enter_pattern')"
              v-model="v$.dialPatternForm.match_pattern.$model"
            />
          </div>
          <small
            v-if="
              (v$.dialPatternForm.match_pattern.$invalid && submitted) ||
              v$.dialPatternForm.match_pattern.$pending.$response
            "
            class="p-error"
            >{{
              v$.dialPatternForm.match_pattern.required.$message.replace(
                "Value",
                $t("models.dial_pattern.pattern")
              )
            }}</small
          >
          <small v-if="repeatedMatchPattern" class="p-error"
            > {{ $t('forms.outbound_route.validations.repeated_dial_pattern_rule') }}</small
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
import { mapActions } from 'vuex';

export default {
    setup: () => ({ v$: useVuelidate({ $scope: false }) }),
    validations () {
        return {
            dialPatternForm: {
                match_pattern: { required }
            }
        };
    },
    inject: ['$helpers'],
    props: {
        dialPatterns: {
            type: Array,
            default: () => []
        },
        dialPattern: {
            type: Object,
            default: () => null
        },
        showModal: {
            type: Boolean,
            default: false
        },
        formToCreate: {
            type: Boolean,
            default: true
        }
    },
    data () {
        return {
            submitted: false,
            repeatedMatchPattern: false,
            dialPatternForm: {
                id: null,
                prepend: null,
                prefix: null,
                match_pattern: null
            }
        };
    },
    created () {
        this.initializeData();
    },
    methods: {
        ...mapActions(['addDialPattern', 'editDialPattern']),
        initializeData () {
            this.submitted = false;
            this.repeatedMatchPattern = false;
            this.dialPatternForm = {
                id: null,
                prepend: null,
                prefix: null,
                match_pattern: null
            };
        },
        initDialPatternForm () {
            if (this.dialPattern) {
                this.dialPatternForm.id = this.dialPattern.id;
                this.dialPatternForm.prepend = this.dialPattern.prepend;
                this.dialPatternForm.prefix = this.dialPattern.prefix;
                this.dialPatternForm.match_pattern = this.dialPattern.match_pattern;
            }
        },
        closeModal () {
            this.$emit('handleDialPatternModalEvent', false, true, null);
            this.initializeData();
        },
        inputPatternEvent () {
            this.repeatedMatchPattern = this.dialPatterns.find(
                (dp) => (dp.match_pattern === this.dialPatternForm.match_pattern && dp.prefix === this.dialPatternForm.prefix)
            );
        },
        async save (isFormValid) {
            this.submitted = true;
            if (!isFormValid || this.repeatedMatchPattern) {
                return null;
            }
            if (this.formToCreate) {
                this.addDialPattern(this.dialPatternForm);
            } else {
                this.editDialPattern(this.dialPatternForm);
            }
            this.closeModal();
        }
    },
    watch: {
        dialPatterns: {
            handler () {},
            deep: true,
            immediate: true
        },
        dialPattern: {
            handler () {
                this.initDialPatternForm();
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
