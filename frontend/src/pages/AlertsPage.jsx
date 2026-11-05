import React, { useState } from 'react';
import {
  Bell,
  CheckCircle,
  AlertTriangle,
  Clock,
  Shield,
  Send,
  UserCheck,
  Check,
  Info,
  ArrowUpRight
} from 'lucide-react';

export default function AlertsPage({
  alerts = [],
  onAcknowledge,
  onLogAction
}) {
  const [selectedAlert, setSelectedAlert] = useState(alerts[0] || null);
  const [actionNotes, setActionNotes] = useState('');
  const [selectedActionCode, setSelectedActionCode] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const currentAlert = selectedAlert || alerts[0];

  const handleAcknowledge = async () => {
    if (!currentAlert) return;
    setIsSubmitting(true);
    try {
      await onAcknowledge(currentAlert.alert_id);
      setSuccessMessage('Alert successfully acknowledged and logged to audit trail.');
      setTimeout(() => setSuccessMessage(''), 4000);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleExecuteAction = async () => {
    if (!currentAlert || !selectedActionCode) return;
    setIsSubmitting(true);
    try {
      await onLogAction(currentAlert.alert_id, selectedActionCode, actionNotes);
      setSuccessMessage('Preventive action logged successfully.');
      setActionNotes('');
      setTimeout(() => setSuccessMessage(''), 4000);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="p-8 max-w-[1600px] mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 gap-4 border-b border-[#e6e2da]">
        <div>
          <p className="text-[11px] font-mono tracking-wider font-semibold text-[#80958e] uppercase">
            OPERATIONS / DECISION SUPPORT
          </p>
          <h2 className="text-2xl font-bold text-[#142621]">Alerts & Action Playbook</h2>
          <p className="text-xs text-[#5f746d] mt-1">
            Evidence cards, multi-signal explanations, and role-specific HSE mitigation workflows.
          </p>
        </div>
      </div>

      {successMessage && (
        <div className="p-3 rounded-lg bg-[#eaf4ee] border border-[#c4e3cf] text-xs font-semibold text-[#276e49] flex items-center space-x-2">
          <CheckCircle className="w-4 h-4 text-[#276e49]" />
          <span>{successMessage}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Alerts Queue (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-xl border border-[#e6e2da] p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-[#f0ece4]">
            <h3 className="font-bold text-sm text-[#182a25]">Active & Recent Alerts</h3>
            <span className="text-xs font-mono text-[#788e87]">{alerts.length} total</span>
          </div>

          <div className="space-y-2.5 max-h-[650px] overflow-y-auto pr-1">
            {alerts.length === 0 ? (
              <div className="p-8 text-center text-xs text-[#788e87]">
                No active alerts. All sites are operating within baseline thresholds.
              </div>
            ) : (
              alerts.map((alt) => {
                const isSelected = currentAlert?.alert_id === alt.alert_id;
                const isAck = !!alt.acknowledged_at;

                return (
                  <div
                    key={alt.alert_id}
                    onClick={() => setSelectedAlert(alt)}
                    className={`p-3.5 rounded-lg border cursor-pointer transition-all ${
                      isSelected
                        ? 'border-[#1b3e37] bg-[#f8f6f2] shadow-sm'
                        : 'border-[#ede7dc] bg-white hover:bg-[#faf7f2]'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-bold text-[#182a25]">{alt.site_id}</span>
                      <span
                        className={`text-[10.5px] font-semibold px-2 py-0.5 rounded-full ${
                          alt.tier === 'Action'
                            ? 'bg-[#faece5] text-[#b8421c]'
                            : alt.tier === 'Advisory'
                            ? 'bg-[#fef4e8] text-[#b86f1e]'
                            : 'bg-[#ebf5ee] text-[#2c6e49]'
                        }`}
                      >
                        {alt.tier}
                      </span>
                    </div>

                    <p className="text-xs font-semibold text-[#273a34] mt-1.5 truncate">
                      {alt.evidence?.site_name || alt.site_id}
                    </p>

                    <div className="flex items-center justify-between text-[11px] text-[#788e87] mt-2">
                      <span>{new Date(alt.issued_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} GST</span>
                      <span className={isAck ? 'text-[#2c6e49] font-medium' : 'text-[#d9653b] font-medium'}>
                        {isAck ? '✓ Acknowledged' : '● Action pending'}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right: Evidence Card & Playbook Actions (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-xl border border-[#e6e2da] p-6 shadow-sm space-y-6">
          {currentAlert ? (
            <>
              {/* Evidence Card Header */}
              <div className="pb-4 border-b border-[#f0ece4]">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono tracking-wider text-[#7e948c] uppercase font-semibold">
                    EVIDENCE CARD · {currentAlert.alert_id}
                  </span>
                  <span className="text-xs font-mono font-bold text-[#b84a1e] uppercase">
                    {currentAlert.tier} TIER
                  </span>
                </div>
                <h3 className="text-xl font-bold text-[#182a25] mt-1">
                  {currentAlert.evidence?.site_name || currentAlert.site_id}
                </h3>
                <p className="text-xs text-[#637770] mt-0.5">
                  Issued at: {new Date(currentAlert.issued_at).toLocaleString()}
                </p>
              </div>

              {/* Observed Measurements Breakdown */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                <div className="p-3 rounded-lg bg-[#faf8f4] border border-[#eee8df]">
                  <span className="text-[11px] font-mono text-[#788e87]">Temperature</span>
                  <p className="font-bold font-mono text-base text-[#182a25] mt-1">
                    {currentAlert.evidence?.measurements?.temperature_c ?? '--'}°C
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-[#faf8f4] border border-[#eee8df]">
                  <span className="text-[11px] font-mono text-[#788e87]">Heat Index</span>
                  <p className="font-bold font-mono text-base text-[#c85a32] mt-1">
                    {currentAlert.evidence?.measurements?.heat_index_c ?? '--'}°C
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-[#faf8f4] border border-[#eee8df]">
                  <span className="text-[11px] font-mono text-[#788e87]">PM2.5 (Dust)</span>
                  <p className="font-bold font-mono text-base text-[#182a25] mt-1">
                    {currentAlert.evidence?.measurements?.pm25 ?? '--'}
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-[#faf8f4] border border-[#eee8df]">
                  <span className="text-[11px] font-mono text-[#788e87]">ML Risk Score</span>
                  <p className="font-bold font-mono text-base text-[#2d6a4f] mt-1">
                    {currentAlert.evidence?.ml_classifier?.ml_score ?? '0.45'}
                  </p>
                </div>
              </div>

              {/* Scientific Disclaimer */}
              <div className="p-3 rounded-lg bg-[#f7f5f0] border border-[#e4ded4] flex items-start space-x-2 text-xs text-[#677c75] leading-relaxed">
                <Info className="w-4 h-4 text-[#8a9f98] shrink-0 mt-0.5" />
                <span>
                  {currentAlert.evidence?.ml_classifier?.disclaimer ||
                    'Alerts are decision-support recommendations. Not a clinically validated diagnosis.'}
                </span>
              </div>

              {/* Prevention Playbook Actions */}
              <div className="p-4 rounded-xl bg-[#faf7f2] border border-[#e8e2d5] space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-sm text-[#182a25]">
                    {currentAlert.playbook?.title || 'Prevention Playbook'}
                  </h4>
                  <span className="text-[11px] font-mono text-[#b84a1e] font-semibold">
                    {currentAlert.playbook?.urgency || 'Action required'}
                  </span>
                </div>
                <p className="text-xs text-[#5f746d]">
                  {currentAlert.playbook?.recommended_response}
                </p>

                {/* Available Action Options */}
                <div className="space-y-2 pt-2">
                  <p className="text-[11px] font-mono text-[#7a8f88] uppercase font-semibold">
                    SELECT PREVENTIVE ACTION TO LOG:
                  </p>
                  {(currentAlert.playbook?.actions || [
                    { code: 'ACT_INSPECT_SHADE', label: 'Inspect shaded resting zones and cooling' },
                    { code: 'ACT_HYDRATION_SCHEDULE', label: 'Enforce mandatory hydration breaks' },
                    { code: 'ACT_RETIME_TASKS', label: 'Reschedule high-exertion outdoor tasks' }
                  ]).map((act) => (
                    <label
                      key={act.code}
                      className={`flex items-center space-x-2.5 p-2.5 rounded-lg border cursor-pointer transition-all text-xs ${
                        selectedActionCode === act.code
                          ? 'border-[#1b3e37] bg-white font-semibold shadow-sm'
                          : 'border-[#e4ded4] bg-white/70 hover:bg-white'
                      }`}
                    >
                      <input
                        type="radio"
                        name="playbookAction"
                        value={act.code}
                        checked={selectedActionCode === act.code}
                        onChange={() => setSelectedActionCode(act.code)}
                        className="text-[#1b3e37] focus:ring-0"
                      />
                      <span>{act.label}</span>
                    </label>
                  ))}
                </div>

                {/* Notes Input */}
                <div className="pt-2">
                  <textarea
                    rows={2}
                    placeholder="Optional HSE Officer shift notes / execution feedback..."
                    value={actionNotes}
                    onChange={(e) => setActionNotes(e.target.value)}
                    className="w-full text-xs p-2.5 rounded-lg border border-[#ded8cb] bg-white focus:outline-none focus:border-[#1b3e37]"
                  />
                </div>

                {/* Action Buttons */}
                <div className="flex items-center space-x-3 pt-2">
                  {!currentAlert.acknowledged_at && (
                    <button
                      onClick={handleAcknowledge}
                      disabled={isSubmitting}
                      className="flex-1 py-2 px-4 rounded-lg bg-white border border-[#1b3e37] text-xs font-bold text-[#1b3e37] hover:bg-[#f2ede6] transition-colors disabled:opacity-50"
                    >
                      Acknowledge Alert
                    </button>
                  )}
                  <button
                    onClick={handleExecuteAction}
                    disabled={isSubmitting || !selectedActionCode}
                    className="flex-1 py-2 px-4 rounded-lg bg-[#1b3e37] hover:bg-[#142f2a] text-xs font-bold text-white transition-colors disabled:opacity-50 shadow-sm"
                  >
                    Log Preventive Action
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="p-12 text-center text-xs text-[#788e87]">
              Select an alert from the queue to view evidence and execute actions.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

