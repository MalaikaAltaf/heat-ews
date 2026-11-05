import React, { useState } from 'react';
import {
  Activity,
  ShieldCheck,
  User,
  Lock,
  Building2,
  ArrowRight,
  CheckCircle,
  AlertCircle,
  Zap,
  Eye,
  EyeOff
} from 'lucide-react';
import { loginUser, registerUser } from '../api';

export default function AuthPage({ onLoginSuccess }) {
  const [tab, setTab] = useState('login'); // 'login' or 'register'
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('hse_officer');
  const [siteId, setSiteId] = useState('AD_SITE_01');
  const [errorMsg, setErrorMsg] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const demoPersonas = [
    {
      username: 'hse_reem',
      password: 'password123',
      label: 'HSE Officer (Al Reem)',
      site: 'AD_SITE_01',
      badgeColor: 'bg-[#d9653b]',
      desc: 'Scoped to Al Reem high-rise construction sector.'
    },
    {
      username: 'hse_mussafah',
      password: 'password123',
      label: 'HSE Officer (Mussafah)',
      site: 'AD_SITE_02',
      badgeColor: 'bg-[#b87628]',
      desc: 'Scoped to Mussafah industrial & heavy dust corridor.'
    },
    {
      username: 'public_health_viewer',
      password: 'password123',
      label: 'District / Public Health',
      site: 'All Sites (Masked)',
      badgeColor: 'bg-[#2c6e49]',
      desc: 'Regional surveillance with <11 small-cell privacy.'
    },
    {
      username: 'admin_steward',
      password: 'password123',
      label: 'Data Steward / Admin',
      site: 'System Wide',
      badgeColor: 'bg-[#3b6662]',
      desc: 'CSV ingestion, system audits & model retraining.'
    }
  ];

  const handleLogin = async (e) => {
    if (e) e.preventDefault();
    setErrorMsg('');
    setIsLoading(true);

    try {
      const user = await loginUser(username, password);
      onLoginSuccess(user);
    } catch (err) {
      setErrorMsg(err.message || 'Login failed. Please check credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setIsLoading(true);

    try {
      const user = await registerUser({
        username,
        password,
        role,
        permitted_site_id: role === 'hse_officer' ? siteId : null
      });
      onLoginSuccess(user);
    } catch (err) {
      setErrorMsg(err.message || 'Registration failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickDemoLogin = async (persona) => {
    setErrorMsg('');
    setIsLoading(true);
    try {
      const user = await loginUser(persona.username, persona.password);
      onLoginSuccess(user);
    } catch (err) {
      setErrorMsg(err.message || 'Quick login failed.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a1714] text-[#c0cac6] flex flex-col justify-between p-6 sm:p-10 select-none">
      {/* Top Brand Bar */}
      <div className="max-w-5xl mx-auto w-full flex items-center justify-between pb-6 border-b border-[#183630]">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-[#d97736] flex items-center justify-center text-white shadow-md shadow-[#d97736]/20">
            <Activity className="w-5 h-5 stroke-[2.5]" />
          </div>
          <div>
            <h1 className="font-bold text-xl text-white tracking-wide">HEAT-EWS</h1>
            <p className="text-[11px] font-mono tracking-wider text-[#738a83] uppercase">
              Abu Dhabi · Occupational Health Surveillance
            </p>
          </div>
        </div>

        <div className="hidden sm:flex items-center space-x-2 text-xs font-mono text-[#8ca49c]">
          <ShieldCheck className="w-4 h-4 text-[#2c6e49]" />
          <span>Server-Side Scoped RBAC (SRS v3.0)</span>
        </div>
      </div>

      {/* Main Container */}
      <div className="max-w-5xl mx-auto w-full py-8 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Form: Login / Register (7 cols) */}
        <div className="lg:col-span-7 bg-[#0f231f] border border-[#1b3d36] rounded-2xl p-6 sm:p-8 shadow-xl">
          {/* Tab Switcher */}
          <div className="flex rounded-lg bg-[#0a1815] p-1 mb-6 border border-[#1a3831]">
            <button
              onClick={() => {
                setTab('login');
                setErrorMsg('');
              }}
              className={`flex-1 py-2 text-xs font-semibold rounded-md transition-all ${
                tab === 'login'
                  ? 'bg-[#1b3d36] text-white shadow'
                  : 'text-[#7d9790] hover:text-white'
              }`}
            >
              Sign In (Existing Officer)
            </button>
            <button
              onClick={() => {
                setTab('register');
                setErrorMsg('');
              }}
              className={`flex-1 py-2 text-xs font-semibold rounded-md transition-all ${
                tab === 'register'
                  ? 'bg-[#1b3d36] text-white shadow'
                  : 'text-[#7d9790] hover:text-white'
              }`}
            >
              Register New HSE Account
            </button>
          </div>

          {errorMsg && (
            <div className="p-3 mb-4 rounded-lg bg-[#3b1912] border border-[#6b2c20] text-xs text-[#f4a896] flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-[#d9653b]" />
              <span>{errorMsg}</span>
            </div>
          )}

          {tab === 'login' ? (
            /* Login Form */
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-mono uppercase tracking-wider text-[#79948c] mb-1.5 font-semibold">
                  Username
                </label>
                <div className="relative">
                  <User className="w-4 h-4 text-[#5c736c] absolute left-3.5 top-3" />
                  <input
                    type="text"
                    required
                    placeholder="e.g. hse_reem"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full bg-[#142b26] border border-[#20443c] rounded-lg pl-10 pr-3.5 py-2.5 text-xs text-white placeholder-[#4b605a] focus:outline-none focus:border-[#d97736]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-mono uppercase tracking-wider text-[#79948c] mb-1.5 font-semibold">
                  Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-[#5c736c] absolute left-3.5 top-3" />
                  <input
                    type="password"
                    required
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-[#142b26] border border-[#20443c] rounded-lg pl-10 pr-3.5 py-2.5 text-xs text-white placeholder-[#4b605a] focus:outline-none focus:border-[#d97736]"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full mt-2 py-3 rounded-lg bg-[#d97736] hover:bg-[#c4682b] text-white font-bold text-xs uppercase tracking-wider flex items-center justify-center space-x-2 transition-all shadow-md shadow-[#d97736]/20 disabled:opacity-50"
              >
                <span>{isLoading ? 'Authenticating...' : 'Sign In to Dashboard'}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>
          ) : (
            /* Register Form */
            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <label className="block text-xs font-mono uppercase tracking-wider text-[#79948c] mb-1.5 font-semibold">
                  Choose Username
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. hse_officer_ahmed"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-[#142b26] border border-[#20443c] rounded-lg px-3.5 py-2.5 text-xs text-white placeholder-[#4b605a] focus:outline-none focus:border-[#d97736]"
                />
              </div>

              <div>
                <label className="block text-xs font-mono uppercase tracking-wider text-[#79948c] mb-1.5 font-semibold">
                  Password
                </label>
                <input
                  type="password"
                  required
                  placeholder="Minimum 4 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-[#142b26] border border-[#20443c] rounded-lg px-3.5 py-2.5 text-xs text-white placeholder-[#4b605a] focus:outline-none focus:border-[#d97736]"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-mono uppercase tracking-wider text-[#79948c] mb-1.5 font-semibold">
                    Role Assignment
                  </label>
                  <select
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="w-full bg-[#142b26] border border-[#20443c] rounded-lg px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-[#d97736]"
                  >
                    <option value="hse_officer">HSE Officer (Site Scoped)</option>
                    <option value="public_health_viewer">District / Public Health Viewer</option>
                    <option value="data_steward">Data Steward / Admin</option>
                  </select>
                </div>

                {role === 'hse_officer' && (
                  <div>
                    <label className="block text-xs font-mono uppercase tracking-wider text-[#79948c] mb-1.5 font-semibold">
                      Permitted Abu Dhabi Site
                    </label>
                    <select
                      value={siteId}
                      onChange={(e) => setSiteId(e.target.value)}
                      className="w-full bg-[#142b26] border border-[#20443c] rounded-lg px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-[#d97736]"
                    >
                      <option value="AD_SITE_01">AD_SITE_01 (Al Reem Island)</option>
                      <option value="AD_SITE_02">AD_SITE_02 (Mussafah Industrial)</option>
                      <option value="AD_SITE_03">AD_SITE_03 (Khalifa City Hub)</option>
                    </select>
                  </div>
                )}
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full mt-2 py-3 rounded-lg bg-[#276e49] hover:bg-[#205b3d] text-white font-bold text-xs uppercase tracking-wider flex items-center justify-center space-x-2 transition-all shadow-md shadow-[#276e49]/20 disabled:opacity-50"
              >
                <span>{isLoading ? 'Creating Account...' : 'Register & Enter Dashboard'}</span>
                <CheckCircle className="w-4 h-4" />
              </button>
            </form>
          )}
        </div>

        {/* Right: Quick Demo Personas (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center space-x-2 text-xs font-mono uppercase tracking-wider text-[#d97736] font-bold">
            <Zap className="w-4 h-4 text-[#d97736]" />
            <span>1-Click Hackathon Evaluator Logins</span>
          </div>
          <p className="text-xs text-[#7d9790] leading-relaxed">
            Instant role switching to verify server-side site isolation and small-cell privacy safeguards without typing credentials:
          </p>

          <div className="space-y-2.5">
            {demoPersonas.map((p) => (
              <div
                key={p.username}
                onClick={() => handleQuickDemoLogin(p)}
                className="p-3.5 rounded-xl bg-[#0f231f] border border-[#1b3d36] hover:border-[#d97736]/60 hover:bg-[#142c27] transition-all cursor-pointer group shadow-sm"
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center space-x-2">
                    <span className={`w-2 h-2 rounded-full ${p.badgeColor}`}></span>
                    <span className="font-bold text-xs text-white group-hover:text-[#e58a4e] transition-colors">
                      {p.label}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-[#6c867f] uppercase">
                    {p.site}
                  </span>
                </div>
                <p className="text-[11px] text-[#7d9790] leading-relaxed">{p.desc}</p>
              </div>
            ))}
          </div>

          <div className="p-3.5 rounded-xl bg-[#0c1c18] border border-[#193630] text-[11px] text-[#69847c] space-y-1">
            <p className="font-semibold text-[#8ca49c]">Zero Worker Identifiers:</p>
            <p>No employee names, ID numbers, or individual patient EHR fields may enter the schema (SRS PRV-01).</p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="max-w-5xl mx-auto w-full text-center text-[11px] font-mono text-[#5c736c] pt-4 border-t border-[#183630]">
        HEAT-EWS · Prototype Occupational Decision Support · Abu Dhabi, UAE
      </div>
    </div>
  );
}

