import React from 'react';
import { Calendar, Clock, LogOut, User } from 'lucide-react';

export default function Header({
  activeView,
  activeScenario,
  onSelectScenario,
  scenarios = [],
  currentUser,
  onLogout
}) {
  const viewTitles = {
    overview: 'OVERVIEW',
    sites: 'CONSTRUCTION SITES',
    alerts: 'ALERTS & DECISION SUPPORT',
    outlook: 'EXPOSURE OUTLOOK',
    analytics: 'TELEMETRY & ANOMALY ANALYTICS',
    data_quality: 'DATA SOURCES & QUALITY',
    model_eval: 'MODEL EVALUATION & MONITORING',
    settings: 'SETTINGS & ROLE ACCESS'
  };

  return (
    <header className="h-14 border-b border-[#e6e2da] bg-white px-8 flex items-center justify-between shrink-0 sticky top-0 z-20">
      {/* Left: Breadcrumbs */}
      <div className="flex items-center space-x-2 text-xs font-mono tracking-wider font-semibold">
        <span className="text-[#84948f]"># HEALTH INTELLIGENCE</span>
        <span className="text-[#c4cec9]">/</span>
        <span className="text-[#192b26]">{viewTitles[activeView] || 'DASHBOARD'}</span>
      </div>

      {/* Right: Controls & Clocks */}
      <div className="flex items-center space-x-4">
        {/* Timezone badge */}
        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-[#f2eee7] border border-[#e2ddd5] text-[11px] font-mono font-medium text-[#495b55]">
          <Clock className="w-3.5 h-3.5 text-[#7c8e88]" />
          <span>GST · UTC+04</span>
        </div>

        {/* Scenario Replay Selector Dropdown */}
        <div className="relative">
          <div className="flex items-center space-x-2 px-3 py-1 rounded bg-[#f7f5f1] border border-[#e0dad0] text-xs font-medium text-[#2d403a]">
            <Calendar className="w-3.5 h-3.5 text-[#d97736]" />
            <span className="text-[11px] font-mono text-[#788a84]">Replay mode:</span>
            <select
              value={activeScenario?.id || 'live'}
              onChange={(e) => {
                const sc = scenarios.find((s) => s.id === e.target.value);
                onSelectScenario(sc || null);
              }}
              className="bg-transparent text-xs font-semibold text-[#182622] focus:outline-none cursor-pointer"
            >
              <option value="live">Live Stream (Current Nov 2026)</option>
              {scenarios.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.id}: {s.name} ({s.site_id})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* User Pill & Switch / Logout */}
        <div className="flex items-center space-x-3 pl-2 border-l border-[#e4ded6]">
          <div className="flex items-center space-x-2">
            <div className="w-7 h-7 rounded-full bg-[#1b3e37] text-white flex items-center justify-center text-xs font-bold font-mono">
              {currentUser?.username ? currentUser.username.substring(0, 2).toUpperCase() : 'DP'}
            </div>
            <div className="hidden sm:block text-left text-xs">
              <p className="font-bold text-[#182a25] leading-none">{currentUser?.username || 'HSE Officer'}</p>
              <p className="text-[10px] text-[#71857e] leading-tight mt-0.5">
                {currentUser?.role ? currentUser.role.replace('_', ' ') : 'HSE'}
              </p>
            </div>
          </div>

          <button
            onClick={onLogout}
            title="Switch Account / Log Out"
            className="p-1.5 rounded-lg border border-[#e2ddd5] bg-[#f7f5f1] hover:bg-[#ede7dc] text-[#556963] hover:text-[#b8421c] transition-colors"
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </header>
  );
}
