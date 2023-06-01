<template>
  <div>
    <div>
      <h3 class="text-center title title_color">
        <b>{{ $t("views.register_server.title").toUpperCase() }}</b>
      </h3>
      <Image
        :src="iconUrl"
        alt="OML Logo"
        class="flex justify-content-center mt-2"
        width="210"
      />
      <br>
      <div class="text-center">
        <b>{{ $t("views.register_server.info1") }}</b><br>
        <b>{{ $t("views.register_server.info2") }}</b>
      </div>
      <br>
      <div>
        {{ $t("views.register_server.info3") }}
        <ul>
          <li>{{ $t("views.register_server.info6") }}</li>
          <li>{{ $t("views.register_server.info7") }}</li>
          <li>{{ $t("views.register_server.info8") }}</li>
          <li>{{ $t("views.register_server.info9") }}</li>
          <li>{{ $t("views.register_server.info10") }}</li>
          <li>{{ $t("views.register_server.info11") }}</li>
        </ul>
      </div>
      <div class="text-center">
        {{ $t("views.register_server.info4") }}<br>
        <small><b>{{ $t("views.register_server.info5") }}</b></small>
      </div>
    </div>
    <br>
    <div>
      <div class="fluid grid formgrid">
        <div class="field col-6">
          <label
            id="name"
            :class="{
              'p-error': v$.form.name.$invalid && submitted,
            }"
            >{{ $t("models.register_server.name") }}*</label
          >
          <div class="p-inputgroup">
            <span class="p-inputgroup-addon">
              <i class="pi pi-list"></i>
            </span>
            <InputText
              id="name"
              :class="{
                'p-invalid': v$.form.name.$invalid && submitted,
              }"
              class="w-full"
              :placeholder="$t('forms.register_server.enter_name')"
              v-model="v$.form.name.$model"
            />
          </div>
          <small
            v-if="
              (v$.form.name.$invalid && submitted) ||
              v$.form.name.$pending.$response
            "
            class="p-error"
            >{{
              v$.form.name.required.$message.replace(
                "Value",
                $t("models.register_server.name")
              )
            }}</small
          >
        </div>
        <div class="field col-6">
          <label
            id="password"
            :class="{
              'p-error': v$.form.password.$invalid && submitted,
            }"
            >{{ $t("models.register_server.password") }}*</label
          >
          <div class="p-inputgroup">
            <span class="p-inputgroup-addon">
              <i class="pi pi-lock-open"></i>
            </span>
            <Password
              id="password"
              :toggleMask="true"
              :feedback="false"
              :class="{
                'p-invalid': v$.form.password.$invalid && submitted,
              }"
              :placeholder="$t('forms.register_server.enter_password')"
              v-model="v$.form.password.$model"
            />
          </div>
          <small
            v-if="
              (v$.form.password.$invalid && submitted) ||
              v$.form.password.$pending.$response
            "
            class="p-error"
            >{{
              v$.form.password.required.$message.replace(
                "Value",
                $t("models.register_server.password")
              )
            }}</small
          >
        </div>
      </div>
      <div class="fluid grid formgrid">
        <div class="field col-6">
          <label
            id="email"
            :class="{
              'p-error': v$.form.email.$invalid && submitted,
            }"
            >{{ $t("models.register_server.email") }}*</label
          >
          <div class="p-inputgroup">
            <span class="p-inputgroup-addon">
              <i class="pi pi-at"></i>
            </span>
            <InputText
              id="email"
              :class="{
                'p-invalid': v$.form.email.$invalid && submitted,
              }"
              :placeholder="$t('forms.register_server.enter_email')"
              v-model="v$.form.email.$model"
            />
          </div>
          <small
            v-if="
              (v$.form.email.$invalid && submitted) ||
              v$.form.email.$pending.$response
            "
            class="p-error"
          >
            <div v-if="v$.form.email.$errors">
              <span v-if="v$.form.email.required.$invalid">
                {{
                  v$.form.email.required.$message.replace(
                    "Value",
                    $t("models.register_server.email")
                  )
                }}
              </span>
              <span v-if="v$.form.email.email.$invalid">
                {{
                  v$.form.email.email.$message.replace(
                    "Value",
                    $t("models.register_server.email")
                  )
                }}
              </span>
            </div>
          </small>
        </div>
        <div class="field col-6">
          <label id="phone">{{ $t("models.register_server.phone") }}</label>
          <div class="p-inputgroup">
            <span class="p-inputgroup-addon">
              <i class="pi pi-phone"></i>
            </span>
            <InputText
              id="phone"
              :placeholder="$t('forms.register_server.enter_phone')"
              v-model="form.phone"
            />
          </div>
        </div>
      </div>
      <br>
      <div class="fluid grid formgrid">
        <div class="field col-6">
          <Button
            class="p-button-danger p-button-outlined mr-2 btn_border w-full"
            @click="cancel"
            :label="$t('globals.cancel')"
          />
        </div>
        <div class="field col-6">
          <Button
            :label="$t('globals.register')"
            :loading="isLoading"
            class="w-full btn_border"
            @click="save(!v$.$invalid)"
          />
        </div>
      </div>
      <div class="fluid grid formgrid">
        <div class="field col-12 flex justify-content-center">
          <Button
            class="p-button-link"
            @click="privacyPolicies"
            :label="$t('views.register_server.privacy_policies')"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { required, email } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { mapActions, mapState } from 'vuex';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            form: {
                name: { required },
                email: { required, email },
                password: { required }
            }
        };
    },
    inject: ['$helpers'],
    data () {
        return {
            form: {
                name: '',
                email: '',
                password: '',
                phone: ''
            },
            isLoading: false,
            submitted: false
        };
    },
    created () {
        this.initializeData();
    },
    computed: {
        ...mapState(['registerServer']),
        iconUrl () {
            return require('@/assets/oml_logo.png');
        }
    },
    methods: {
        ...mapActions(['createRegisterServer', 'initRegisterServer']),
        initializeData () {
            this.initFormData();
            this.submitted = false;
        },
        privacyPolicies () {
            window.open('https://www.omnileads.net/en/terms-and-conditions', '_blank');
        },
        cancel () {
            this.initFormData();
            this.submitted = false;
            const event = new CustomEvent('onCloseModalRegisterServerPopUpEvent');
            window.parent.document.dispatchEvent(event);
        },
        initFormData () {
            this.form.name = this.registerServer?.name;
            this.form.email = this.registerServer?.email;
            this.form.password = this.registerServer?.password;
            this.form.phone = this.registerServer?.phone;
        },
        async save (isFormValid) {
            this.submitted = true;
            if (!isFormValid) {
                return null;
            }
            var response = null;
            this.isLoading = true;
            this.$swal.fire({
                title: this.$t('globals.processing_request'),
                timerProgressBar: true,
                allowOutsideClick: false,
                didOpen: () => {
                    this.$swal.showLoading();
                }
            });
            this.form.client = this.form?.name;
            response = await this.createRegisterServer(this.form);
            this.$swal.close();
            this.isLoading = false;
            const { status, message } = response;
            if (status === 'SUCCESS') {
                await this.initRegisterServer();
                const event = new CustomEvent('onSuccessRegisterServerEvent');
                window.parent.document.dispatchEvent(event);
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
        registerServer: {
            handler () {
                this.initFormData();
            },
            deep: true,
            immediate: true
        }
    }
};
</script>

<style scoped>
.btn_border {
  border-radius: 25px;
}
.title {
  border: 5px solid #4caf50;
  border-radius: 25px;
  padding: 7px;
}
.title_color {
  color: #4caf50;
}
</style>
