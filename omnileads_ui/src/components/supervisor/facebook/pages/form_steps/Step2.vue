<template>
  <div class="card">
    <div class="grid formgrid">
      <div class="field col-12">
        <Fieldset>
          <template #legend>
            {{ $t("views.facebook.page.step2.webhook") }}
          </template>
          <div>
            <label
              :class="{
                'p-error': v$.supFacebookPage.verify_token.$invalid && submitted,
              }"
              > 
              {{ $t("models.facebook.page.verify_token") }}*</label>
            <div class="p-inputgroup mt-2">
              <span class="p-inputgroup-addon">
                <i class="pi pi-phone"></i>
              </span>
              <InputText
                :class="{
                  'p-invalid': v$.supFacebookPage.verify_token.$invalid && submitted,
                }"
                v-model="v$.supFacebookPage.verify_token.$model"
              />
            </div>
            <small
              v-if="
                (v$.supFacebookPage.verify_token.$invalid && submitted) ||
                v$.supFacebookPage.verify_token.$pending.$response
              "
              class="p-error"
              >
              {{
                v$.supFacebookPage.verify_token.required.$message.replace(
                  "Value",
                  $t("models.facebook.page.verify_token")
                )
              }}
            </small>
          </div>
        </Fieldset>
      </div>
    </div>
    <div class="grid formgrid mt-4">
      <div class="field col-12">
        <Fieldset>
          <template #legend>
            {{ $t("views.facebook.page.step2.page_info") }}
          </template>
          <div class="grid formgrid">
            <div class="field col-6">
              <label
                :class="{
                  'p-error':
                    v$.supFacebookPage.access_token.$invalid &&
                    submitted,
                }"
                >{{ $t("models.facebook.page.access_token") }}*</label
              >
              <div class="p-inputgroup">
                <span class="p-inputgroup-addon">
                  <i class="pi pi-list"></i>
                </span>
                <InputText
                  :class="{
                    'p-invalid':
                      v$.supFacebookPage.access_token.$invalid &&
                      submitted,
                  }"
                  :placeholder="$t('forms.form.enter_value')"
                  v-model="v$.supFacebookPage.access_token.$model"
                />
              </div>
              <small
                v-if="
                  (v$.supFacebookPage.access_token.$invalid &&
                    submitted) ||
                  v$.supFacebookPage.access_token.$pending.$response
                "
                class="p-error"
                >{{
                  v$.supFacebookPage.access_token.required.$message.replace(
                    "Value",
                    $t("models.facebook.page.access_token")
                  )
                }}</small
              >
            </div>
            <div class="field col-6">
              <label
                :class="{
                  'p-error':
                    v$.supFacebookPage.app_id.$invalid &&
                    submitted,
                }"
                >{{ $t("models.facebook.page.app_id") }}*</label
              >
              <div class="p-inputgroup">
                <span class="p-inputgroup-addon">
                  <i class="pi pi-list"></i>
                </span>
                <InputText
                  :class="{
                    'p-invalid':
                      v$.supFacebookPage.app_id.$invalid &&
                      submitted,
                  }"
                  :placeholder="$t('forms.form.enter_value')"
                  v-model="v$.supFacebookPage.app_id.$model"
                />
              </div>
              <small
                v-if="
                  (v$.supFacebookPage.app_id.$invalid &&
                    submitted) ||
                  v$.supFacebookPage.app_id.$pending.$response
                "
                class="p-error"
                >{{
                  v$.supFacebookPage.app_id.required.$message.replace(
                    "Value",
                    $t("models.facebook.page.app_id")
                  )
                }}</small
              >
            </div>
            <div class="field col-6">
              <label
                :class="{
                  'p-error':
                    v$.supFacebookPage.page_id.$invalid &&
                    submitted,
                }"
                >{{ $t("models.facebook.page.page_id") }}*</label
              >
              <div class="p-inputgroup">
                <span class="p-inputgroup-addon">
                  <i class="pi pi-list"></i>
                </span>
                <InputText
                  :class="{
                    'p-invalid':
                      v$.supFacebookPage.page_id.$invalid &&
                      submitted,
                  }"
                  :placeholder="$t('forms.form.enter_value')"
                  v-model="v$.supFacebookPage.page_id.$model"
                />
              </div>
              <small
                v-if="
                  (v$.supFacebookPage.page_id.$invalid &&
                    submitted) ||
                  v$.supFacebookPage.page_id.$pending.$response
                "
                class="p-error"
                >{{
                  v$.supFacebookPage.page_id.required.$message.replace(
                    "Value",
                    $t("models.facebook.page.page_id")
                  )
                }}</small
              >
            </div>

          </div>
        </Fieldset>
      </div>
    </div>
    <div class="flex justify-content-between flex-wrap">
      <div class="flex align-items-center justify-content-center">
        <Button
          :label="$t('globals.back')"
          icon="pi pi-angle-left"
          icon-pos="right"
          class="mt-4 p-button-secondary"
          @click="prevPage"
        />
      </div>
      <div class="flex align-items-center justify-content-center">
        <Button
          :label="$t('globals.next')"
          icon="pi pi-angle-right"
          icon-pos="right"
          class="mt-4 p-button-secondary"
          @click="nextPage(!v$.$invalid)"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            supFacebookPage: {
                verify_token: {
                    required
                },
                access_token: {
                    required
                },
                app_id: {
                    required
                },
                page_id: {
                    required
                }
            }
        };
    },
    inject: ['$helpers'],
    data () {
        return {
            submitted: false
        };
    },
    computed: {
        ...mapState(['supFacebookPage'])
    },
    methods: {
        ...mapActions(['']),
        validFields () {
            var formErrors = [];
            if (!this.supFacebookPage.name || this.supFacebookPage.name === '') {
                formErrors.push(
                    this.$tc('forms.facebook.page.validations.field_is_required', {
                        field: this.$t('models.facebook.page.name')
                    })
                );
            }
            if (formErrors.length > 0) {
                var errors = '<ul>';
                formErrors.forEach((e) => {
                    errors += `<li>${e}</li>`;
                });
                errors += '<ul/>';
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.warning_notification'),
                        null,
                        this.$t('globals.icon_warning'),
                        null,
                        errors
                    )
                );
                return false;
            }
            return true;
        },
        nextPage (isFormValid) {
            this.submitted = true;
            if (isFormValid) {
                if (this.validFields()) {
                    this.$emit('next-page', { pageIndex: 1 });
                }
                return null;
            } else {
                return null;
            }
        },
        prevPage () {
            this.$emit('prev-page', { pageIndex: 1 });
        }
    },
    watch: {
        supWhatsappLine: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
