<template>
  <Dialog
    :visible="showModal"
    :modal="true"
    :closable="false"
    :style="{ width: '96vw', height: '100vh', maxHeight: '100vh' }"
    :contentStyle="{ padding: '0', overflow: 'hidden', height: '100%' }"
    class="whatsapp-flow-builder"
  >
    <template #header>
      <div class="flow-builder-header">
        <div>
          <h2 class="flow-builder-title">{{ $t('views.whatsapp.line.flow.title') }}</h2>
          <small>{{ $t('views.whatsapp.line.flow.subtitle') }}</small>
        </div>
        <div class="flow-builder-header__actions">
          <Button
            icon="pi pi-plus"
            :label="$t('views.whatsapp.line.flow.add_block')"
            @click="addNode"
          />
        </div>
      </div>
    </template>
    <div
      ref="canvasWrapper"
      class="flow-builder-canvas-wrapper flow-builder-canvas-wrapper--interactive"
      @mousedown="startPan"
      @wheel.prevent="handleWheel"
    >
      <div class="flow-builder-toolbar">
        <Button
          v-if="linkingOption"
          icon="pi pi-times"
          class="p-button-text p-button-danger"
          :label="$t('views.whatsapp.line.flow.cancel_link')"
          @click="cancelLinking"
        />
        <Button icon="pi pi-search-minus" class="p-button-text" @click="zoomOut" />
        <span>{{ Math.round(scale * 100) }}%</span>
        <Button icon="pi pi-search-plus" class="p-button-text" @click="zoomIn" />
        <Button icon="pi pi-refresh" class="p-button-text" @click="resetViewport" />
      </div>
      <div
        ref="canvasStage"
        class="flow-builder-stage"
        :class="{
          'flow-builder-stage--panning': isPanning,
          'flow-builder-stage--dragging': Boolean(draggingNodeId)
        }"
        :style="stageStyle"
      >
        <svg class="flow-builder-arrows" :width="canvasSize.width" :height="canvasSize.height">
          <defs>
            <marker
              id="flow-arrow-head"
              markerWidth="10"
              markerHeight="10"
              refX="8"
              refY="5"
              orient="auto"
            >
              <path d="M0,0 L10,5 L0,10 z" fill="#2563eb" />
            </marker>
          </defs>
          <g v-for="arrow in arrows" :key="arrow.key">
            <path
              :d="arrow.path"
              class="flow-builder-arrow"
              marker-end="url(#flow-arrow-head)"
            />
            <text :x="arrow.labelX" :y="arrow.labelY" class="flow-builder-arrow__label">
              {{ arrow.label }}
            </text>
          </g>
        </svg>

        <div
          ref="incomingNode"
          class="flow-node flow-node--incoming"
          :style="incomingNodeStyle"
        >
          <div class="flow-node__topbar">
            <Tag severity="info" :value="$t('views.whatsapp.line.flow.incoming_message')" />
          </div>
          <div class="whatsapp-preview whatsapp-preview--incoming">
            <div class="whatsapp-preview__meta">WhatsApp</div>
            <div class="whatsapp-preview__body">
              {{ $t('views.whatsapp.line.flow.incoming_help') }}
            </div>
          </div>
        </div>

        <div
          v-for="node in nodes"
          :key="node.id_tmp"
          :ref="(el) => setNodeRef(node.id_tmp, el)"
          class="flow-node"
          :class="{
            'flow-node--selected': selectedNodeId === node.id_tmp,
            'flow-node--invalid': isNodeInvalid(node),
            'flow-node--link-target': isLinkTarget(node.id_tmp)
          }"
          :style="getNodeStyle(node)"
          @mousedown.stop="startDrag($event, node.id_tmp)"
          @click.stop="handleNodeClick(node.id_tmp)"
        >
          <div class="flow-node__topbar">
            <Tag
              v-if="node.is_main"
              severity="success"
              :value="$t('views.whatsapp.line.flow.main')"
            />
            <div class="flow-node__actions">
              <Button
                icon="pi pi-pencil"
                class="p-button-text"
                @click.stop="openEditor(node.id_tmp)"
              />
              <Button
                v-if="!node.is_main"
                icon="pi pi-trash"
                class="p-button-text p-button-danger"
                @click.stop="deleteNode(node.id_tmp)"
              />
            </div>
          </div>

          <div class="whatsapp-preview">
            <div class="whatsapp-preview__headerbar">
              <div class="whatsapp-preview__header-title">
                {{ node.menu_header || getNodeTitle(node) }}
              </div>
              <i class="pi pi-chevron-down whatsapp-preview__caret" />
            </div>
            <div class="whatsapp-preview__body">
              {{ node.menu_body || $t('views.whatsapp.line.flow.empty_body') }}
            </div>
            <div class="whatsapp-preview__meta-row">
              <small v-if="node.menu_footer" class="whatsapp-preview__footer">
                {{ node.menu_footer }}
              </small>
              <span class="whatsapp-preview__time">{{ $t('views.whatsapp.line.flow.preview_time') }}</span>
            </div>
            <div class="whatsapp-preview__button">
              <i class="pi pi-list" />
              <span>{{ node.menu_button || $t('views.whatsapp.line.flow.default_list_button') }}</span>
            </div>
          </div>

          <div class="flow-node__connections">
            <div class="flow-node__connections-header">
              <strong>{{ $t('views.whatsapp.line.flow.connections') }}</strong>
              <Button
                icon="pi pi-share-alt"
                class="p-button-text p-button-sm"
                :label="$t('views.whatsapp.line.flow.connect')"
                @click.stop="startLinkFromNode(node.id_tmp)"
              />
            </div>
            <div
              v-for="(option, optionIndex) in getInteractiveOptions(node)"
              :key="`${node.id_tmp}-link-${optionIndex}`"
              class="flow-link-row"
              :class="{ 'flow-link-row--pending': isPendingLink(node.id_tmp, optionIndex) }"
            >
              <div class="flow-link-row__content">
                <strong>{{ getOptionLabel(option, optionIndex) }}</strong>
                <small>
                  {{
                    option.destination
                      ? `${$t('views.whatsapp.line.flow.connected_to')} ${getDestinationName(option.destination)}`
                      : $t('views.whatsapp.line.flow.unlinked')
                  }}
                </small>
              </div>
              <div class="flow-link-row__actions">
                <Button
                  v-if="isInteractiveOption(option)"
                  icon="pi pi-share-alt"
                  class="p-button-text p-button-sm"
                  @click.stop="startLinkFromNode(node.id_tmp, optionIndex)"
                />
                <Button
                  v-if="isInteractiveOption(option) && option.destination"
                  icon="pi pi-times"
                  class="p-button-text p-button-sm p-button-danger"
                  @click.stop="clearOptionDestination(node.id_tmp, optionIndex)"
                />
              </div>
            </div>
            <div
              v-if="getInteractiveOptions(node).length === 0"
              class="flow-link-row flow-link-row--empty"
            >
              {{ $t('views.whatsapp.line.flow.no_links') }}
            </div>
            <small
              v-if="linkingOption && linkingOption.sourceId === node.id_tmp"
              class="flow-link-row__hint"
            >
              {{ $t('views.whatsapp.line.flow.click_target') }}
            </small>
          </div>
        </div>
      </div>
    </div>
    <template #footer>
      <div class="flow-builder-footer">
        <small>{{ $t('views.whatsapp.line.flow.drag_help') }}</small>
        <div>
          <Button
            class="p-button-text mr-2"
            :label="$t('globals.close')"
            @click="$emit('handleModalEvent', { showModal: false })"
          />
          <Button
            class="p-button-success"
            :label="$t('globals.save')"
            @click="saveFlow"
          />
        </div>
      </div>
    </template>

    <Dialog
      :visible="showEditorModal"
      :modal="true"
      :closable="false"
      :style="{ width: '680px', maxWidth: '92vw' }"
      :contentStyle="{ padding: '0', overflow: 'hidden' }"
      class="flow-node-editor"
    >
      <template #header>
        <div class="flow-editor-header">
          <div>
            <h3>{{ editingNode ? getNodeTitle(editingNode) : $t('views.whatsapp.line.flow.edit_block') }}</h3>
            <small>{{ $t('views.whatsapp.line.flow.editor_help') }}</small>
          </div>
        </div>
      </template>

      <div v-if="editingNode" class="flow-editor-modal__content">
        <TabView>
          <TabPanel header="Mensaje">
            <div class="field">
              <label class="flex justify-content-between w-full mb-1">
                <span>{{ $t('models.whatsapp.line.interactive_form.menu_header') }}</span>
                <small class="text-color-secondary">{{ editingNode.menu_header ? editingNode.menu_header.length : 0 }} / 60</small>
              </label>
              <EmojiTextInput
                v-model="editingNode.menu_header"
                inputClass="w-full"
                :maxLength="60"
                @input="refreshArrows"
              />
            </div>
            <div class="field mt-3">
              <label class="flex justify-content-between w-full mb-1">
                <span>{{ $t('models.whatsapp.line.interactive_form.menu_body') }}*</span>
                <small class="text-color-secondary">{{ editingNode.menu_body ? editingNode.menu_body.length : 0 }} / 1024</small>
              </label>
              <EmojiTextInput
                v-model="editingNode.menu_body"
                inputClass="w-full"
                :multiline="true"
                rows="4"
                :autoResize="true"
                :maxLength="1024"
                @input="refreshArrows"
              />
            </div>
            <div class="field mt-3">
              <label class="flex justify-content-between w-full mb-1">
                <span>{{ $t('models.whatsapp.line.interactive_form.menu_footer') }}</span>
                <small class="text-color-secondary">{{ editingNode.menu_footer ? editingNode.menu_footer.length : 0 }} / 60</small>
              </label>
              <EmojiTextInput
                v-model="editingNode.menu_footer"
                inputClass="w-full"
                :maxLength="60"
                @input="refreshArrows"
              />
            </div>
            <div class="field mt-3">
              <label class="flex justify-content-between w-full mb-1">
                <span>{{ $t('models.whatsapp.line.interactive_form.menu_button') }}*</span>
                <small class="text-color-secondary">{{ editingNode.menu_button ? editingNode.menu_button.length : 0 }} / 20</small>
              </label>
              <InputText v-model="editingNode.menu_button" class="w-full" @input="refreshArrows" />
            </div>
          </TabPanel>

          <TabPanel header="Respuestas">
            <div class="field">
              <label class="flex justify-content-between w-full mb-1">
                <span>{{ $t('models.whatsapp.line.interactive_form.wrong_answer') }}</span>
                <small class="text-color-secondary">{{ editingNode.wrong_answer ? editingNode.wrong_answer.length : 0 }} / 100</small>
              </label>
              <EmojiTextInput
                v-model="editingNode.wrong_answer"
                inputClass="w-full"
                :maxLength="100"
              />
            </div>
            <div class="field mt-3">
              <label class="flex justify-content-between w-full mb-1">
                <span>{{ $t('models.whatsapp.line.interactive_form.success_answer') }}</span>
                <small class="text-color-secondary">{{ editingNode.success ? editingNode.success.length : 0 }} / 100</small>
              </label>
              <EmojiTextInput
                v-model="editingNode.success"
                inputClass="w-full"
                :maxLength="100"
              />
            </div>
          </TabPanel>

          <TabPanel header="Opciones de Menú">
            <div class="flow-editor-options-header">
              <h4>{{ $t('models.whatsapp.line.interactive_form.options') }}</h4>
              <Button
                icon="pi pi-plus"
                class="p-button-sm"
                :label="$t('globals.new')"
                @click="addOption"
              />
            </div>
            <InlineMessage severity="info" class="w-full mt-2 mb-3">
              {{ $t('views.whatsapp.line.flow.meta_rows_warning') }}
            </InlineMessage>

            <div v-if="editingNode.options.length === 0" class="flow-editor__empty">
              {{ $t('forms.whatsapp.line.options.empty_options') }}
            </div>

            <div
              v-for="(option, index) in editingNode.options"
              :key="`${editingNode.id_tmp}-${index}`"
              class="flow-option"
            >
              <div class="flow-option__row">
                <div class="field">
                  <label class="flex justify-content-between w-full mb-1">
                    <span>{{ $t('models.whatsapp.line.options.value') }}*</span>
                    <small class="text-color-secondary">{{ option.value ? option.value.length : 0 }} / 24</small>
                  </label>
                  <EmojiTextInput
                    v-model="option.value"
                    inputClass="w-full"
                    :maxLength="24"
                    @input="refreshArrows"
                  />
                </div>
                <div class="field">
                  <label class="flex justify-content-between w-full mb-1">
                    <span>{{ $t('models.whatsapp.line.options.description') }}</span>
                    <small class="text-color-secondary">{{ option.description ? option.description.length : 0 }} / 72</small>
                  </label>
                  <EmojiTextInput
                    v-model="option.description"
                    inputClass="w-full"
                    :maxLength="72"
                    @input="refreshArrows"
                  />
                </div>
                <Button
                  icon="pi pi-trash"
                  class="p-button-text p-button-danger flow-option__delete"
                  @click="removeOption(index)"
                />
              </div>
              <div class="flow-option__row flow-option__row--destinations mt-2">
                <div class="field">
                  <label>{{ $t('models.whatsapp.line.options.destination_type') }}*</label>
                  <Dropdown
                    v-model="option.type_option"
                    :options="destinationTypes"
                    optionLabel="name"
                    optionValue="value"
                    class="w-full"
                    @change="handleOptionTypeChange(option)"
                  />
                </div>
                <div class="field">
                  <label>{{ $t('models.whatsapp.line.options.destination') }}*</label>
                  <Dropdown
                    v-model="option.destination"
                    :options="getDestinationOptions(option)"
                    optionLabel="name"
                    optionValue="id"
                    class="w-full"
                    @change="refreshArrows"
                  />
                </div>
              </div>
              <div
                v-if="option.type_option === DESTINATION_OPTION_TYPES.CAMPAIGN"
                class="flow-option__campaign-message mt-3"
              >
                <div class="flex align-items-center gap-2">
                  <Checkbox
                    v-model="option.send_message_before_campaign"
                    :binary="true"
                    @change="handlePreCampaignMessageToggle(option)"
                  />
                  <label class="mb-0">Mensaje previo a derivacion</label>
                </div>
                <div v-if="option.send_message_before_campaign" class="field mt-3 mb-0">
                  <label>Plantilla*</label>
                  <Dropdown
                    v-model="option.message_before_campaign"
                    :options="textMessageTemplates"
                    optionLabel="name"
                    optionValue="id"
                    class="w-full"
                  />
                </div>
              </div>
            </div>
          </TabPanel>
        </TabView>
      </div>

      <template #footer>
        <div class="flow-editor-footer">
          <Button
            class="p-button-text"
            :label="$t('globals.close')"
            @click="closeEditor"
          />
        </div>
      </template>
    </Dialog>
  </Dialog>
</template>

<script>
/* eslint-disable vue/no-mutating-props */
import { nextTick } from 'vue';
import { DESTINATION_OPTION_TYPES } from '@/globals/supervisor/whatsapp/line';
import { TEMPLATE_TYPES } from '@/globals/supervisor/whatsapp/message_template';
import EmojiTextInput from '@/components/supervisor/whatsapp/lines/options_form/EmojiTextInput.vue';

const DEFAULT_NODE_WIDTH = 320;
const DEFAULT_NODE_HEIGHT = 320;
const NODE_HORIZONTAL_GAP = 64;
const NODE_VERTICAL_GAP = 72;
const NODE_COLLISION_PADDING = 24;
const NODE_START_X = 340;
const NODE_START_Y = 90;
const NODE_COLUMNS = 3;
const INCOMING_NODE_POSITION = {
    x: 48,
    y: 220
};

export default {
    components: {
        EmojiTextInput
    },
    inject: ['$helpers'],
    props: {
        showModal: {
            type: Boolean,
            default: false
        },
        nodes: {
            type: Array,
            default: () => []
        },
        campaigns: {
            type: Array,
            default: () => []
        },
        messageTemplates: {
            type: Array,
            default: () => []
        }
    },
    data () {
        return {
            DESTINATION_OPTION_TYPES,
            selectedNodeId: null,
            editingNodeId: null,
            showEditorModal: false,
            nodeRefs: {},
            arrows: [],
            canvasSize: {
                width: 1600,
                height: 900
            },
            scale: 1,
            isPanning: false,
            panStartX: 0,
            panStartY: 0,
            scrollStartLeft: 0,
            scrollStartTop: 0,
            draggingNodeId: null,
            dragStartX: 0,
            dragStartY: 0,
            dragNodeOriginX: 0,
            dragNodeOriginY: 0,
            dragMoved: false,
            panOffsetX: 0,
            panOffsetY: 0,
            panStartOffsetX: 0,
            panStartOffsetY: 0,
            suppressClick: false,
            resolvingOverlaps: false,
            linkingOption: null,
            destinationTypes: [
                {
                    name: this.$t('forms.whatsapp.line.destination_types.campaign'),
                    value: DESTINATION_OPTION_TYPES.CAMPAIGN
                },
                {
                    name: this.$t('forms.whatsapp.line.destination_types.menu'),
                    value: DESTINATION_OPTION_TYPES.INTERACTIVE
                },
                {
                    name: this.$t('forms.whatsapp.line.destination_types.closing_menssage'),
                    value: DESTINATION_OPTION_TYPES.CLOSING_MESSAGE
                }
            ]
        };
    },
    computed: {
        editingNode () {
            return this.nodes.find((node) => node.id_tmp === this.editingNodeId) || null;
        },
        stageStyle () {
            return {
                width: `${this.canvasSize.width}px`,
                height: `${this.canvasSize.height}px`,
                transform: `scale(${this.scale}) translate(${this.panOffsetX}px, ${this.panOffsetY}px)`,
                transformOrigin: '0 0'
            };
        },
        incomingNodeStyle () {
            return {
                left: `${INCOMING_NODE_POSITION.x}px`,
                top: `${INCOMING_NODE_POSITION.y}px`
            };
        },
        flattenedCampaigns () {
            return this.campaigns.reduce((acc, group) => acc.concat(group.items || []), []);
        },
        flattenedTemplates () {
            return this.messageTemplates.reduce((acc, group) => acc.concat(group.items || []), []);
        },
        textMessageTemplates () {
            return this.messageTemplates
                .filter((group) => group.type === TEMPLATE_TYPES.TEXT)
                .reduce((acc, group) => acc.concat(group.items || []), []);
        }
    },
    mounted () {
        window.addEventListener('resize', this.refreshArrows);
        window.addEventListener('mousemove', this.handlePointerMove);
        window.addEventListener('mouseup', this.stopPointerInteraction);
        this.ensureNodes();
    },
    beforeUnmount () {
        window.removeEventListener('resize', this.refreshArrows);
        window.removeEventListener('mousemove', this.handlePointerMove);
        window.removeEventListener('mouseup', this.stopPointerInteraction);
        document.body.style.userSelect = '';
    },
    methods: {
        buildNode (isMain = false) {
            return {
                id_tmp: Date.now() + Math.floor(Math.random() * 1000),
                is_main: isMain,
                menu_header: '',
                menu_body: '',
                menu_footer: '',
                menu_button: '',
                wrong_answer: '',
                success: '',
                timeout: 0,
                options: [],
                flow_builder_x: null,
                flow_builder_y: null
            };
        },
        normalizeNode (node, index) {
            if (node.menu_header === undefined) node.menu_header = '';
            if (node.menu_body === undefined) node.menu_body = '';
            if (node.menu_footer === undefined) node.menu_footer = '';
            if (node.menu_button === undefined) node.menu_button = '';
            if (node.wrong_answer === undefined) {
                node.wrong_answer = node.wrongAnswer || '';
            }
            if (node.success === undefined) {
                node.success = node.successAnswer || '';
            }
            if (node.timeout === undefined) node.timeout = 0;
            if (!Array.isArray(node.options)) node.options = [];
            if (node.flow_builder_x === undefined) node.flow_builder_x = null;
            if (node.flow_builder_y === undefined) node.flow_builder_y = null;
            if (node.flow_builder_x === null || node.flow_builder_y === null) {
                const defaultPosition = this.buildDefaultPosition(index);
                node.flow_builder_x = defaultPosition.x;
                node.flow_builder_y = defaultPosition.y;
            }
            node.options.forEach((option) => this.normalizeOption(option));
        },
        normalizeOption (option) {
            if (option.value === undefined) option.value = '';
            if (option.description === undefined) option.description = '';
            if (option.type_option === undefined) option.type_option = null;
            if (option.destination === undefined) option.destination = null;
            if (option.send_message_before_campaign === undefined) {
                option.send_message_before_campaign = false;
            }
            if (option.message_before_campaign === undefined) {
                option.message_before_campaign = null;
            }
        },
        buildDefaultPosition (index) {
            return {
                x: NODE_START_X + ((index % NODE_COLUMNS) * (DEFAULT_NODE_WIDTH + NODE_HORIZONTAL_GAP)),
                y: NODE_START_Y + (Math.floor(index / NODE_COLUMNS) * (DEFAULT_NODE_HEIGHT + NODE_VERTICAL_GAP))
            };
        },
        ensureNodes () {
            if (!Array.isArray(this.nodes)) {
                return;
            }
            if (this.nodes.length === 0) {
                this.nodes.push(this.buildNode(true));
            }
            this.nodes.forEach((node, index) => this.normalizeNode(node, index));
            if (!this.nodes.some((node) => node.is_main) && this.nodes[0]) {
                this.nodes[0].is_main = true;
            }
            if (!this.selectedNodeId || !this.nodes.find((node) => node.id_tmp === this.selectedNodeId)) {
                this.selectedNodeId = this.nodes[0].id_tmp;
            }
            this.refreshArrows();
        },
        addNode () {
            const node = this.buildNode(false);
            this.normalizeNode(node, this.nodes.length);
            this.nodes.push(node);
            this.selectNode(node.id_tmp);
            this.refreshArrows();
        },
        deleteNode (nodeId) {
            const nextNodes = this.nodes.filter((node) => node.id_tmp !== nodeId);
            this.nodes.splice(0, this.nodes.length, ...nextNodes);
            this.nodes.forEach((node) => {
                node.options = node.options.filter((option) => !(
                    option.type_option === DESTINATION_OPTION_TYPES.INTERACTIVE &&
                    option.destination === nodeId
                ));
            });
            if (!this.nodes.some((node) => node.is_main) && this.nodes[0]) {
                this.nodes[0].is_main = true;
            }
            if (this.editingNodeId === nodeId) {
                this.closeEditor();
            }
            this.selectedNodeId = this.nodes[0] ? this.nodes[0].id_tmp : null;
            this.refreshArrows();
        },
        isNodeInvalid (node) {
            return [
                node.menu_body,
                node.menu_button
            ].some((value) => !value) || node.options.some((option) => (
                option.type_option === DESTINATION_OPTION_TYPES.CAMPAIGN &&
                option.send_message_before_campaign &&
                !option.message_before_campaign
            ));
        },
        getInteractiveOptions (node) {
            return node.options || [];
        },
        isInteractiveOption (option) {
            return option.type_option === DESTINATION_OPTION_TYPES.INTERACTIVE;
        },
        getOptionLabel (option, index) {
            return option.value || `${this.$t('views.whatsapp.line.flow.option_label')} ${index + 1}`;
        },
        getDestinationName (destinationId) {
            const node = this.nodes.find((item) => item.id_tmp === destinationId);
            return node ? this.getNodeTitle(node) : this.$t('views.whatsapp.line.flow.untitled_block');
        },
        isPendingLink (nodeId, optionIndex) {
            return Boolean(
                this.linkingOption &&
                this.linkingOption.sourceId === nodeId &&
                this.linkingOption.optionIndex === optionIndex
            );
        },
        isLinkTarget (nodeId) {
            return Boolean(
                this.linkingOption &&
                this.linkingOption.sourceId !== nodeId
            );
        },
        selectNode (nodeId) {
            this.selectedNodeId = nodeId;
            this.refreshArrows();
        },
        handleNodeClick (nodeId) {
            if (this.suppressClick) {
                this.suppressClick = false;
                return;
            }
            if (this.linkingOption) {
                this.linkOptionToNode(nodeId);
                return;
            }
            this.selectNode(nodeId);
        },
        openEditor (nodeId) {
            this.selectNode(nodeId);
            this.editingNodeId = nodeId;
            this.showEditorModal = true;
        },
        closeEditor () {
            this.showEditorModal = false;
            this.editingNodeId = null;
        },
        startLinkFromNode (nodeId, optionIndex = null) {
            const node = this.nodes.find((item) => item.id_tmp === nodeId);
            if (!node) {
                return;
            }
            const interactiveOptions = this.getInteractiveOptions(node);
            let selectedIndex = optionIndex;
            if (selectedIndex === null) {
                const freeInteractiveIndex = node.options.findIndex((option) => (
                    option.type_option === DESTINATION_OPTION_TYPES.INTERACTIVE &&
                    !option.destination
                ));
                if (freeInteractiveIndex >= 0) {
                    selectedIndex = freeInteractiveIndex;
                } else {
                    node.options.push({
                        value: `${this.$t('views.whatsapp.line.flow.option_label')} ${interactiveOptions.length + 1}`,
                        description: '',
                        type_option: DESTINATION_OPTION_TYPES.INTERACTIVE,
                        destination: null,
                        send_message_before_campaign: false,
                        message_before_campaign: null
                    });
                    selectedIndex = node.options.length - 1;
                }
            } else {
                const option = node.options[selectedIndex];
                if (!option) {
                    return;
                }
                option.type_option = DESTINATION_OPTION_TYPES.INTERACTIVE;
            }
            this.linkingOption = {
                sourceId: nodeId,
                optionIndex: selectedIndex
            };
            this.selectNode(nodeId);
            this.refreshArrows();
        },
        cancelLinking () {
            this.linkingOption = null;
        },
        linkOptionToNode (targetNodeId) {
            if (!this.linkingOption || this.linkingOption.sourceId === targetNodeId) {
                return;
            }
            const sourceNode = this.nodes.find((node) => node.id_tmp === this.linkingOption.sourceId);
            if (!sourceNode || !sourceNode.options[this.linkingOption.optionIndex]) {
                this.cancelLinking();
                return;
            }
            sourceNode.options[this.linkingOption.optionIndex].type_option = DESTINATION_OPTION_TYPES.INTERACTIVE;
            sourceNode.options[this.linkingOption.optionIndex].destination = targetNodeId;
            this.cancelLinking();
            this.refreshArrows();
        },
        clearOptionDestination (nodeId, optionIndex) {
            const node = this.nodes.find((item) => item.id_tmp === nodeId);
            if (!node || !node.options[optionIndex]) {
                return;
            }
            node.options[optionIndex].destination = null;
            this.refreshArrows();
        },
        addOption () {
            if (!this.editingNode) {
                return;
            }
            this.editingNode.options.push({
                value: '',
                description: '',
                type_option: null,
                destination: null,
                send_message_before_campaign: false,
                message_before_campaign: null
            });
            this.refreshArrows();
        },
        removeOption (index) {
            if (!this.editingNode) {
                return;
            }
            this.editingNode.options.splice(index, 1);
            this.refreshArrows();
        },
        handleOptionTypeChange (option) {
            option.destination = null;
            if (option.type_option !== DESTINATION_OPTION_TYPES.CAMPAIGN) {
                option.send_message_before_campaign = false;
                option.message_before_campaign = null;
            }
            this.refreshArrows();
        },
        handlePreCampaignMessageToggle (option) {
            if (!option.send_message_before_campaign) {
                option.message_before_campaign = null;
            }
        },
        getNodeTitle (node) {
            return node.menu_header || this.$t('views.whatsapp.line.flow.untitled_block');
        },
        getDestinationOptions (option) {
            if (option.type_option === DESTINATION_OPTION_TYPES.CAMPAIGN) {
                return this.flattenedCampaigns.map((campaign) => ({
                    id: campaign.id,
                    name: campaign.name
                }));
            }
            if (option.type_option === DESTINATION_OPTION_TYPES.CLOSING_MESSAGE) {
                return this.flattenedTemplates.map((template) => ({
                    id: template.id,
                    name: template.name
                }));
            }
            if (option.type_option === DESTINATION_OPTION_TYPES.INTERACTIVE) {
                return this.nodes
                    .filter((node) => !this.editingNode || node.id_tmp !== this.editingNode.id_tmp)
                    .map((node) => ({
                        id: node.id_tmp,
                        name: this.getNodeTitle(node)
                    }));
            }
            return [];
        },
        getNodeStyle (node) {
            return {
                left: `${node.flow_builder_x}px`,
                top: `${node.flow_builder_y}px`,
                zIndex: this.getNodeZIndex(node.id_tmp)
            };
        },
        getNodeZIndex (nodeId) {
            if (this.draggingNodeId === nodeId) {
                return 5;
            }
            if (this.selectedNodeId === nodeId) {
                return 4;
            }
            return 2;
        },
        setNodeRef (nodeId, el) {
            if (el) {
                this.nodeRefs[nodeId] = el;
            } else {
                delete this.nodeRefs[nodeId];
            }
        },
        buildArrow (source, target, label, key, offset = 0) {
            const x1 = source.left + source.width;
            const y1 = source.top + (source.height / 2) + offset;
            const x2 = target.left;
            const y2 = target.top + (target.height / 2);
            const controlOffset = Math.max(90, Math.abs(x2 - x1) / 2);
            return {
                key,
                path: `M ${x1} ${y1} C ${x1 + controlOffset} ${y1}, ${x2 - controlOffset} ${y2}, ${x2} ${y2}`,
                labelX: x1 + ((x2 - x1) / 2),
                labelY: y1 + ((y2 - y1) / 2) - 12,
                label
            };
        },
        getElementMetrics (element) {
            return {
                left: element.offsetLeft,
                top: element.offsetTop,
                width: element.offsetWidth || DEFAULT_NODE_WIDTH,
                height: element.offsetHeight || DEFAULT_NODE_HEIGHT
            };
        },
        getEstimatedNodeMetrics (node) {
            return {
                left: node.flow_builder_x || 0,
                top: node.flow_builder_y || 0,
                width: DEFAULT_NODE_WIDTH,
                height: Math.max(
                    DEFAULT_NODE_HEIGHT,
                    DEFAULT_NODE_HEIGHT + ((this.getInteractiveOptions(node).length - 3) * 56)
                )
            };
        },
        getNodeMetrics (node) {
            const element = this.nodeRefs[node.id_tmp];
            if (element) {
                return this.getElementMetrics(element);
            }
            return this.getEstimatedNodeMetrics(node);
        },
        rectanglesOverlap (firstRect, secondRect) {
            return (
                firstRect.left < (secondRect.left + secondRect.width + NODE_COLLISION_PADDING) &&
                (firstRect.left + firstRect.width + NODE_COLLISION_PADDING) > secondRect.left &&
                firstRect.top < (secondRect.top + secondRect.height + NODE_COLLISION_PADDING) &&
                (firstRect.top + firstRect.height + NODE_COLLISION_PADDING) > secondRect.top
            );
        },
        findAvailableNodePosition (node, index, occupiedRects) {
            const fallbackPosition = this.buildDefaultPosition(index);
            const baseMetrics = this.getNodeMetrics(node);
            const candidate = {
                left: Math.max(40, node.flow_builder_x === null || node.flow_builder_x === undefined
                    ? fallbackPosition.x
                    : node.flow_builder_x),
                top: Math.max(40, node.flow_builder_y === null || node.flow_builder_y === undefined
                    ? fallbackPosition.y
                    : node.flow_builder_y),
                width: baseMetrics.width,
                height: baseMetrics.height
            };
            let attempts = 0;
            while (attempts < 40) {
                const overlappingRect = occupiedRects.find((rect) => this.rectanglesOverlap(candidate, rect));
                if (!overlappingRect) {
                    return candidate;
                }
                const shiftedLeft = overlappingRect.left + overlappingRect.width + NODE_HORIZONTAL_GAP;
                const rowWidth = NODE_COLUMNS * (DEFAULT_NODE_WIDTH + NODE_HORIZONTAL_GAP);
                if ((shiftedLeft - NODE_START_X) < rowWidth) {
                    candidate.left = shiftedLeft;
                    candidate.top = Math.max(candidate.top, overlappingRect.top);
                } else {
                    candidate.left = fallbackPosition.x;
                    candidate.top = Math.max(
                        candidate.top,
                        overlappingRect.top + overlappingRect.height + NODE_VERTICAL_GAP
                    );
                }
                attempts += 1;
            }
            return {
                ...candidate,
                left: fallbackPosition.x,
                top: fallbackPosition.y + (attempts * NODE_VERTICAL_GAP)
            };
        },
        resolveNodeCollisions () {
            if (this.draggingNodeId) {
                return false;
            }
            const occupiedRects = [];
            let hasChanges = false;
            const incomingNode = this.$refs.incomingNode;
            if (incomingNode) {
                occupiedRects.push(this.getElementMetrics(incomingNode));
            }
            this.nodes.forEach((node, index) => {
                const resolvedPosition = this.findAvailableNodePosition(node, index, occupiedRects);
                const nodeMetrics = this.getNodeMetrics(node);
                if (
                    node.flow_builder_x !== resolvedPosition.left ||
                    node.flow_builder_y !== resolvedPosition.top
                ) {
                    node.flow_builder_x = resolvedPosition.left;
                    node.flow_builder_y = resolvedPosition.top;
                    hasChanges = true;
                }
                occupiedRects.push({
                    left: node.flow_builder_x,
                    top: node.flow_builder_y,
                    width: nodeMetrics.width,
                    height: nodeMetrics.height
                });
            });
            return hasChanges;
        },
        updateCanvasSize () {
            const metrics = [];
            const incomingNode = this.$refs.incomingNode;
            if (incomingNode) {
                metrics.push(this.getElementMetrics(incomingNode));
            }
            this.nodes.forEach((node) => {
                const element = this.nodeRefs[node.id_tmp];
                if (element) {
                    metrics.push(this.getElementMetrics(element));
                } else {
                    metrics.push({
                        left: node.flow_builder_x || 0,
                        top: node.flow_builder_y || 0,
                        width: DEFAULT_NODE_WIDTH,
                        height: DEFAULT_NODE_HEIGHT
                    });
                }
            });
            const width = metrics.length > 0
                ? Math.max(1600, ...metrics.map((metric) => metric.left + metric.width + 220))
                : 1600;
            const height = metrics.length > 0
                ? Math.max(900, ...metrics.map((metric) => metric.top + metric.height + 220))
                : 900;
            this.canvasSize.width = width;
            this.canvasSize.height = height;
        },
        getTreeBounds () {
            const metrics = [];
            const incomingNode = this.$refs.incomingNode;
            if (incomingNode) {
                metrics.push(this.getElementMetrics(incomingNode));
            }
            this.nodes.forEach((node) => {
                const element = this.nodeRefs[node.id_tmp];
                if (element) {
                    metrics.push(this.getElementMetrics(element));
                } else {
                    metrics.push({
                        left: node.flow_builder_x || 0,
                        top: node.flow_builder_y || 0,
                        width: DEFAULT_NODE_WIDTH,
                        height: DEFAULT_NODE_HEIGHT
                    });
                }
            });
            if (metrics.length === 0) {
                return {
                    minX: 0,
                    minY: 0,
                    maxX: this.canvasSize.width,
                    maxY: this.canvasSize.height
                };
            }
            return {
                minX: Math.min(...metrics.map((metric) => metric.left)),
                minY: Math.min(...metrics.map((metric) => metric.top)),
                maxX: Math.max(...metrics.map((metric) => metric.left + metric.width)),
                maxY: Math.max(...metrics.map((metric) => metric.top + metric.height))
            };
        },
        refreshArrows () {
            nextTick(() => {
                if (!this.resolvingOverlaps) {
                    const overlapsResolved = this.resolveNodeCollisions();
                    if (overlapsResolved) {
                        this.resolvingOverlaps = true;
                        nextTick(() => {
                            this.resolvingOverlaps = false;
                            this.refreshArrows();
                        });
                        return;
                    }
                }
                this.updateCanvasSize();
                const arrows = [];
                const incomingElement = this.$refs.incomingNode;
                const mainNode = this.nodes.find((node) => node.is_main) || this.nodes[0];
                if (incomingElement && mainNode && this.nodeRefs[mainNode.id_tmp]) {
                    arrows.push(
                        this.buildArrow(
                            this.getElementMetrics(incomingElement),
                            this.getElementMetrics(this.nodeRefs[mainNode.id_tmp]),
                            this.$t('views.whatsapp.line.flow.incoming_message'),
                            'incoming-main'
                        )
                    );
                }

                this.nodes.forEach((node) => {
                    const source = this.nodeRefs[node.id_tmp];
                    if (!source) {
                        return;
                    }
                    node.options
                        .filter((option) => (
                            option.type_option === DESTINATION_OPTION_TYPES.INTERACTIVE &&
                            option.destination &&
                            this.nodeRefs[option.destination]
                        ))
                        .forEach((option, index) => {
                            arrows.push(
                                this.buildArrow(
                                    this.getElementMetrics(source),
                                    this.getElementMetrics(this.nodeRefs[option.destination]),
                                    option.value || `${this.$t('views.whatsapp.line.flow.option_label')} ${index + 1}`,
                                    `${node.id_tmp}-${option.destination}-${index}`,
                                    (index * 10) - 10
                                )
                            );
                        });
                });
                this.arrows = arrows;
            });
        },
        zoomIn () {
            this.scale = Math.min(2, this.scale + 0.1);
            this.refreshArrows();
        },
        zoomOut () {
            this.scale = Math.max(0.25, this.scale - 0.1);
            this.refreshArrows();
        },
        resetViewport () {
            const wrapper = this.$refs.canvasWrapper;
            if (!wrapper) {
                return;
            }
            const padding = 140;
            const bounds = this.getTreeBounds();
            const availableWidth = Math.max(wrapper.clientWidth - 40, 400);
            const availableHeight = Math.max(wrapper.clientHeight - 40, 300);
            const contentWidth = Math.max(availableWidth, (bounds.maxX - bounds.minX) + padding);
            const contentHeight = Math.max(availableHeight, (bounds.maxY - bounds.minY) + padding);
            const fitScale = Math.min(
                1,
                availableWidth / contentWidth,
                availableHeight / contentHeight
            );
            this.scale = Math.max(0.25, fitScale);
            this.panOffsetX = -(bounds.minX - 70);
            this.panOffsetY = -(bounds.minY - 70);
            nextTick(() => {
                this.refreshArrows();
            });
        },
        saveFlow () {
            const hasErrors = this.nodes.some((node) => this.isNodeInvalid(node));
            if (hasErrors) {
                if (this.$swal && this.$helpers) {
                    this.$swal(
                        this.$helpers.getToasConfig(
                            this.$t('globals.error_notification') || 'Error',
                            this.$t('forms.whatsapp.line.validations.form_invalid') || 'Existen campos obligatorios incompletos. Verifique los bloques en rojo antes de guardar.',
                            this.$t('globals.icon_error') || 'error'
                        )
                    );
                } else {
                    alert('Existen campos obligatorios incompletos. Verifique los bloques en rojo antes de guardar.');
                }
                return;
            }
            this.$emit('handleModalEvent', { showModal: false });
            this.$emit('saveFlow');
        },
        handleWheel (event) {
            if (event.deltaY < 0) {
                this.zoomIn();
            } else {
                this.zoomOut();
            }
        },
        startPan (event) {
            if (
                this.draggingNodeId ||
                event.target.closest('.flow-node') ||
                event.target.closest('.p-button')
            ) {
                return;
            }
            const wrapper = this.$refs.canvasWrapper;
            if (!wrapper) {
                return;
            }
            this.isPanning = true;
            this.panStartX = event.clientX;
            this.panStartY = event.clientY;
            this.scrollStartLeft = wrapper.scrollLeft;
            this.scrollStartTop = wrapper.scrollTop;
            document.body.style.userSelect = 'none';
        },
        startDrag (event, nodeId) {
            if (event.target.closest('.p-button')) {
                return;
            }
            const node = this.nodes.find((item) => item.id_tmp === nodeId);
            if (!node) {
                return;
            }
            this.draggingNodeId = nodeId;
            this.dragStartX = event.clientX;
            this.dragStartY = event.clientY;
            this.dragNodeOriginX = node.flow_builder_x;
            this.dragNodeOriginY = node.flow_builder_y;
            this.dragMoved = false;
            this.selectNode(nodeId);
            document.body.style.userSelect = 'none';
        },
        handlePointerMove (event) {
            if (this.isPanning) {
                this.panOffsetX = this.panStartOffsetX + ((event.clientX - this.panStartX) / this.scale);
                this.panOffsetY = this.panStartOffsetY + ((event.clientY - this.panStartY) / this.scale);
                return;
            }
            if (!this.draggingNodeId) {
                return;
            }
            const node = this.nodes.find((item) => item.id_tmp === this.draggingNodeId);
            if (!node) {
                return;
            }
            const deltaX = (event.clientX - this.dragStartX) / this.scale;
            const deltaY = (event.clientY - this.dragStartY) / this.scale;
            if (Math.abs(deltaX) > 2 || Math.abs(deltaY) > 2) {
                this.dragMoved = true;
            }
            node.flow_builder_x = Math.max(40, Math.round(this.dragNodeOriginX + deltaX));
            node.flow_builder_y = Math.max(40, Math.round(this.dragNodeOriginY + deltaY));
            this.refreshArrows();
        },
        stopPointerInteraction () {
            this.isPanning = false;
            this.suppressClick = this.dragMoved;
            this.dragMoved = false;
            this.draggingNodeId = null;
            document.body.style.userSelect = '';
        }
    },
    watch: {
        showModal: {
            handler (value) {
                if (value) {
                    this.ensureNodes();
                } else {
                    this.closeEditor();
                }
            },
            immediate: true
        },
        nodes: {
            handler () {
                if (this.showModal) {
                    this.refreshArrows();
                }
            },
            deep: true
        }
    }
};
</script>

<style scoped>
.flow-builder-header {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.flow-builder-title {
  margin: 0;
}

.flow-builder-header__actions {
  display: flex;
  gap: 0.75rem;
}

.flow-builder-canvas-wrapper {
  position: relative;
  overflow: hidden;
  height: calc(100vh - 120px);
  padding: 0;
  background:
    radial-gradient(circle at top, rgba(37, 99, 235, 0.16), transparent 28%),
    linear-gradient(180deg, #f8fbff 0%, #edf4ff 100%);
}

.flow-builder-toolbar {
  position: sticky;
  top: 0;
  z-index: 4;
  width: fit-content;
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.5rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
}

.flow-builder-stage {
  position: relative;
  margin-top: 1rem;
  cursor: grab;
}

.flow-builder-stage--panning,
.flow-builder-stage--dragging {
  cursor: grabbing;
}

.flow-builder-arrows {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.flow-builder-arrow {
  fill: none;
  stroke: #2563eb;
  stroke-width: 2.5;
}

.flow-builder-arrow__label {
  fill: #1d4ed8;
  font-size: 12px;
  font-weight: 700;
}

.flow-node {
  position: absolute;
  z-index: 2;
  width: 320px;
  border: 2px solid transparent;
  border-radius: 20px;
  padding: 0.9rem;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 18px 38px rgba(15, 23, 42, 0.1);
}

.flow-node--selected {
  border-color: #2563eb;
}

.flow-node--invalid {
  box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2), 0 18px 38px rgba(15, 23, 42, 0.1);
}

.flow-node--link-target {
  border-color: #14b8a6;
}

.flow-node--incoming {
  width: 250px;
  border-color: #93c5fd;
  background: rgba(239, 246, 255, 0.98);
}

.flow-node__topbar,
.flow-node__actions,
.flow-builder-footer,
.flow-editor-options-header,
.flow-editor-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.whatsapp-preview {
  position: relative;
  background: #e7ffdb;
  border-radius: 7.5px;
  box-shadow: 0 1px 0.5px rgba(11,20,26,.13);
  margin-bottom: 8px;
  overflow: visible;
  border: none;
}

.whatsapp-preview::after {
  content: "";
  position: absolute;
  top: 0;
  right: -8px;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 0 8px 10px 0;
  border-color: transparent #e7ffdb transparent transparent;
}

.whatsapp-preview--incoming {
  background: #ffffff;
}

.whatsapp-preview--incoming::after {
  right: auto;
  left: -8px;
  border-width: 0 0 10px 8px;
  border-color: transparent transparent transparent #ffffff;
}

.whatsapp-preview__meta {
  padding: 0.5rem 0.5rem 0;
  font-size: 0.78rem;
  color: #667781;
}

.whatsapp-preview__headerbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.5rem 0.6rem 0.3rem;
  font-weight: 700;
  color: #111b21;
}

.whatsapp-preview__header-title {
  min-width: 0;
}

.whatsapp-preview__caret {
  color: #667781;
  font-size: 0.8rem;
}

.whatsapp-preview__body {
  padding: 0 0.6rem 0.4rem;
  white-space: pre-line;
  color: #111b21;
  font-size: 0.95rem;
  line-height: 1.35;
  min-height: 48px;
}

.whatsapp-preview__meta-row {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 0 0.6rem 0.3rem;
}

.whatsapp-preview__footer {
  font-size: 0.75rem;
  color: #667781;
  margin-right: auto;
}

.whatsapp-preview__time {
  font-size: 0.6875rem;
  color: #667781;
  display: flex;
  align-items: center;
  gap: 3px;
}

.whatsapp-preview__time::after {
  content: "\2713\2713"; /* Unicode Double Checkmark */
  color: #53bdeb; /* WhatsApp read tick color */
  font-size: 0.7rem;
  font-weight: bold;
}

.whatsapp-preview__button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  padding: 0.6rem 0;
  margin: 0 4px 4px 4px;
  border-top: 1px solid #d1d7db;
  font-weight: 600;
  color: #00a884;
  background: transparent;
  cursor: pointer;
}

.flow-node__connections {
  display: grid;
  gap: 0.6rem;
  margin-top: 0.75rem;
}

.flow-node__connections-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.flow-link-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.6rem 0.75rem;
  border-radius: 12px;
  background: rgba(248, 250, 252, 0.95);
  border: 1px solid #e2e8f0;
}

.flow-link-row--pending {
  border-color: #14b8a6;
  background: rgba(204, 251, 241, 0.6);
}

.flow-link-row--empty {
  justify-content: center;
  color: #64748b;
}

.flow-link-row__content {
  min-width: 0;
}

.flow-link-row__content strong,
.flow-link-row__content small {
  display: block;
}

.flow-link-row__content small,
.flow-link-row__hint {
  color: #64748b;
}

.flow-link-row__actions {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.flow-link-row__hint {
  font-size: 0.82rem;
  padding-left: 0.15rem;
}

.flow-builder-footer {
  width: 100%;
  color: #64748b;
}

.flow-editor-header h3 {
  margin: 0 0 0.25rem;
}

.flow-editor-modal__content {
  max-height: 70vh;
  overflow-y: auto;
  padding: 1.5rem;
}

.flow-option {
  padding: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #f8fbff;
  margin-bottom: 1rem;
}

.flow-option__campaign-message {
  padding: 0.85rem 1rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid #dbeafe;
}

.flow-option__row {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 0.75rem;
  align-items: end;
}

.flow-option__row--destinations {
  grid-template-columns: 1fr 1fr;
}

.flow-option__delete {
  margin-bottom: 0.5rem;
}

.flow-editor__empty {
  color: #64748b;
  padding: 1rem 0;
}

@media (max-width: 768px) {
  .flow-builder-header {
    flex-direction: column;
    align-items: stretch;
  }

  .flow-node {
    width: 280px;
  }

  .flow-builder-footer {
    gap: 0.75rem;
    flex-direction: column;
    align-items: flex-start;
  }

  .flow-option__row,
  .flow-option__row--destinations {
    grid-template-columns: 1fr;
  }
}
</style>
