import React, { useState, useEffect } from 'react';
import {
  ArrowUpRight,
  Info,
  AlertTriangle,
  CheckCircle,
  Clock,
  ExternalLink,
  ShieldAlert,
  Sun,
  Wind,
  FileSpreadsheet,
  Check
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip
} from 'recharts';
import { fetchSiteForecast } from '../api';

export default function OverviewPage({
  sites = [],
  alerts = [],
  onSelectSite,
  onOpenValidationLab,
  onAcknowledgeAlert,
  onNavigateToView
}) {
  const [selectedSiteIndex, setSelectedSiteIndex] = useState(0);
  const [isAcknowledged, setIsAcknowledged] = useState(false);
  const [forecastSeries, setForecastSeries] = useState([]);

  const activeSite = sites[selectedSiteIndex] || sites[0] || {
    site_id: 'AD_SITE_01',
    pseudonym: 'Al Reem Coastal Construction Sector A',
    current_tier: 'Watch',
    latest_environment: { temperature_c: 28.7, pm25: 36.4, heat_index_c: 33.5, status: 'fresh' }
  };

  useEffect(() => {
    if (activeSite?.site_id) {
      fetchSiteForecast(activeSite.site_id, 72)
        .then((records) => {
          if (records && records.length > 0) {
            const formatted = records.map((r, idx) => {
              const dt = new Date(r.valid_at);
              const hourStr = dt.getHours().toString().padStart(2, '0') + ':00';
              return {
                time: idx === 0 ? 'NOW' : hourStr,
                temp: r.temperature_c !== null ? Math.round(r.temperature_c) : 32,
                pm25: r.pm25 !== null ? Math.round(r.pm25) : 25,
                hi: r.heat_index_c !== null ? Math.round(r.heat_index_c) : 34
              };
            });
            setForecastSeries(formatted);
          }
        })
        .catch((err) => console.warn('Could not fetch real forecast, using fallback:', err));
    }
  }, [activeSite?.site_id]);

  // Fallback if network is loading
  const displayForecast = forecastSeries.length > 0 ? forecastSeries : [
    { time: 'NOW', temp: 32, pm25: 22 },
    { time: '+6H', temp: 35, pm25: 26 },
    { time: '+12H', temp: 34, pm25: 28 },
    { time: '+18H', temp: 37, pm25: 32 },
    { time: '+24H', temp: 42, pm25: 38 },
    { time: '+30H', temp: 44, pm25: 42 },
    { time: '+36H', temp: 43, pm25: 40 },
    { time: '+48H', temp: 45, pm25: 35 },
    { time: '+72H', temp: 40, pm25: 29 },
  ];

  return (
    <div className="p-8 max-w-[1600px] mx-auto space-y-6">
      {/* Hero Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 gap-4">
        <div>
          <div className="text-[11px] font-mono tracking-wider font-semibold text-[#839790] uppercase mb-1">
            ABU DHABI · SITE OPERATIONS / REPLAY MODE
          </div>
          <h2 className="text-3xl font-bold text-[#142621] tracking-tight">
            Where should teams act today<span className="text-[#d9653b]">?</span>
          </h2>
          <p className="text-sm text-[#5f746d] mt-1 max-w-3xl">
            Environmental signals meet workplace evidence. Prioritize sites, understand why, and record the next safe action.
          </p>
        </div>

        <div className="flex items-center space-x-3 shrink-0">
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-[#faece5] border border-[#f0d4c8] text-xs font-semibold text-[#a6421c]">
            <span className="w-2 h-2 rounded-full bg-[#d9653b]"></span>
            <span>SYNTHETIC WORKPLACE DATA</span>
          </div>
          <button
            onClick={() => window.print()}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded bg-white border border-[#d6cfc5] text-xs font-medium text-[#2d403a] hover:bg-[#f7f5f1] transition-colors shadow-sm"
          >
            <span>Export brief</span>
            <ArrowUpRight className="w-3.5 h-3.5 text-[#637770]" />
          </button>
        </div>
      </div>

      {/* Top 4 KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Sites Monitored */}
        <div
          onClick={() => onNavigateToView('sites')}
          className="bg-white rounded-xl p-5 border border-[#e6e2da] shadow-sm hover:border-[#ccd7d3] transition-all cursor-pointer"
        >
          <div className="flex items-center justify-between text-xs font-mono font-semibold text-[#718780] tracking-wider uppercase">
            <span>SITES MONITORED</span>
            <ArrowUpRight className="w-4 h-4 text-[#8a9f98]" />
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-4xl font-bold font-mono text-[#142621]">03</span>
            <span className="text-xs font-medium text-[#5f746d]">Abu Dhabi pilot</span>
          </div>
          <p className="text-xs text-[#849a92] mt-2">Fictional sites · scoped access</p>
        </div>

        {/* Card 2: Needs Attention */}
        <div
          onClick={() => onNavigateToView('alerts')}
          className="bg-white rounded-xl p-5 border border-[#e6e2da] shadow-sm hover:border-[#ccd7d3] transition-all cursor-pointer"
        >
          <div className="flex items-center justify-between text-xs font-mono font-semibold text-[#718780] tracking-wider uppercase">
            <span>NEEDS ATTENTION</span>
            <span className="w-2 h-2 rounded-full bg-[#d97736]"></span>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-4xl font-bold font-mono text-[#d9653b]">02</span>
            <span className="text-xs font-medium text-[#5f746d]">1 advisory · 1 watch</span>
          </div>
          <p className="text-xs text-[#849a92] mt-2">Review in priority order</p>
        </div>

        {/* Card 3: Source Health */}
        <div
          onClick={() => onNavigateToView('data_quality')}
          className="bg-white rounded-xl p-5 border border-[#e6e2da] shadow-sm hover:border-[#ccd7d3] transition-all cursor-pointer"
        >
          <div className="flex items-center justify-between text-xs font-mono font-semibold text-[#718780] tracking-wider uppercase">
            <span>SOURCE HEALTH</span>
            <ArrowUpRight className="w-4 h-4 text-[#8a9f98]" />
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-4xl font-bold font-mono text-[#142621]">2/3</span>
            <span className="text-xs font-medium text-[#5f746d]">Feeds up to date</span>
          </div>
          <div className="flex items-center space-x-1.5 text-xs text-[#b87628] mt-2 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-[#d99b26]"></span>
            <span>Workplace feed delayed</span>
          </div>
        </div>

        {/* Card 4: Unacknowledged */}
        <div
          onClick={() => onNavigateToView('alerts')}
          className="bg-white rounded-xl p-5 border border-[#e6e2da] shadow-sm hover:border-[#ccd7d3] transition-all cursor-pointer"
        >
          <div className="flex items-center justify-between text-xs font-mono font-semibold text-[#718780] tracking-wider uppercase">
            <span>UNACKNOWLEDGED</span>
            <ArrowUpRight className="w-4 h-4 text-[#8a9f98]" />
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-4xl font-bold font-mono text-[#142621]">01</span>
            <span className="text-xs font-medium text-[#5f746d]">HSE action pending</span>
          </div>
          <p className="text-xs text-[#849a92] mt-2">Latest alert · 12:40 GST</p>
        </div>
      </div>

      {/* Middle Grid: Prioritization Queue + Evidence Card */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: 01 / PRIORITIZATION */}
        <div className="lg:col-span-7 bg-white rounded-xl border border-[#e6e2da] p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-[#f0ece4]">
              <div>
                <p className="text-[11px] font-mono tracking-wider font-semibold text-[#80958e] uppercase">
                  01 / PRIORITIZATION
                </p>
                <h3 className="text-xl font-bold text-[#142621]">Site priority queue</h3>
                <p className="text-xs text-[#6e837c] mt-0.5">
                  One view of site status, independent evidence and next steps.
                </p>
              </div>
              <div className="flex items-center space-x-1 text-xs font-mono text-[#6c827b]">
                <span>PRIORITY ORDER</span>
                <span>↓</span>
              </div>
            </div>

            {/* Sites Table */}
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="text-[#889d96] font-mono text-[10.5px] uppercase border-b border-[#f2ede6]">
                    <th className="pb-2 font-semibold">LOCATION / SITE</th>
                    <th className="pb-2 font-semibold">RISK STATE</th>
                    <th className="pb-2 font-semibold">EVIDENCE SNAPSHOT</th>
                    <th className="pb-2 font-semibold text-right">NEXT STEP</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#f5f1ea]">
                  {/* Row 1: Mussafah Industrial */}
                  <tr
                    onClick={() => setSelectedSiteIndex(1)}
                    className={`hover:bg-[#faf7f2] cursor-pointer transition-colors ${
                      selectedSiteIndex === 1 ? 'bg-[#f7f3eb]' : ''
                    }`}
                  >
                    <td className="py-3.5 pr-3">
                      <div className="flex items-center space-x-2.5">
                        <div className="w-7 h-7 rounded bg-[#f3efe8] flex items-center justify-center text-[#748781]">
                          <Sun className="w-3.5 h-3.5" />
                        </div>
                        <div>
                          <p className="font-semibold text-[#182a25]">Mussafah Industrial</p>
                          <p className="text-[10px] text-[#869b94]">AD_SITE_02 · Construction</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 pr-3">
                      <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-[#fceee6] text-[#b84a1e] border border-[#f5d5c6]">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#d9653b]"></span>
                        <span>Advisory</span>
                      </span>
                    </td>
                    <td className="py-3.5 pr-3">
                      <p className="font-medium text-[#2d403a]">Heat + near-miss anomaly</p>
                      <p className="text-[10px] text-[#869b94]">2 corroborating signals · updated 12:40</p>
                    </td>
                    <td className="py-3.5 text-right">
                      <span className="inline-flex items-center space-x-1 font-semibold text-[#2d403a] hover:text-[#d9653b]">
                        <span>Review breaks</span>
                        <ArrowUpRight className="w-3.5 h-3.5" />
                      </span>
                    </td>
                  </tr>

                  {/* Row 2: Al Reem Coastal */}
                  <tr
                    onClick={() => setSelectedSiteIndex(0)}
                    className={`hover:bg-[#faf7f2] cursor-pointer transition-colors ${
                      selectedSiteIndex === 0 ? 'bg-[#f7f3eb]' : ''
                    }`}
                  >
                    <td className="py-3.5 pr-3">
                      <div className="flex items-center space-x-2.5">
                        <div className="w-7 h-7 rounded bg-[#f3efe8] flex items-center justify-center text-[#748781]">
                          <Wind className="w-3.5 h-3.5" />
                        </div>
                        <div>
                          <p className="font-semibold text-[#182a25]">Al Reem Island</p>
                          <p className="text-[10px] text-[#869b94]">AD_SITE_01 · Construction</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 pr-3">
                      <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-[#ebf3ee] text-[#2c6e49] border border-[#d2e4d9]">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#398357]"></span>
                        <span>Watch</span>
                      </span>
                    </td>
                    <td className="py-3.5 pr-3">
                      <p className="font-medium text-[#2d403a]">Environmental exposure rising</p>
                      <p className="text-[10px] text-[#869b94]">Workplace pattern remains stable</p>
                    </td>
                    <td className="py-3.5 text-right">
                      <span className="inline-flex items-center space-x-1 font-semibold text-[#2d403a] hover:text-[#d9653b]">
                        <span>Monitor</span>
                        <ArrowUpRight className="w-3.5 h-3.5" />
                      </span>
                    </td>
                  </tr>

                  {/* Row 3: Khalifa City */}
                  <tr
                    onClick={() => setSelectedSiteIndex(2)}
                    className={`hover:bg-[#faf7f2] cursor-pointer transition-colors ${
                      selectedSiteIndex === 2 ? 'bg-[#f7f3eb]' : ''
                    }`}
                  >
                    <td className="py-3.5 pr-3">
                      <div className="flex items-center space-x-2.5">
                        <div className="w-7 h-7 rounded bg-[#f3efe8] flex items-center justify-center text-[#748781]">
                          <FileSpreadsheet className="w-3.5 h-3.5" />
                        </div>
                        <div>
                          <p className="font-semibold text-[#182a25]">Khalifa City</p>
                          <p className="text-[10px] text-[#869b94]">AD_SITE_03 · Construction</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 pr-3">
                      <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-[#edf1f0] text-[#556963] border border-[#d9e1df]">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#7c918b]"></span>
                        <span>Degraded</span>
                      </span>
                    </td>
                    <td className="py-3.5 pr-3">
                      <p className="font-medium text-[#2d403a]">Workplace report delayed</p>
                      <p className="text-[10px] text-[#869b94]">Incident-based risk cannot be confirmed</p>
                    </td>
                    <td className="py-3.5 text-right">
                      <span className="inline-flex items-center space-x-1 font-semibold text-[#2d403a] hover:text-[#d9653b]">
                        <span>Check feed</span>
                        <ArrowUpRight className="w-3.5 h-3.5" />
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* Legend & Link */}
            <div className="flex items-center justify-between text-[11px] text-[#788e87] pt-4 border-t border-[#f2ede6] mt-4">
              <div className="flex items-center space-x-4">
                <span className="flex items-center space-x-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#d9653b]"></span>
                  <span>Risk state</span>
                </span>
                <span className="flex items-center space-x-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#7c918b]"></span>
                  <span>Data confidence tracked separately</span>
                </span>
              </div>
              <button
                onClick={() => onNavigateToView('sites')}
                className="font-semibold text-[#243731] hover:text-[#d9653b] flex items-center space-x-1"
              >
                <span>VIEW SITE REGISTER</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Shift Handover Box */}
          <div className="mt-5 p-3.5 rounded-lg bg-[#f7f4ee] border border-[#e6e0d4] text-xs">
            <div className="text-[10px] font-mono uppercase tracking-wider text-[#798e87] font-semibold mb-2">
              SHIFT HANDOVER · AS OF 12:40 GST
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="border-l-2 border-[#d9653b] pl-2.5">
                <p className="font-semibold text-[#182a25]">1 awaiting acknowledgement</p>
                <p className="text-[11px] text-[#71857e]">Mussafah · preventive review</p>
              </div>
              <div className="border-l-2 border-[#7c918b] pl-2.5">
                <p className="font-semibold text-[#182a25]">1 data-quality follow-up</p>
                <p className="text-[11px] text-[#71857e]">Khalifa City · request latest CSV</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: 02 / DECISION SUPPORT (Evidence Card) */}
        <div className="lg:col-span-5 bg-white rounded-xl border border-[#e6e2da] p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-[#f0ece4]">
              <div>
                <p className="text-[11px] font-mono tracking-wider font-semibold text-[#80958e] uppercase">
                  02 / DECISION SUPPORT
                </p>
                <h3 className="text-xl font-bold text-[#142621]">Evidence card</h3>
                <p className="text-xs text-[#6e837c] mt-0.5">
                  {activeSite.site_id} · evaluated 12:40 GST
                </p>
              </div>
              <span className="text-xs font-mono font-semibold text-[#849a92]">EV / 001</span>
            </div>

            {/* Alert Status Banner */}
            <div className="mt-4 flex items-center justify-between">
              <span className="text-xs font-mono font-bold tracking-wider uppercase text-[#b84a1e]">
                ADVISORY · REVIEW REQUIRED
              </span>
              <div className="w-6 h-6 rounded-full bg-[#fceee6] flex items-center justify-center text-[#d9653b]">
                <ArrowUpRight className="w-3.5 h-3.5" />
              </div>
            </div>

            {/* Alert Headline */}
            <h4 className="text-xl font-bold text-[#182a25] mt-2 leading-snug">
              Heat exposure with rising near misses.
            </h4>
            <p className="text-xs text-[#5f746d] mt-1.5 leading-relaxed">
              Independent environmental and workplace signals justify a site-level preventive review.
            </p>

            {/* Signals Contribution Progress Bars */}
            <div className="mt-5 space-y-3">
              <div className="flex items-center justify-between text-[11px] font-mono uppercase text-[#738881]">
                <span className="font-semibold">SIGNALS CONTRIBUTING TO THIS ALERT</span>
                <span className="text-[10px] text-[#91a49e]">MODEL UNVALIDATED</span>
              </div>

              {/* Signal 1: Environmental Heat */}
              <div>
                <div className="flex justify-between text-xs font-medium text-[#2d403a] mb-1">
                  <span>Environmental heat</span>
                  <span className="font-mono font-semibold">0.78</span>
                </div>
                <div className="w-full h-2 rounded-full bg-[#ece8df] overflow-hidden">
                  <div className="h-full rounded-full bg-[#c85a32]" style={{ width: '78%' }}></div>
                </div>
              </div>

              {/* Signal 2: Workplace Deviation */}
              <div>
                <div className="flex justify-between text-xs font-medium text-[#2d403a] mb-1">
                  <span>Workplace deviation</span>
                  <span className="font-mono font-semibold">0.69</span>
                </div>
                <div className="w-full h-2 rounded-full bg-[#ece8df] overflow-hidden">
                  <div className="h-full rounded-full bg-[#c87640]" style={{ width: '69%' }}></div>
                </div>
              </div>

              {/* Signal 3: PM2.5 Context */}
              <div>
                <div className="flex justify-between text-xs font-medium text-[#2d403a] mb-1">
                  <span>PM2.5 context</span>
                  <span className="font-mono font-semibold">0.26</span>
                </div>
                <div className="w-full h-2 rounded-full bg-[#ece8df] overflow-hidden">
                  <div className="h-full rounded-full bg-[#ad8158]" style={{ width: '26%' }}></div>
                </div>
              </div>
            </div>

            {/* Scientific / Clinical Disclaimer Notice */}
            <div className="mt-5 p-3 rounded-lg bg-[#f7f5f0] border border-[#e4ded4] flex items-start space-x-2 text-xs text-[#677c75] leading-relaxed">
              <Info className="w-4 h-4 text-[#8a9f98] shrink-0 mt-0.5" />
              <span>
                Near-miss rate elevated relative to a 14-day provisional baseline. Scores are demo evidence units, not calibrated illness probabilities.
              </span>
            </div>
          </div>

          {/* Action Box & Button */}
          <div className="mt-6 pt-4 border-t border-[#f0ece4]">
            <p className="text-[10.5px] font-mono uppercase tracking-wider text-[#798e87] font-semibold">
              RECOMMENDED NEXT ACTION
            </p>
            <div className="flex items-center space-x-2 mt-1.5">
              <ArrowUpRight className="w-4 h-4 text-[#2d403a] shrink-0" />
              <div>
                <p className="text-xs font-bold text-[#182a25]">Review shaded breaks and task timing</p>
                <p className="text-[11px] text-[#71857e]">Owner: HSE Officer + Operations Lead</p>
              </div>
            </div>

            <button
              onClick={() => {
                setIsAcknowledged(true);
                if (onAcknowledgeAlert) onAcknowledgeAlert('ALT-DEMO-01');
              }}
              className={`w-full mt-4 py-2.5 px-4 rounded-lg font-semibold text-xs transition-all flex items-center justify-center space-x-2 shadow-sm ${
                isAcknowledged
                  ? 'bg-[#2b664d] text-white cursor-default'
                  : 'bg-[#1b3e37] hover:bg-[#142f2a] text-white'
              }`}
            >
              {isAcknowledged ? (
                <>
                  <Check className="w-4 h-4" />
                  <span>Alert Acknowledged (Logged to Audit)</span>
                </>
              ) : (
                <>
                  <span>Acknowledge alert</span>
                  <ArrowUpRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Bottom Grid: 72-Hour Exposure Outlook + Signal Integrity */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: 03 / ENVIRONMENT - 72h Exposure Outlook */}
        <div className="lg:col-span-7 bg-white rounded-xl border border-[#e6e2da] p-6 shadow-sm">
          <div className="flex items-center justify-between pb-3 border-b border-[#f0ece4]">
            <div>
              <p className="text-[11px] font-mono tracking-wider font-semibold text-[#80958e] uppercase">
                03 / ENVIRONMENT
              </p>
              <h3 className="text-xl font-bold text-[#142621]">72-hour exposure outlook</h3>
              <p className="text-xs text-[#6e837c] mt-0.5">
                Provider forecast, not a prediction of worker illness.
              </p>
            </div>
            <span className="px-2.5 py-1 rounded bg-[#f5f1ea] text-[10.5px] font-mono font-semibold text-[#667a74]">
              FORECAST / EXAMPLE
            </span>
          </div>

          {/* Chart Legend */}
          <div className="flex items-center justify-between text-xs text-[#6f847d] mt-3">
            <div className="flex items-center space-x-4">
              <span className="flex items-center space-x-1.5 font-medium">
                <span className="w-3.5 h-0.5 bg-[#c85a32]"></span>
                <span>Forecast temperature</span>
              </span>
              <span className="flex items-center space-x-1.5 font-medium">
                <span className="w-3.5 h-0.5 border-t border-dashed border-[#588157]"></span>
                <span>PM2.5</span>
              </span>
            </div>
            <span className="text-[11px] text-[#93a6a0]">Normalized for visual comparison</span>
          </div>

          {/* Recharts Area Curve */}
          <div className="h-44 w-full mt-3">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={displayForecast} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="tempGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#c85a32" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#c85a32" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="time"
                  tickLine={false}
                  axisLine={{ stroke: '#ede8e0' }}
                  tick={{ fill: '#8ca099', fontSize: 10, fontFamily: 'monospace' }}
                />
                <YAxis
                  tickLine={false}
                  axisLine={{ stroke: '#ede8e0' }}
                  tick={{ fill: '#8ca099', fontSize: 10, fontFamily: 'monospace' }}
                  domain={[20, 50]}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1b3e37',
                    borderRadius: '8px',
                    color: '#fff',
                    border: 'none',
                    fontSize: '11px',
                    fontFamily: 'monospace'
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="temp"
                  stroke="#c85a32"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#tempGradient)"
                />
                <Area
                  type="monotone"
                  dataKey="pm25"
                  stroke="#588157"
                  strokeWidth={1.5}
                  strokeDasharray="4 4"
                  fill="none"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* 3 Forecast Takeaways */}
          <div className="grid grid-cols-3 gap-3 pt-4 border-t border-[#f2ede6] mt-2 text-xs">
            <div className="p-2.5 rounded bg-[#faf7f2] border border-[#ede7dc]">
              <span className="font-mono font-bold text-[#182a25]">24h</span>
              <p className="text-[11px] text-[#6b8079] mt-0.5">Heat concern persists</p>
            </div>
            <div className="p-2.5 rounded bg-[#faf7f2] border border-[#ede7dc]">
              <span className="font-mono font-bold text-[#c85a32]">48h</span>
              <p className="text-[11px] text-[#6b8079] mt-0.5">Peak exposure window</p>
            </div>
            <div className="p-2.5 rounded bg-[#faf7f2] border border-[#ede7dc]">
              <span className="font-mono font-bold text-[#182a25]">72h</span>
              <p className="text-[11px] text-[#6b8079] mt-0.5">Review updated forecast</p>
            </div>
          </div>
        </div>

        {/* Right Column: 04 / TRUST & OPERATIONS - Signal Integrity */}
        <div className="lg:col-span-5 bg-white rounded-xl border border-[#e6e2da] p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="pb-3 border-b border-[#f0ece4]">
              <p className="text-[11px] font-mono tracking-wider font-semibold text-[#80958e] uppercase">
                04 / TRUST & OPERATIONS
              </p>
              <h3 className="text-xl font-bold text-[#142621]">Signal integrity</h3>
              <p className="text-xs text-[#6e837c] mt-0.5">
                Every risk assessment depends on data availability.
              </p>
            </div>

            {/* Data Streams List */}
            <div className="mt-4 space-y-3.5">
              {/* Stream 1: Weather Observations */}
              <div className="flex items-center justify-between p-3 rounded-lg bg-[#fbf9f6] border border-[#ede8df]">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-lg bg-[#eef5f1] text-[#2c6e49] flex items-center justify-center">
                    <Sun className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-[#182a25]">Weather observations</p>
                    <p className="text-[10px] text-[#788e87]">Open-Meteo · 12:41 GST</p>
                  </div>
                </div>
                <span className="px-2.5 py-0.5 rounded text-[11px] font-semibold bg-[#ebf5ee] text-[#2c6e49] border border-[#cfdfd5]">
                  Current
                </span>
              </div>

              {/* Stream 2: Air Quality */}
              <div className="flex items-center justify-between p-3 rounded-lg bg-[#fbf9f6] border border-[#ede8df]">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-lg bg-[#eef5f1] text-[#2c6e49] flex items-center justify-center">
                    <Wind className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-[#182a25]">Air quality</p>
                    <p className="text-[10px] text-[#788e87]">Open-Meteo · 12:39 GST</p>
                  </div>
                </div>
                <span className="px-2.5 py-0.5 rounded text-[11px] font-semibold bg-[#ebf5ee] text-[#2c6e49] border border-[#cfdfd5]">
                  Current
                </span>
              </div>

              {/* Stream 3: Workplace Aggregates */}
              <div className="flex items-center justify-between p-3 rounded-lg bg-[#fbf9f6] border border-[#ede8df]">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-lg bg-[#fcf3e8] text-[#b87628] flex items-center justify-center">
                    <FileSpreadsheet className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-[#182a25]">Workplace aggregates</p>
                    <p className="text-[10px] text-[#788e87]">Synthetic CSV · 19h since receipt</p>
                  </div>
                </div>
                <span className="px-2.5 py-0.5 rounded text-[11px] font-semibold bg-[#fef5e7] text-[#b87628] border border-[#f3ddbe]">
                  Delayed
                </span>
              </div>
            </div>
          </div>

          {/* Safety Rule Warning Invariant */}
          <div className="mt-5 p-3 rounded-lg bg-[#fdfaf5] border border-[#eadaa6] text-xs font-medium text-[#8f6412] flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-[#d99b26] shrink-0" />
            <span>A delayed workplace feed must not be shown as "safe".</span>
          </div>
        </div>
      </div>

      {/* Bottom Validation Status Banner */}
      <div className="p-4 rounded-xl bg-[#ede8de] border border-[#ded8cb] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-center space-x-2 text-[#465b54]">
          <span className="font-mono font-bold text-[#182a25] uppercase tracking-wider">
            VALIDATION STATUS
          </span>
          <span className="text-[#a5b5ae]">/</span>
          <span className="font-semibold text-[#182a25]">Scenario-based evaluation pending</span>
          <span className="text-[#a5b5ae]">/</span>
          <span className="text-[#647972]">Clinical predictive performance has not been established</span>
        </div>

        <button
          onClick={onOpenValidationLab}
          className="font-bold text-xs font-mono text-[#182a25] hover:text-[#d9653b] flex items-center space-x-1 shrink-0 uppercase tracking-wider"
        >
          <span>OPEN VALIDATION LAB</span>
          <ArrowUpRight className="w-4 h-4" />
        </button>
      </div>

      {/* Footer Text */}
      <div className="text-center text-[11px] font-mono text-[#8a9e97] pt-2 pb-6">
        HEAT-EWS · Functional UI design prototype · Synthetic workplace data and illustrative environmental values · Not for operational safety decisions
      </div>
    </div>
  );
}

