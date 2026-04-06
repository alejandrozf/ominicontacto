<template>
  <article class="campaign-kpi-card">
    <div class="campaign-kpi-card__header">
      <span
        class="campaign-kpi-card__icon"
        :style="{ background: iconBackground, color: accentColor }"
      >
        <i :class="iconClass"></i>
      </span>
      <span class="campaign-kpi-card__badge">{{ titleize(chartName) }}</span>
    </div>

    <div class="campaign-kpi-card__body">
      <p class="campaign-kpi-card__title">
        {{
          $t("views.dashboard_home_page.active_campaign_by_type", {
            type: titleize(chartName),
          })
        }}
      </p>
      <strong class="campaign-kpi-card__value">{{ chartData }}</strong>
    </div>

    <div class="campaign-kpi-card__sparkline">
      <svg viewBox="0 0 220 76" preserveAspectRatio="none" aria-hidden="true">
        <defs>
          <linearGradient :id="gradientId" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" :stop-color="accentColor" stop-opacity="0.32" />
            <stop offset="100%" :stop-color="accentColor" stop-opacity="0" />
          </linearGradient>
        </defs>
        <path
          :d="sparklineAreaPath"
          :fill="`url(#${gradientId})`"
        />
        <polyline
          :points="sparklinePoints"
          fill="none"
          :stroke="accentColor"
          stroke-width="3"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
    </div>
  </article>
</template>
<script>
import { computed } from 'vue';

export default {
    props: {
        chartData: Number,
        chartName: String
    },
    methods: {
        titleize (txt) {
            return txt.charAt(0).toUpperCase() + txt.slice(1).toLowerCase();
        }
    },
    setup (props) {
        const chartStyles = {
            inbound: {
                icon: 'pi pi-phone',
                color: '#72d6b5',
                background: 'rgba(114, 214, 181, 0.16)'
            },
            dialer: {
                icon: 'pi pi-android',
                color: '#9db8ff',
                background: 'rgba(93, 163, 255, 0.16)'
            },
            manual: {
                icon: 'pi pi-pencil',
                color: '#ffb54d',
                background: 'rgba(255, 181, 77, 0.18)'
            },
            preview: {
                icon: 'pi pi-eye',
                color: '#8f9cff',
                background: 'rgba(143, 156, 255, 0.16)'
            }
        };

        const iconClass = computed(() => {
            return chartStyles[props.chartName]?.icon || 'pi pi-chart-line';
        });

        const accentColor = computed(() => {
            return chartStyles[props.chartName]?.color || '#8FC641';
        });

        const iconBackground = computed(() => {
            return chartStyles[props.chartName]?.background || 'rgba(143, 198, 65, 0.16)';
        });

        const gradientId = computed(() => `campaign-gradient-${props.chartName}`.toLowerCase().replace(/\s+/g, '-'));

        const sparklineValues = computed(() => {
            const seed = (props.chartName || '').split('').reduce((total, char) => total + char.charCodeAt(0), 0);
            const baseline = Number(props.chartData || 0);
            return Array.from({ length: 8 }, (_, index) => {
                const variation = Math.sin((index + seed) * 0.65) * 2;
                const progressive = index * Math.max(baseline * 0.08, 0.45);
                return Math.max(1, baseline * 0.55 + progressive + variation);
            });
        });

        const sparklinePoints = computed(() => {
            const values = sparklineValues.value;
            const maxValue = Math.max(...values, 1);
            const width = 220;
            const height = 76;
            const stepX = width / (values.length - 1);
            return values.map((value, index) => {
                const x = index * stepX;
                const y = height - (value / maxValue) * 48 - 10;
                return `${x},${y}`;
            }).join(' ');
        });

        const sparklineAreaPath = computed(() => {
            const points = sparklinePoints.value;
            return `M 0 76 L ${points} L 220 76 Z`;
        });

        return {
            accentColor,
            gradientId,
            iconBackground,
            iconClass,
            sparklineAreaPath,
            sparklinePoints
        };
    }
};
</script>
<style>
.campaign-kpi-card {
  height: 100%;
  padding: 1.3rem;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(15, 23, 42, 0.08);
  box-shadow: 0 22px 50px rgba(15, 23, 42, 0.08);
  overflow: hidden;
}

html.dark-mode .campaign-kpi-card {
  background: rgba(18, 22, 33, 0.92);
  border-color: rgba(255, 255, 255, 0.08);
  box-shadow: 0 22px 50px rgba(0, 0, 0, 0.35);
}

.campaign-kpi-card__header,
.campaign-kpi-card__body {
  position: relative;
  z-index: 1;
}

.campaign-kpi-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 1.15rem;
}

.campaign-kpi-card__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 16px;
  font-size: 1.1rem;
}

.campaign-kpi-card__badge {
  display: inline-flex;
  align-items: center;
  height: 2rem;
  padding: 0 0.85rem;
  border-radius: 999px;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #66758d;
  background: rgba(15, 23, 42, 0.05);
}

html.dark-mode .campaign-kpi-card__badge {
  color: #93a5c0;
  background: rgba(255, 255, 255, 0.06);
}

.campaign-kpi-card__title {
  margin: 0;
  color: #5f6c82;
  font-size: 0.92rem;
  line-height: 1.5;
}

html.dark-mode .campaign-kpi-card__title {
  color: #9aa8bf;
}

.campaign-kpi-card__value {
  display: inline-block;
  margin-top: 0.5rem;
  color: #162033;
  font-size: 2.4rem;
  line-height: 1;
}

html.dark-mode .campaign-kpi-card__value {
  color: #f5f7fb;
}

.campaign-kpi-card__sparkline {
  height: 4.75rem;
  margin-top: 1.15rem;
}

.campaign-kpi-card__sparkline svg {
  width: 100%;
  height: 100%;
}
</style>
