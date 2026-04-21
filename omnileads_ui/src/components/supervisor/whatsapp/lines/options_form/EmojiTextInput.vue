<template>
  <div ref="root" class="emoji-input">
    <component
      :is="multiline ? 'Textarea' : 'InputText'"
      ref="fieldComponent"
      :modelValue="modelValue"
      :class="inputClass"
      :rows="multiline ? rows : undefined"
      :autoResize="multiline ? autoResize : undefined"
      :maxlength="maxLength"
      @input="handleInput"
    />
    <button
      type="button"
      class="emoji-input__toggle"
      :title="$t('views.whatsapp.line.flow.open_emoji_picker')"
      @click.stop="togglePicker"
    >
      <span aria-hidden="true">😊</span>
    </button>
    <div v-if="showPicker" class="emoji-input__panel">
      <div class="emoji-input__tabs">
        <button
          v-for="category in emojiCategories"
          :key="category.key"
          type="button"
          class="emoji-input__tab"
          :class="{ 'emoji-input__tab--active': activeCategory === category.key }"
          @click="activeCategory = category.key"
        >
          <span aria-hidden="true">{{ category.icon }}</span>
        </button>
      </div>
      <div class="emoji-input__grid">
        <button
          v-for="emoji in activeEmojis"
          :key="`${activeCategory}-${emoji}`"
          type="button"
          class="emoji-input__emoji"
          @click.prevent.stop="insertEmoji(emoji)"
        >
          {{ emoji }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { nextTick } from 'vue';

const EMOJI_CATEGORIES = [
    {
        key: 'faces',
        icon: '🙂',
        items: ['😀', '😃', '😄', '😁', '😊', '😍', '😘', '😎', '🤩', '🥳', '😇', '🤗', '😉', '😌', '😋', '😄', '😢', '😭', '😡', '🤔', '🤯', '😴', '🙌', '🙏']
    },
    {
        key: 'gestures',
        icon: '👍',
        items: ['👍', '👎', '👏', '🙌', '🤝', '💪', '👋', '✌️', '🤞', '👌', '🤟', '🫶', '🙏', '💯', '🔥', '✨', '⭐', '🎉', '🎯', '🚀']
    },
    {
        key: 'objects',
        icon: '💬',
        items: ['💬', '📌', '📍', '📣', '📲', '☎️', '🕐', '🗓️', '✅', '❌', '⚠️', 'ℹ️', '💡', '🛎️', '📝', '📦', '💳', '🏥', '📍', '🔔']
    },
    {
        key: 'nature',
        icon: '🌿',
        items: ['🌿', '🌱', '☀️', '🌙', '⭐', '🌈', '🌸', '🍀', '🍎', '☕', '🍽️', '🎁', '🎈', '❤️', '💙', '💚', '🧡', '💜', '🤍', '🖤']
    }
];

export default {
    name: 'EmojiTextInput',
    props: {
        modelValue: {
            type: String,
            default: ''
        },
        multiline: {
            type: Boolean,
            default: false
        },
        rows: {
            type: Number,
            default: 4
        },
        autoResize: {
            type: Boolean,
            default: false
        },
        maxLength: {
            type: Number,
            default: null
        },
        inputClass: {
            type: [String, Array, Object],
            default: ''
        }
    },
    emits: ['update:modelValue', 'input'],
    data () {
        return {
            showPicker: false,
            activeCategory: EMOJI_CATEGORIES[0].key,
            emojiCategories: EMOJI_CATEGORIES
        };
    },
    computed: {
        activeEmojis () {
            return this.emojiCategories.find((category) => category.key === this.activeCategory)?.items || [];
        }
    },
    mounted () {
        document.addEventListener('mousedown', this.handleClickOutside);
    },
    beforeUnmount () {
        document.removeEventListener('mousedown', this.handleClickOutside);
    },
    methods: {
        handleInput (event) {
            const nextValue = event?.target?.value ?? event;
            this.$emit('update:modelValue', nextValue);
            this.$emit('input', nextValue);
        },
        togglePicker () {
            this.showPicker = !this.showPicker;
        },
        handleClickOutside (event) {
            if (!this.showPicker) {
                return;
            }
            if (!this.$refs.root?.contains(event.target)) {
                this.showPicker = false;
            }
        },
        getNativeInput () {
            const component = this.$refs.fieldComponent;
            if (!component) {
                return null;
            }
            return component.$el?.querySelector('input, textarea') || component.$el || null;
        },
        insertEmoji (emoji) {
            const currentValue = this.modelValue || '';
            const nativeInput = this.getNativeInput();
            const selectionStart = nativeInput?.selectionStart ?? currentValue.length;
            const selectionEnd = nativeInput?.selectionEnd ?? currentValue.length;
            const nextValue =
                currentValue.slice(0, selectionStart) +
                emoji +
                currentValue.slice(selectionEnd);

            this.$emit('update:modelValue', nextValue);
            this.$emit('input', nextValue);

            nextTick(() => {
                const input = this.getNativeInput();
                if (!input) {
                    return;
                }
                const caretPosition = selectionStart + emoji.length;
                input.focus();
                input.setSelectionRange(caretPosition, caretPosition);
            });
        }
    }
};
</script>

<style scoped>
.emoji-input {
  position: relative;
}

.emoji-input :deep(.p-inputtext),
.emoji-input :deep(.p-inputtextarea) {
  width: 100%;
  padding-right: 2.8rem;
}

.emoji-input__toggle {
  position: absolute;
  top: 50%;
  right: 0.65rem;
  transform: translateY(-50%);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border: 0;
  border-radius: 999px;
  background: transparent;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s ease;
}

.emoji-input__toggle:hover {
  background: rgba(236, 72, 153, 0.08);
}

.emoji-input__panel {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  z-index: 50;
  width: 288px;
  padding: 0.75rem;
  border: 1px solid #f3d3e7;
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 20px 45px rgba(15, 23, 42, 0.14);
}

.emoji-input__tabs {
  display: flex;
  gap: 0.35rem;
  margin-bottom: 0.75rem;
}

.emoji-input__tab {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.1rem;
  height: 2.1rem;
  border: 0;
  border-radius: 999px;
  background: #f8fafc;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.emoji-input__tab--active,
.emoji-input__tab:hover {
  background: #fde7f3;
}

.emoji-input__grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 0.4rem;
}

.emoji-input__emoji {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.35rem;
  height: 2.35rem;
  border: 0;
  border-radius: 12px;
  background: #fff;
  cursor: pointer;
  font-size: 1.2rem;
  transition: transform 0.15s ease, background-color 0.15s ease;
}

.emoji-input__emoji:hover {
  background: #fdf2f8;
  transform: scale(1.05);
}
</style>
