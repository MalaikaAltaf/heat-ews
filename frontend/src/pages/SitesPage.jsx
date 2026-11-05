import React, { useState } from 'react';
import {
  Building2,
  MapPin,
  Clock,
  Thermometer,
  Wind,
  Droplets,
  RefreshCw,
  ArrowUpRight,
  ShieldCheck,
  AlertCircle
} from 'lucide-react';

export default function SitesPage({ sites = [], onSyncSite, onSelectSite }) {
  const [syncingId, setSyncingId] = useState(null);

  const handleSync = async (siteId) => {
    setSyncingId(siteId);
    try {
      await onSyncSite(siteId);
    } finally {
      setSyncingId(null);
    }
  };

  const getTierBadge = (tier) => {
    switch (tier) {
      case 'Action':
        return 'bg-[#faece5] text-[#b8421c] border-[#f2cdbc]';
      case 'Advisory':
        return 'bg-[#fef4e8] text-[#b86f1e] border-[#f4dac0]';
      case 'Watch':
        return 'bg-[#ebf5ee] text-[#2c6e49] border-[#cfdfd5]';
      case 'Degraded':
        return 'bg-[#edf1f0] text-[#556963] border-[#d9e1df]';
      default:
        return 'bg-[#f0ede6] text-[#485e56] border-[#ddd7cc]';
    }
  };

  return (
    <div className="p-8 max-w-[1600px] mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 gap-4 border-b border-[#e6e2da]">
        <div>
          <p className="text-[11px] font-mono tracking-wider font-semibold text-[#80958e] uppercase">
            OPERATIONS / SITE REGISTER
          </p>
          <h2 className="text-2xl font-bold text-[#142621]">Abu Dhabi Construction Sites</h2>
          <p className="text-xs text-[#5f746d] mt-1">
            Fictional pilot locations monitored for thermal heat and PM2.5 environmental exposure.
          </p>
        </div>
      </div>

      {/* Sites Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {sites.map((site) => {
          const env = site.latest_environment || {};
          const isSyncing = syncingId === site.site_id;

          return (
            <div
              key={site.site_id}
              className="bg-white rounded-xl border border-[#e6e2da] p-6 shadow-sm flex flex-col justify-between hover:border-[#ccd7d3] transition-all"
            >
              <div>
                {/* Header */}
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-lg bg-[#f4f0e8] text-[#1b3e37] flex items-center justify-center font-bold font-mono">
                      <Building2 className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-bold text-[#182a25] text-base leading-tight">
                        {site.pseudonym}
                      </h3>
                      <p className="text-xs font-mono text-[#81968f] mt-0.5">{site.site_id}</p>
                    </div>
                  </div>
                  <span
                    className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${getTierBadge(
                      site.current_tier
                    )}`}
                  >
                    {site.current_tier}
                  </span>
                </div>

                {/* Metadata */}
                <div className="mt-4 pt-3 border-t border-[#f2ede6] space-y-2 text-xs text-[#637770]">
                  <div className="flex items-center space-x-2">
                    <MapPin className="w-3.5 h-3.5 text-[#91a69f]" />
                    <span>{site.region} ({site.latitude.toFixed(3)}°N, {site.longitude.toFixed(3)}°E)</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Clock className="w-3.5 h-3.5 text-[#91a69f]" />
                    <span>Timezone: {site.timezone} (UTC+04:00)</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <ShieldCheck className="w-3.5 h-3.5 text-[#91a69f]" />
                    <span>Sector: {site.sector}</span>
                  </div>
                </div>

                {/* Live Environmental Gauges */}
                <div className="mt-5 p-3 rounded-lg bg-[#faf8f4] border border-[#ede7dd] grid grid-cols-3 gap-2 text-center">
                  <div>
                    <div className="flex items-center justify-center space-x-1 text-[11px] text-[#788e87]">
                      <Thermometer className="w-3 h-3 text-[#c85a32]" />
                      <span>Temp</span>
                    </div>
                    <p className="font-bold font-mono text-sm text-[#182a25] mt-1">
                      {env.temperature_c !== undefined && env.temperature_c !== null
                        ? `${env.temperature_c}°C`
                        : '--'}
                    </p>
                  </div>

                  <div>
                    <div className="flex items-center justify-center space-x-1 text-[11px] text-[#788e87]">
                      <Droplets className="w-3 h-3 text-[#2d6a4f]" />
                      <span>Humidity</span>
                    </div>
                    <p className="font-bold font-mono text-sm text-[#182a25] mt-1">
                      {env.humidity_pct !== undefined && env.humidity_pct !== null
                        ? `${env.humidity_pct}%`
                        : '--'}
                    </p>
                  </div>

                  <div>
                    <div className="flex items-center justify-center space-x-1 text-[11px] text-[#788e87]">
                      <Wind className="w-3 h-3 text-[#a0682b]" />
                      <span>PM2.5</span>
                    </div>
                    <p className="font-bold font-mono text-sm text-[#182a25] mt-1">
                      {env.pm25 !== undefined && env.pm25 !== null ? env.pm25 : '--'}
                    </p>
                  </div>
                </div>

                {/* Status Notice */}
                <div className="mt-3 text-[11px] text-[#7a8f88] flex items-center justify-between">
                  <span>Source: {env.source || 'Open-Meteo'}</span>
                  <span
                    className={`font-semibold ${
                      env.is_stale ? 'text-[#b8421c]' : 'text-[#2c6e49]'
                    }`}
                  >
                    {env.is_stale ? 'Stale (>3h)' : 'Fresh'}
                  </span>
                </div>
              </div>

              {/* Bottom Buttons */}
              <div className="mt-6 pt-3 border-t border-[#f0ece4] flex items-center space-x-2">
                <button
                  onClick={() => handleSync(site.site_id)}
                  disabled={isSyncing}
                  className="flex-1 py-2 px-3 rounded bg-white border border-[#d6cfc5] hover:bg-[#f7f5f1] text-xs font-semibold text-[#2d403a] flex items-center justify-center space-x-1.5 transition-colors disabled:opacity-50"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isSyncing ? 'animate-spin' : ''}`} />
                  <span>{isSyncing ? 'Syncing...' : 'Sync Weather'}</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

