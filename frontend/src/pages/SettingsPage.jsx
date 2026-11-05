import React, { useState, useEffect } from 'react';
import {
  Settings,
  Shield,
  User,
  CheckCircle,
  Building2,
  Clock,
  KeyRound,
  FileCode
} from 'lucide-react';
import { fetchDemoAccounts, loginUser } from '../api';

export default function SettingsPage({ currentUser, onUserChange }) {
  const [demoAccounts, setDemoAccounts] = useState([]);
  const [activeUsername, setActiveUsername] = useState(currentUser?.username || 'hse_reem');
  const [statusMsg, setStatusMsg] = useState('');

  useEffect(() => {
    fetchDemoAccounts()
      .then(setDemoAccounts)
      .catch((err) => console.error('Failed to load demo accounts:', err));
  }, []);

  const handleSwitchAccount = async (account) => {
    try {
      const data = await loginUser(account.username, account.password);
      setActiveUsername(account.username);
      if (onUserChange) onUserChange(data);
      setStatusMsg(`Switched role to: ${account.role} (${account.username})`);
      setTimeout(() => setStatusMsg(''), 4000);
    } catch (err) {
      console.error('Account switch error:', err);
    }
  };

  return (
    <div className="p-8 max-w-[1600px] mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 gap-4 border-b border-[#e6e2da]">
        <div>
          <p className="text-[11px] font-mono tracking-wider font-semibold text-[#80958e] uppercase">
            SYSTEM ADMINISTRATION / ROLE-BASED ACCESS
          </p>
          <h2 className="text-2xl font-bold text-[#142621]">Settings & Role Access</h2>
          <p className="text-xs text-[#5f746d] mt-1">
            Server-side site scoping RBAC test accounts, UAE occupational policy configuration, and audit settings.
          </p>
        </div>
      </div>

      {statusMsg && (
        <div className="p-3 rounded-lg bg-[#eaf4ee] border border-[#c4e3cf] text-xs font-semibold text-[#276e49] flex items-center space-x-2">
          <CheckCircle className="w-4 h-4 text-[#276e49]" />
          <span>{statusMsg}</span>
        </div>
      )}

      {/* Role-Based Test Accounts Grid */}
      <div className="bg-white rounded-xl border border-[#e6e2da] p-6 shadow-sm space-y-4">
        <h3 className="font-bold text-sm text-[#182a25]">Predefined Test Accounts (SRS Section 3)</h3>
        <p className="text-xs text-[#637770]">
          Click any persona below to switch token scope and test server-side access enforcement:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          {demoAccounts.map((acc) => {
            const isActive = activeUsername === acc.username;

            return (
              <div
                key={acc.username}
                onClick={() => handleSwitchAccount(acc)}
                className={`p-4 rounded-xl border cursor-pointer transition-all ${
                  isActive
                    ? 'border-[#1b3e37] bg-[#f8f6f2] shadow-sm ring-1 ring-[#1b3e37]'
                    : 'border-[#ede7dc] bg-white hover:bg-[#faf7f2]'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <User className="w-4 h-4 text-[#d97736]" />
                    <span className="font-bold text-xs text-[#182a25]">{acc.username}</span>
                  </div>
                  {isActive && (
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#1b3e37] text-white">
                      Active
                    </span>
                  )}
                </div>

                <p className="text-xs font-semibold text-[#2b413b]">{acc.role}</p>
                <p className="text-[11px] text-[#788e87] mt-1">Site Scope: {acc.site_id}</p>

                <div className="mt-3 pt-2 border-t border-[#f0ece4] text-[10.5px] text-[#869b94]">
                  Password: <span className="font-mono">{acc.password}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* UAE Policy & Midday Break Rules */}
      <div className="bg-white rounded-xl border border-[#e6e2da] p-6 shadow-sm space-y-3">
        <h3 className="font-bold text-sm text-[#182a25]">Abu Dhabi & UAE MOHRE Occupational Policy</h3>
        <div className="space-y-2 text-xs text-[#5f746d] leading-relaxed">
          <p>
            • <strong>Midday Break Rule:</strong> Outdoor work under direct sun in open areas is restricted between 12:30 and 15:00 from 15 June to 15 September annually.
          </p>
          <p>
            • <strong>Decision Support Invariant:</strong> HEAT-EWS produces decision-support recommendations only. The app does not issue medical advice or automated shift cancellations.
          </p>
          <p>
            • <strong>Privacy Guarantee:</strong> No worker names, identification numbers, or medical EHR data enter the system. Counts 1-10 are suppressed as `&lt;11`.
          </p>
        </div>
      </div>
    </div>
  );
}

