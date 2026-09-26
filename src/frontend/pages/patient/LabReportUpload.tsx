import { useState, useRef, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload, FileText, CheckCircle2, Clock, Eye, Download,
  Trash2, Search, Image, File, AlertCircle,  Stethoscope, ChevronDown
} from 'lucide-react';
import { useLanguage } from '../../context/providers';
import { PageBanner } from '../../components/ui/PageBanner';

interface LabReport {
  id: string;
  name: string;
  type: string;
  uploadDate: string;
  size: string;
  status: 'processed' | 'processing' | 'failed';
  category: string;
  summary?: string;
  results?: { test: string; value: string; range: string; status: string }[];
  aiConnected?: boolean;
  metadata?: { stored_name?: string };
}

const REPORTS_API = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '') + '/reports';

const mockReports: LabReport[] = [
  {
    id: 'LR001', name: 'Complete_Blood_Count_Aug2026.pdf', type: 'application/pdf',
    uploadDate: '2026-08-18', size: '245 KB', status: 'processed', category: 'Blood Test',
    summary: 'CBC shows mild anemia (Hemoglobin: 10.2 g/dL). All other parameters within normal limits.',
    results: [
      { test: 'Hemoglobin', value: '10.2 g/dL', range: '12.0-16.0 g/dL', status: 'low' },
      { test: 'WBC Count', value: '7,500 /μL', range: '4,000-11,000 /μL', status: 'normal' },
      { test: 'Platelet Count', value: '2,50,000 /μL', range: '1,50,000-4,00,000 /μL', status: 'normal' },
      { test: 'RBC Count', value: '4.2 million/μL', range: '4.5-5.5 million/μL', status: 'low' },
    ]
  },
  {
    id: 'LR002', name: 'Lipid_Profile_Aug2026.pdf', type: 'application/pdf',
    uploadDate: '2026-08-18', size: '189 KB', status: 'processed', category: 'Blood Test',
    summary: 'Lipid profile shows borderline high LDL cholesterol. Recommend dietary modifications.',
    results: [
      { test: 'Total Cholesterol', value: '210 mg/dL', range: '<200 mg/dL', status: 'high' },
      { test: 'LDL Cholesterol', value: '140 mg/dL', range: '<100 mg/dL', status: 'high' },
      { test: 'HDL Cholesterol', value: '45 mg/dL', range: '>40 mg/dL', status: 'normal' },
      { test: 'Triglycerides', value: '150 mg/dL', range: '<150 mg/dL', status: 'normal' },
    ]
  },
  {
    id: 'LR003', name: 'ECG_Report_Sep2026.pdf', type: 'application/pdf',
    uploadDate: '2026-08-28', size: '312 KB', status: 'processed', category: 'ECG',
    summary: 'ECG shows normal sinus rhythm. No acute ST-T changes detected.',
    results: [
      { test: 'Heart Rhythm', value: 'Normal Sinus', range: 'Normal Sinus', status: 'normal' },
      { test: 'Heart Rate', value: '76 bpm', range: '60-100 bpm', status: 'normal' },
      { test: 'PR Interval', value: '0.16 sec', range: '0.12-0.20 sec', status: 'normal' },
    ]
  },
  {
    id: 'LR004', name: 'Thyroid_Panel_Jul2026.pdf', type: 'application/pdf',
    uploadDate: '2026-07-15', size: '156 KB', status: 'processed', category: 'Blood Test',
    summary: 'Thyroid function within normal limits. TSH: 2.5 mIU/L.',
    results: [
      { test: 'TSH', value: '2.5 mIU/L', range: '0.4-4.0 mIU/L', status: 'normal' },
      { test: 'Free T4', value: '1.2 ng/dL', range: '0.8-1.8 ng/dL', status: 'normal' },
    ]
  },
  {
    id: 'LR005', name: 'XRay_Chest_Sep2026.jpg', type: 'image/jpeg',
    uploadDate: '2026-09-01', size: '1.2 MB', status: 'processing', category: 'X-Ray',
    summary: 'Processing...',
  },
];

const categories = ['All', 'Blood Test', 'ECG', 'X-Ray', 'Imaging', 'Pathology'];

function getFileIcon(type: string) {
  if (type.startsWith('image/')) return <Image size={18} className="text-purple-500" />;
  if (type === 'application/pdf') return <FileText size={18} className="text-red-500" />;
  return <File size={18} className="text-gray-500" />;
}

function getStatusBadge(status: string, t: (key: string) => string) {
  if (status === 'normal') return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600">{t('lab.normal')}</span>;
  if (status === 'low') return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-600">{t('lab.low')}</span>;
  if (status === 'high') return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-50 text-red-600">{t('lab.high')}</span>;
  return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-gray-50 text-gray-500">—</span>;
}

export function LabReportUpload() {
  const { t } = useLanguage();
  const [reports, setReports] = useState<LabReport[]>(mockReports);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedReport, setExpandedReport] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let active = true;
    fetch(REPORTS_API)
      .then(response => response.ok ? response.json() as Promise<LabReport[]> : Promise.reject(new Error('Unable to load reports')))
      .then(data => { if (active) setReports(data); })
      .catch(() => { if (active) setError('Backend unavailable. Showing saved demo reports.'); });
    return () => { active = false; };
  }, []);

  const filteredReports = reports.filter(r => {
    const matchCategory = selectedCategory === 'All' || r.category === selectedCategory;
    const matchSearch = r.name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchCategory && matchSearch;
  });

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) handleFile(e.dataTransfer.files[0]);
  }, []);

  const handleFile = async (file: File) => {
    setUploading(true);
    setUploadProgress(25);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);
    try {
      setUploadProgress(55);
      const response = await fetch(`${REPORTS_API}/upload`, { method: 'POST', body: formData });
      if (!response.ok) {
        const body = await response.json().catch(() => null) as { detail?: string } | null;
        throw new Error(body?.detail || 'Report upload failed');
      }
      const report = await response.json() as LabReport;
      setReports(prev => [report, ...prev.filter(item => item.id !== report.id)]);
      setUploadProgress(100);
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : 'Report upload failed');
    } finally {
      setUploading(false);
    }
  };

  const downloadReport = async (report: LabReport) => {
    const response = await fetch(`${REPORTS_API}/${report.id}/download`);
    if (!response.ok) {
      setError('Report download failed');
      return;
    }
    const url = URL.createObjectURL(await response.blob());
    const link = document.createElement('a');
    link.href = url;
    link.download = report.name;
    link.click();
    URL.revokeObjectURL(url);
  };

  const deleteReport = async (report: LabReport) => {
    const response = await fetch(`${REPORTS_API}/${report.id}`, { method: 'DELETE' });
    if (response.ok) setReports(prev => prev.filter(item => item.id !== report.id));
    else setError('Report deletion failed');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <PageBanner
        title={t('lab.title')}
        subtitle={t('lab.desc')}
        image="https://images.unsplash.com/photo-1579154204601-01588f351e67?auto=format&fit=crop&w=1200&q=80"
      />

      {error && (
        <div className="flex items-center gap-2 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs text-amber-700">
          <AlertCircle size={14} /> {error}
        </div>
      )}

      {/* Upload Area */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`relative p-8 rounded-2xl border-2 border-dashed transition-all cursor-pointer ${
            dragActive
              ? 'border-sahaay-deep bg-sahaay-surface scale-[1.01]'
              : 'border-sahaay-deep/20 bg-white/40 hover:border-sahaay-deep/40 hover:bg-white/60'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
            onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])}
          />
          <div className="flex flex-col items-center text-center">
            <div className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-4 ${
              dragActive ? 'sahaay-gradient' : 'bg-sahaay-deep/10'
            }`}>
              <Upload size={24} className={dragActive ? 'text-white' : 'text-sahaay-deep'} />
            </div>
            <p className="text-sm font-semibold text-gray-800 mb-1">
              {dragActive ? 'Drop your file here' : t('lab.dragDrop')}
            </p>
            <p className="text-xs text-gray-400">{t('lab.browse')}</p>
          </div>
        </div>
      </motion.div>

      {/* Upload Progress */}
      <AnimatePresence>
        {uploading && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="glass-card p-4"
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="w-8 h-8 rounded-lg bg-sahaay-deep/10 flex items-center justify-center">
                <Upload size={16} className="text-sahaay-deep animate-pulse" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-800">{t('lab.uploading')}</p>
                <p className="text-[11px] text-gray-400">{uploadProgress}% {t('lab.complete')}</p>
              </div>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <motion.div
                className="h-full sahaay-gradient rounded-full"
                animate={{ width: `${uploadProgress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1 max-w-xs">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            placeholder={t('lab.search')}
            className="sahaay-input pl-9 text-sm"
          />
        </div>
        <div className="flex gap-1.5 flex-wrap">
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                selectedCategory === cat
                  ? 'sahaay-gradient text-white'
                  : 'bg-white/60 text-gray-500 hover:bg-white border border-sahaay-deep/8'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Reports List */}
      <div className="space-y-3">
        <AnimatePresence>
          {filteredReports.map((report, i) => (
            <motion.div
              key={report.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ delay: i * 0.03 }}
              className="glass-card overflow-hidden hover:shadow-md transition-all"
            >
              <div
                className="p-4 flex items-center gap-4 cursor-pointer"
                onClick={() => setExpandedReport(expandedReport === report.id ? null : report.id)}
              >
                <div className="w-10 h-10 rounded-xl bg-sahaay-surface flex items-center justify-center shrink-0">
                  {getFileIcon(report.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-gray-800 truncate">{report.name}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-[11px] text-gray-400">{report.size}</span>
                    <span className="text-[11px] text-gray-300">•</span>
                    <span className="text-[11px] text-gray-400">{report.uploadDate}</span>
                    <span className="text-[11px] text-gray-300">•</span>
                    <span className="text-[11px] text-sahaay-deep font-medium">{report.category}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  {report.status === 'processed' && (
                    <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full">
                      <CheckCircle2 size={10} /> {t('lab.processed')}
                    </span>
                  )}
                  {report.status === 'processing' && (
                    <span className="flex items-center gap-1 text-[10px] font-bold text-amber-600 bg-amber-50 px-2 py-1 rounded-full">
                      <Clock size={10} className="animate-spin" /> {t('lab.processing')}
                    </span>
                  )}
                  {report.status === 'failed' && (
                    <span className="flex items-center gap-1 text-[10px] font-bold text-red-600 bg-red-50 px-2 py-1 rounded-full">
                      <AlertCircle size={10} /> {t('lab.failed')}
                    </span>
                  )}
                  <ChevronDown size={16} className={`text-gray-300 transition-transform ${expandedReport === report.id ? 'rotate-180' : ''}`} />
                </div>
              </div>

              {/* Expanded details */}
              <AnimatePresence>
                {expandedReport === report.id && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="border-t border-sahaay-deep/6"
                  >
                    <div className="p-4">
                      {report.summary && (
                        <div className="p-3 rounded-xl bg-sahaay-surface border border-sahaay-deep/8 mb-4">
                          <div className="flex items-center gap-2 mb-2">
                            <Stethoscope size={14} className="text-sahaay-deep" />
                            <span className="text-xs font-bold text-sahaay-deep">{t('lab.aiSummary')}</span>
                          </div>
                          <p className="text-sm text-gray-700 leading-relaxed">{report.summary}</p>
                        </div>
                      )}

                      {report.results && report.results.length > 0 && (
                        <div className="mb-4">
                          <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">{t('lab.testResults')}</h4>
                          <div className="space-y-1.5">
                            {report.results.map((result, j) => (
                              <div key={j} className="flex items-center gap-3 p-2.5 rounded-lg bg-white/60">
                                <span className="text-sm text-gray-700 flex-1">{result.test}</span>
                                <span className="text-sm font-semibold text-gray-900 w-24 text-right">{result.value}</span>
                                <span className="text-[11px] text-gray-400 w-28 text-right">{result.range}</span>
                                {getStatusBadge(result.status, t)}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="flex gap-2">
                        <button className="sahaay-btn-secondary px-3 py-1.5 text-xs flex items-center gap-1.5">
                          <Eye size={12} /> {t('lab.view')}
                        </button>
                        <button onClick={(event) => { event.stopPropagation(); void downloadReport(report); }} className="sahaay-btn-secondary px-3 py-1.5 text-xs flex items-center gap-1.5">
                          <Download size={12} /> {t('lab.download')}
                        </button>
                        <button onClick={(event) => { event.stopPropagation(); void deleteReport(report); }} className="px-3 py-1.5 text-xs font-medium text-red-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors flex items-center gap-1.5 ml-auto">
                          <Trash2 size={12} /> {t('lab.delete')}
                        </button>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </AnimatePresence>

        {filteredReports.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            <FileText size={40} className="mx-auto mb-3 opacity-40" />
            <p className="text-sm font-medium">{t('lab.noReports')}</p>
            <p className="text-xs">{t('lab.uploadFirst')}</p>
          </div>
        )}
      </div>

      <div className="h-4 lg:hidden" />
    </div>
  );
}
