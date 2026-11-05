import React from 'react';
import {
  LayoutGrid,
  Building2,
  Bell,
  CloudSun,
  LineChart,
  Database,
  Brain,
  Settings,
  Activity,
  User,
  ShieldCheck
} from 'lucide-react';

export default function Sidebar({
  activeView,
  setActiveView,
  unacknowledgedAlertsCount = 1,
  currentUser,
  onOpenSettings
}) {
  const operationsNav = [
    { id: 'overview', label: 'Overview', icon: LayoutGrid },
    { id: 'sites', label: 'Construction Sites', icon: Building2 },
    {
      id: 'alerts',
      label: 'Alerts & Actions',
      icon: Bell,
      badge: unacknowledgedAlertsCount > 0 ? unacknowledgedAlertsCount : null,
      badgeColor: 'bg-[#d9653b]'
    },
    { id: 'outlook', label: 'Exposure Outlook', icon: CloudSun },
    { id: 'analytics', label: 'Analytics', icon: LineChart }
  ];

  const administrationNav = [
    { id: 'data_quality', label: 'Data Sources & Quality', icon: Database },
    { id: 'model_eval', label: 'Model Evaluation & Monitoring', icon: Brain },
    { id: 'settings', label: 'Settings & Access', icon: Settings }
  ];

  return (
    <aside className="w-64 bg-[#0f231f] text-[#c0cac6] flex flex-col justify-between shrink-0 h-screen sticky top-0 border-r border-[#1a3832] select-none">
      {/* Top Branding */}
      <div>
        <div className="p-5 pb-6 border-b border-[#183630] flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-[#d97736] flex items-center justify-center text-white shadow-sm shadow-[#d97736]/20">
            <Activity className="w-5 h-5 stroke-[2.5]" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-white tracking-wide flex items-center">
              HEAT-EWS
            </h1>
            <p className="text-[10px] uppercase font-mono tracking-wider text-[#738a83]">
              Abu Dhabi · Operations
            </p>
          </div>
        </div>

        {/* OPERATIONS Group */}
        <div className="px-3 pt-5">
          <p className="px-3 text-[11px] font-mono uppercase tracking-wider text-[#647c74] mb-2 font-semibold">
            OPERATIONS
          </p>
          <nav className="space-y-1">
            {operationsNav.map((item) => {
              const Icon = item.icon;
              const isActive = activeView === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveView(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-[#1b3d36] text-white shadow-inner shadow-black/20'
                      : 'text-[#9ab1aa] hover:bg-[#142c27] hover:text-white'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-[#e58a4e]' : 'text-[#7d9790]'}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className={`text-[11px] font-bold px-1.5 py-0.5 rounded-full text-white ${item.badgeColor}`}>
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* SYSTEM ADMINISTRATION Group */}
        <div className="px-3 pt-6">
          <div className="border-t border-[#183630] my-3"></div>
          <p className="px-3 text-[11px] font-mono uppercase tracking-wider text-[#647c74] mb-2 font-semibold">
            SYSTEM ADMINISTRATION
          </p>
          <nav className="space-y-1">
            {administrationNav.map((item) => {
              const Icon = item.icon;
              const isActive = activeView === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveView(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-[#1b3d36] text-white shadow-inner shadow-black/20'
                      : 'text-[#9ab1aa] hover:bg-[#142c27] hover:text-white'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-[#e58a4e]' : 'text-[#7d9790]'}`} />
                    <span className="truncate">{item.label}</span>
                  </div>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Bottom Environment & User Badge */}
      <div className="p-3 border-t border-[#183630] space-y-3">
        <div className="px-3 py-2.5 rounded-lg bg-[#142925] border border-[#1d3d37] text-[11px] text-[#869f97] leading-relaxed">
          <div className="flex items-center space-x-1.5 font-semibold text-[#c8d8d3] mb-1">
            <span className="w-2 h-2 rounded-full bg-[#d97736] animate-pulse"></span>
            <span className="uppercase tracking-wider text-[10px]">Demo / Simulation</span>
          </div>
          <p className="text-[10.5px]">
            Workplace observations are synthetic. No real occupational health decisions.
          </p>
        </div>

        {/* Current User Card */}
        <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-[#142c27] border border-[#1b3b34]">
          <div
            onClick={onOpenSettings}
            className="flex items-center space-x-2.5 cursor-pointer flex-1 min-w-0"
            title="Open Account Settings"
          >
            <div className="w-7 h-7 rounded-full bg-[#204a41] border border-[#2d6459] flex items-center justify-center text-xs font-bold text-white shrink-0">
              {currentUser?.username ? currentUser.username.substring(0, 2).toUpperCase() : 'DP'}
            </div>
            <div className="text-left truncate">
              <p className="text-xs font-semibold text-white truncate">
                {currentUser?.username || 'HSE Lead'}
              </p>
              <p className="text-[10px] text-[#738e86] truncate">
                {currentUser?.role ? currentUser.role.replace('_', ' ') : 'Site Officer'}
              </p>
            </div>
          </div>
          <button
            onClick={onOpenSettings}
            title="Settings & Role Scoping"
            className="p-1 text-[#738e86] hover:text-white transition-colors"
          >
            <Settings className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </aside>
  );
}

