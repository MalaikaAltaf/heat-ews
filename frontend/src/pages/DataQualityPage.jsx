import React, { useState } from 'react';
import {
  Database,
  UploadCloud,
  FileCheck,
  AlertCircle,
  Eye,
  EyeOff,
  ShieldAlert,
  CheckCircle,
  RefreshCw
} from 'lucide-react';
import { uploadWorkplaceCsv } from '../api';

export default function DataQualityPage({ onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [privacyPreviewMasked, setPrivacyPreviewMasked] = useState(true);

  const sampleRawRows = [
    { site: 'AD_SITE_01', date: '2026-06-15', workers: 75, incidents: 2, nearMisses: 4, absences: 3 },
    { site: 'AD_SITE_02', date: '2026-06-15', workers: 48, incidents: 0, nearMisses: 1, absences: 5 },
    { site: 'AD_SITE_03', date: '2026-06-15', workers: 92, incidents: 1, nearMisses: 3, absences: 1 },
    { site: 'AD_SITE_01', date: '2026-06-16', workers: 14, incidents: 3, nearMisses: 2, absences: 4 }, // Small cohort N=14
  ];

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setUploadResult(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    setUploadResult(null);

    try {
      const res = await uploadWorkplaceCsv(selectedFile);
      setUploadResult(res);
      if (res.success && onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (err) {
      setUploadResult({
        success: false,
        errors: [err.message || 'CSV upload failed.'],
        rows_imported: 0
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="p-8 max-w-[1600px] mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 gap-4 border-b border-[#e6e2da]">
        <div>
          <p className="text-[11px] font-mono tracking-wider font-semibold text-[#80958e] uppercase">
            SYSTEM ADMINISTRATION / INGESTION & PRIVACY
          </p>
          <h2 className="text-2xl font-bold text-[#142621]">Data Sources & Quality</h2>
          <p className="text-xs text-[#5f746d] mt-1">
            Aggregated shift CSV ingestion, provider health tracking, and small-cell privacy safeguards.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* CSV Upload Section (6 cols) */}
        <div className="lg:col-span-6 bg-white rounded-xl border border-[#e6e2da] p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-[#f0ece4]">
            <h3 className="font-bold text-sm text-[#182a25]">Upload Workplace Daily CSV</h3>
            <span className="text-xs font-mono text-[#788e87]">SRS ING-02 & PRV-01</span>
          </div>
          <p className="text-xs text-[#627770]">
            Import shift-level aggregate records (`site_id`, `shift_date`, `workers_on_shift`, `worker_hours`, `heat_incidents`, `near_misses`, `sickness_absence_count`).
          </p>

          {/* Drag & Drop Area */}
          <div className="border-2 border-dashed border-[#dcd7cc] rounded-xl p-8 text-center bg-[#faf8f4] hover:bg-[#f7f4ee] transition-colors relative">
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
            />
            <div className="flex flex-col items-center">
              <div className="w-12 h-12 rounded-full bg-[#f2ede4] text-[#1b3e37] flex items-center justify-center mb-3">
                <UploadCloud className="w-6 h-6" />
              </div>
              <p className="text-sm font-semibold text-[#182a25]">
                {selectedFile ? selectedFile.name : 'Click or drag CSV file to this area'}
              </p>
              <p className="text-[11px] text-[#7a8f88] mt-1">
                Strict privacy check: Identifiers (worker_id, name, etc.) are automatically rejected.
              </p>
            </div>
          </div>

          <button
            onClick={handleUpload}
            disabled={!selectedFile || isUploading}
            className="w-full py-2.5 rounded-lg bg-[#1b3e37] hover:bg-[#142f2a] text-white font-bold text-xs flex items-center justify-center space-x-2 transition-colors disabled:opacity-50 shadow-sm"
          >
            {isUploading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Validating & Ingesting...</span>
              </>
            ) : (
              <>
                <FileCheck className="w-4 h-4" />
                <span>Upload & Ingest Shift Feeds</span>
              </>
            )}
          </button>

          {/* Upload Result Alert */}
          {uploadResult && (
            <div
              className={`p-4 rounded-lg text-xs border ${
                uploadResult.success
                  ? 'bg-[#ebf5ee] border-[#c4e3cf] text-[#276e49]'
                  : 'bg-[#faece5] border-[#f2cdbc] text-[#a6421c]'
              }`}
            >
              {uploadResult.success ? (
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 shrink-0" />
                  <span className="font-semibold">
                    Successfully ingested {uploadResult.rows_imported} shift records! Risk evaluations recomputed.
                  </span>
                </div>
              ) : (
                <div className="space-y-1">
                  <div className="flex items-center space-x-2 font-bold">
                    <ShieldAlert className="w-4 h-4 shrink-0" />
                    <span>Upload Rejected:</span>
                  </div>
                  <ul className="list-disc pl-5 space-y-0.5 text-[11px]">
                    {uploadResult.errors?.map((err, i) => (
                      <li key={i}>{err}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Small-Cell Privacy Demonstration (6 cols) */}
        <div className="lg:col-span-6 bg-white rounded-xl border border-[#e6e2da] p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-[#f0ece4]">
            <h3 className="font-bold text-sm text-[#182a25]">Small-Cell Privacy Suppression (PRV-02)</h3>
            <button
              onClick={() => setPrivacyPreviewMasked(!privacyPreviewMasked)}
              className="flex items-center space-x-1 px-2.5 py-1 rounded bg-[#f5f1ea] border border-[#e0dad0] text-[11px] font-semibold text-[#2d403a]"
            >
              {privacyPreviewMasked ? <EyeOff className="w-3.5 h-3.5 text-[#b84a1e]" /> : <Eye className="w-3.5 h-3.5 text-[#2c6e49]" />}
              <span>{privacyPreviewMasked ? 'Masked (<11 Active)' : 'Unmasked (Internal HSE)'}</span>
            </button>
          </div>
          <p className="text-xs text-[#627770]">
            In public or outward-facing views, incident counts between 1 and 10 are strictly masked as `&lt;11` to prevent workforce identification.
          </p>

          {/* Privacy Table Preview */}
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead>
                <tr className="text-[#889d96] font-mono text-[10.5px] uppercase border-b border-[#f2ede6]">
                  <th className="pb-2 font-semibold">SITE / DATE</th>
                  <th className="pb-2 font-semibold">WORKERS</th>
                  <th className="pb-2 font-semibold">HEAT INCIDENTS</th>
                  <th className="pb-2 font-semibold">NEAR MISSES</th>
                  <th className="pb-2 font-semibold">ABSENCES</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#f5f1ea]">
                {sampleRawRows.map((r, i) => (
                  <tr key={i} className="hover:bg-[#faf7f2]">
                    <td className="py-2.5 font-mono text-[11px] font-semibold text-[#182a25]">
                      {r.site} ({r.date})
                    </td>
                    <td className="py-2.5 font-mono">{r.workers}</td>
                    <td className="py-2.5 font-mono font-semibold">
                      {privacyPreviewMasked && r.incidents > 0 && r.incidents <= 10 ? (
                        <span className="text-[#b8421c] bg-[#faece5] px-1.5 py-0.5 rounded">&lt;11</span>
                      ) : (
                        r.incidents
                      )}
                    </td>
                    <td className="py-2.5 font-mono font-semibold">
                      {privacyPreviewMasked && r.nearMisses > 0 && r.nearMisses <= 10 ? (
                        <span className="text-[#b8421c] bg-[#faece5] px-1.5 py-0.5 rounded">&lt;11</span>
                      ) : (
                        r.nearMisses
                      )}
                    </td>
                    <td className="py-2.5 font-mono font-semibold">
                      {privacyPreviewMasked && r.absences > 0 && r.absences <= 10 ? (
                        <span className="text-[#b8421c] bg-[#faece5] px-1.5 py-0.5 rounded">&lt;11</span>
                      ) : (
                        r.absences
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="p-3 rounded-lg bg-[#faf8f4] border border-[#ede7dd] text-[11px] text-[#637770]">
            <p className="font-semibold text-[#182a25]">Reconstruction Prevention:</p>
            Derived percentages and exact incident rates are also suppressed whenever underlying cells are masked.
          </div>
        </div>
      </div>
    </div>
  );
}

