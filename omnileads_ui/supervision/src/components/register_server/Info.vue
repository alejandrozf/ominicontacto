<template>
  <Card>
    <template #title>
      <div class="flex justify-content-center">
        {{ $t("views.register_server.detail.title") }}
      </div>
    </template>
    <template #subtitle>
      <div class="text-center">
        <Tag
          icon="pi pi-user"
          severity="info"
          rounded
          :value="
            $t('views.register_server.detail.user') +
              ': ' +
              registerServerAdminName || '----'
          "
        ></Tag
        ><br />
        <Tag
          v-if="registerServerStatus"
          style="margin-top: 5px"
          icon="pi pi-check-circle"
          severity="success"
          rounded
          :value="
            registerServerStatus
              ? $t('views.register_server.detail.already_register')
              : '----'
          "
        ></Tag>
      </div>
    </template>
    <template #content>
      <ul>
        <li>
          <i class="pi pi-user"></i>
          <b>{{ $t("models.register_server.name") }}</b
          >: {{ registerServer.name || "----" }}
        </li>
        <li>
          <i class="pi pi-at"></i>
          <b>{{ $t("models.register_server.email") }}</b
          >: {{ registerServer.email || "----" }}
        </li>
        <li>
          <i class="pi pi-phone"></i>
          <b>{{ $t("models.register_server.phone") }}</b
          >: {{ registerServer.phone || "----" }}
        </li>
        <li>
          <i class="pi pi-lock-open"></i>
          <b>{{ $t("models.register_server.password") }}</b
          >:
          <Password
            :value="registerServer.password"
            :feedback="false"
            disabled
            toggleMask
          />
        </li>
      </ul>
    </template>
    <template #footer>
      <div class="fluid grid formgrid">
        <div class="field col-6">
          <Button
            class="p-button-secondary p-button-outlined mr-2 w-full btn_border"
            @click="close()"
            :label="$t('globals.close')"
          />
        </div>
        <div class="field col-6">
          <Button
            class="w-full btn_border"
            @click="resendKey()"
            :loading="isLoading"
            :label="$t('views.register_server.detail.resend_key')"
          />
        </div>
      </div>
    </template>
  </Card>
</template>

<script>
import { mapActions, mapState } from 'vuex';

export default {
    inject: ['$helpers'],
    data () {
        return {
            isLoading: false
        };
    },
    computed: {
        ...mapState([
            'registerServer',
            'registerServerStatus',
            'registerServerAdminName'
        ])
    },
    methods: {
        ...mapActions(['resendKeyRegisterServer']),
        close () {
            const event = new CustomEvent('onCloseModalRegisterServerPopUpEvent');
            window.parent.document.dispatchEvent(event);
        },
        async resendKey () {
            this.isLoading = true;
            this.$swal.fire({
                title: this.$t('globals.processing_request'),
                timerProgressBar: true,
                allowOutsideClick: false,
                didOpen: () => {
                    this.$swal.showLoading();
                }
            });
            const { status } = await this.resendKeyRegisterServer();
            this.$swal.close();
            this.isLoading = false;
            let message = '';
            if (status === 'OK') {
                message = this.$t('views.register_server.detail.http_responses.res1');
            } else if (status === 'ERROR-CONN-SAAS') {
                message = this.$t('views.register_server.detail.http_responses.res2');
            } else {
                message = this.$t('views.register_server.detail.http_responses.res3');
            }
            if (status === 'OK') {
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
            handler () {},
            deep: true,
            immediate: true
        },
        registerServerAdminName: {
            handler () {},
            deep: true,
            immediate: true
        },
        registerServerStatus: {
            handler () {},
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
</style>
