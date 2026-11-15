const { useState, useEffect, useRef } = React;

function BrandGuardApp() {
  // Navigation & Locale state
  const [currentPage, setCurrentPage] = useState('home');
  const [lang, setLang] = useState('en');
  const [token, setToken] = useState(localStorage.getItem('bg_token') || '');
  const [user, setUser] = useState({
    id: 1,
    full_name: "Sarah Jenkins (Admin)",
    email: "admin@brandguard.ai",
    role: "ADMIN",
    department: "Executive",
    org_id: 1,
    organisation_name: "Nexura Technologies"
  });

  // Translation helper
  const t = (key) => {
    const dict = window.I18N_TRANSLATIONS ? window.I18N_TRANSLATIONS[lang] || window.I18N_TRANSLATIONS['en'] : {};
    return dict[key] || key;
  };

  // Switch demo role
  const switchRole = async (targetRole) => {
    try {
      const res = await fetch(`/api/auth/demo-switch?role=${targetRole}`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setToken(data.access_token);
        setUser(data.user);
        localStorage.setItem('bg_token', data.access_token);
      }
    } catch (e) {
      console.error("Demo switch failed:", e);
    }
  };

  // Re-render Lucide icons on DOM updates
  useEffect(() => {
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }, [currentPage, lang, user]);

  return (
    <div className="flex h-screen overflow-hidden bg-[#0B0F19] text-gray-100 font-sans">
      {/* LEFT COMPACT SIDEBAR (230px) */}
      <aside className="w-[230px] flex-shrink-0 flex flex-col bg-[#0F172A] border-r border-gray-800 select-none z-30">
        {/* Brand Header */}
        <div className="h-16 flex items-center px-4 gap-3 border-b border-gray-800 bg-[#0B0F19]/50 cursor-pointer" onClick={() => setCurrentPage('home')}>
          <img src="/static/logo.png" alt="Logo" className="w-8 h-8 rounded-lg shadow-md" />
          <div className="overflow-hidden">
            <h1 className="font-bold text-sm tracking-wider text-white font-mono uppercase bg-gradient-to-r from-blue-400 via-indigo-300 to-cyan-300 bg-clip-text text-transparent">
              BRANDGUARD
            </h1>
            <p className="text-[10px] text-gray-400 truncate">Intelligence Platform</p>
          </div>
        </div>

        {/* Sidebar Nav Items */}
        <nav className="flex-1 px-3 py-4 space-y-1.5 overflow-y-auto">
          {[
            { id: 'overview', icon: 'layout-dashboard', label: t('nav_overview') },
            { id: 'scanner', icon: 'scan-text', label: t('nav_scanner') },
            { id: 'brain', icon: 'brain-circuit', label: t('nav_brain') },
            { id: 'visual', icon: 'eye', label: t('nav_visual') },
            { id: 'rewrite', icon: 'wand2', label: t('nav_rewrite') },
            { id: 'review', icon: 'clipboard-check', label: t('nav_review') },
            { id: 'analytics', icon: 'bar-chart-3', label: t('nav_analytics') },
            { id: 'settings', icon: 'settings', label: t('nav_settings') },
          ].map((item) => {
            const isActive = currentPage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentPage(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/20 font-semibold'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/60'
                }`}
              >
                <i data-lucide={item.icon} className={`w-4 h-4 ${isActive ? 'text-white' : 'text-gray-400'}`}></i>
                <span className="truncate">{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Role Switcher Pill in Sidebar Footer */}
        <div className="p-3 border-t border-gray-800 bg-[#0B0F19]/40">
          <div className="text-[10px] uppercase font-semibold text-gray-400 mb-1.5 flex items-center justify-between">
            <span>{t('switch_role')}</span>
            <span className="px-1.5 py-0.5 rounded text-[9px] bg-blue-900/60 text-blue-300 font-mono">{user.role}</span>
          </div>
          <div className="grid grid-cols-3 gap-1">
            {['ADMIN', 'CREATOR', 'REVIEWER'].map((r) => (
              <button
                key={r}
                onClick={() => switchRole(r)}
                className={`py-1 text-[10px] font-medium rounded transition ${
                  user.role === r
                    ? 'bg-blue-600 text-white font-bold'
                    : 'bg-gray-800/80 text-gray-300 hover:bg-gray-700'
                }`}
              >
                {r[0] + r.slice(1).toLowerCase()}
              </button>
            ))}
          </div>
        </div>
      </aside>

      {/* MAIN VIEWPORT */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* TOP HEADER */}
        <header className="h-16 flex-shrink-0 flex items-center justify-between px-6 border-b border-gray-800 bg-[#0F172A]/70 backdrop-blur-md z-20">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setCurrentPage('home')}
              className="text-xs text-gray-400 hover:text-white flex items-center gap-1.5 transition"
            >
              <i data-lucide="home" className="w-4 h-4"></i>
              <span>Home</span>
            </button>
            <span className="text-gray-600">/</span>
            <span className="text-xs font-semibold text-blue-400 capitalize">{currentPage}</span>
          </div>

          <div className="flex items-center gap-4">
            {/* Bilingual Switcher */}
            <div className="flex items-center bg-gray-800 rounded-lg p-0.5 border border-gray-700">
              <button
                onClick={() => setLang('en')}
                className={`px-2.5 py-1 text-xs rounded font-medium transition ${
                  lang === 'en' ? 'bg-blue-600 text-white font-bold shadow' : 'text-gray-400 hover:text-gray-200'
                }`}
              >
                English
              </button>
              <button
                onClick={() => setLang('ta')}
                className={`px-2.5 py-1 text-xs rounded font-medium transition ${
                  lang === 'ta' ? 'bg-blue-600 text-white font-bold shadow' : 'text-gray-400 hover:text-gray-200'
                }`}
              >
                தமிழ்
              </button>
            </div>

            {/* Active User Badge */}
            <div className="flex items-center gap-2.5 pl-3 border-l border-gray-800">
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-xs font-bold text-white shadow">
                {user.full_name ? user.full_name.charAt(0) : 'U'}
              </div>
              <div className="hidden sm:block text-left">
                <p className="text-xs font-semibold text-white leading-tight">{user.full_name}</p>
                <p className="text-[10px] text-gray-400 leading-tight">{user.department} • <span className="text-blue-400 font-mono">{user.role}</span></p>
              </div>
            </div>
          </div>
        </header>

        {/* BODY CONTENT AREA */}
        <main className="flex-1 overflow-y-auto bg-[#0B0F19]">
          {currentPage === 'home' && <HomePage t={t} onNavigate={setCurrentPage} />}
          {currentPage === 'overview' && <OverviewPage t={t} user={user} onNavigate={setCurrentPage} />}
          {currentPage === 'scanner' && <ScannerPage t={t} user={user} onNavigate={setCurrentPage} />}
          {currentPage === 'brain' && <BrainPage t={t} user={user} />}
          {currentPage === 'visual' && <VisualPage t={t} user={user} />}
          {currentPage === 'rewrite' && <RewritePage t={t} user={user} />}
          {currentPage === 'review' && <ReviewPage t={t} user={user} />}
          {currentPage === 'analytics' && <AnalyticsPage t={t} user={user} />}
          {currentPage === 'settings' && <SettingsPage t={t} user={user} />}
        </main>
      </div>
    </div>
  );
}

// ----------------- 1. HOME PAGE WITH REAL BACKGROUND IMAGE -----------------
function HomePage({ t, onNavigate }) {
  return (
    <div className="relative min-h-full flex flex-col justify-between">
      {/* Real Full-Width Hero Background Image with Subtle Dark Overlay */}
      <div 
        className="relative py-24 px-6 md:px-16 overflow-hidden border-b border-gray-800 bg-cover bg-center"
        style={{ backgroundImage: `url('/static/hero-bg.jpg')` }}
      >
        <div className="absolute inset-0 hero-overlay"></div>
        <div className="relative max-w-5xl mx-auto text-center z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-medium mb-6">
            <i data-lucide="shield-check" className="w-4 h-4 text-blue-400"></i>
            <span>Intelligent Brand Governance & Content Intelligence Platform</span>
          </div>

          <h1 className="text-4xl md:text-6xl font-extrabold text-white tracking-tight leading-tight mb-4">
            {t('hero_headline')}
          </h1>

          <p className="text-lg md:text-xl text-blue-200/90 font-medium italic mb-4 max-w-3xl mx-auto">
            "{t('tagline')}"
          </p>

          <p className="text-sm md:text-base text-gray-300 max-w-2xl mx-auto mb-8 leading-relaxed">
            {t('hero_sub')}
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4">
            <button
              onClick={() => onNavigate('scanner')}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 text-white font-semibold text-sm shadow-xl shadow-blue-500/30 hover:scale-[1.02] active:scale-[0.98] transition flex items-center gap-2"
            >
              <i data-lucide="scan-text" className="w-4 h-4"></i>
              <span>{t('btn_start_analysing')}</span>
            </button>
            <button
              onClick={() => onNavigate('overview')}
              className="px-6 py-3 rounded-xl bg-gray-900/80 hover:bg-gray-800 text-gray-200 border border-gray-700 text-sm font-semibold transition flex items-center gap-2"
            >
              <i data-lucide="layout-dashboard" className="w-4 h-4"></i>
              <span>{t('btn_view_dashboard')}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Key Product Capabilities Grid */}
      <div className="max-w-6xl mx-auto px-6 py-12 w-full">
        <h2 className="text-xl font-bold text-white text-center mb-8">
          Core AI Governance Engine Modules
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              icon: "brain-circuit",
              title: "Brand Intelligence Brain",
              desc: "Single source of truth for tone of voice, terminology, visual guidelines, and certified company facts with source attribution.",
              color: "text-blue-400",
              border: "hover:border-blue-500/50"
            },
            {
              icon: "file-check-2",
              title: "Evidence-Based Claim Verification",
              desc: "Cross-checks promotional claims against approved company facts. Flags contradictions and unverified claims without inventing evidence.",
              color: "text-emerald-400",
              border: "hover:border-emerald-500/50"
            },
            {
              icon: "eye",
              title: "Visual Brand Guardian",
              desc: "Computer vision engine inspecting creative posters, color palette harmony, WCAG contrast ratios, and logo positioning quadrant.",
              color: "text-cyan-400",
              border: "hover:border-cyan-500/50"
            },
            {
              icon: "wand2",
              title: "AI Smart Rewrite Studio",
              desc: "Offers three distinct brand-compliant rewrite options (Professional, Friendly, Marketing) with side-by-side diffs and manual control.",
              color: "text-violet-400",
              border: "hover:border-violet-500/50"
            },
            {
              icon: "git-pull-request",
              title: "Human-in-the-Loop Workflow",
              desc: "Role-based approvals (Admin, Creator, Reviewer). Prevents automated unauthorized publication with strict audit trail tracking.",
              color: "text-rose-400",
              border: "hover:border-rose-500/50"
            },
            {
              icon: "sparkles",
              title: "Guideline Clarity Analyzer",
              desc: "Meta-audits organizational guidelines to detect contradictory rules, ambiguous phrasing, and missing terminology definitions.",
              color: "text-amber-400",
              border: "hover:border-amber-500/50"
            }
          ].map((item, idx) => (
            <div key={idx} className={`glass-card p-6 rounded-2xl border border-gray-800 transition duration-200 ${item.border}`}>
              <div className="w-10 h-10 rounded-xl bg-gray-800/80 flex items-center justify-center mb-4">
                <i data-lucide={item.icon} className={`w-5 h-5 ${item.color}`}></i>
              </div>
              <h3 className="text-sm font-bold text-white mb-2">{item.title}</h3>
              <p className="text-xs text-gray-400 leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Human Oversight & Trust Banner */}
      <div className="bg-[#0F172A] border-t border-gray-800 py-6 px-6">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-center md:text-left">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <i data-lucide="lock" className="w-4 h-4"></i>
            </div>
            <div>
              <p className="text-xs font-semibold text-white">Strict Privacy & No Blind Approvals</p>
              <p className="text-[11px] text-gray-400">All claims require human verification. Zero confidential data leakage to external models.</p>
            </div>
          </div>
          <button
            onClick={() => onNavigate('overview')}
            className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition"
          >
            Launch Governance Workspace →
          </button>
        </div>
      </div>
    </div>
  );
}

// ----------------- 2. OVERVIEW / DASHBOARD PAGE -----------------
function OverviewPage({ t, user, onNavigate }) {
  const [analytics, setAnalytics] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [aRes, sRes] = await Promise.all([
          fetch('/api/analytics/overview'),
          fetch('/api/scanner/submissions')
        ]);
        if (aRes.ok) setAnalytics(await aRes.json());
        if (sRes.ok) setSubmissions(await sRes.json());
      } catch (err) {
        console.error("Failed to load overview data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-blue-900/30 via-indigo-900/20 to-purple-900/20 p-6 rounded-2xl border border-blue-500/20">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <span>{t('nav_overview')}</span>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 font-mono">Nexura Technologies</span>
          </h1>
          <p className="text-xs text-gray-400 mt-1">Real-time enterprise compliance telemetry & approval velocity.</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate('scanner')}
            className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow transition"
          >
            <i data-lucide="plus-circle" className="w-3.5 h-3.5"></i>
            <span>Scan New Draft</span>
          </button>
          <button
            onClick={() => onNavigate('visual')}
            className="px-4 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 text-xs font-semibold flex items-center gap-1.5 transition"
          >
            <i data-lucide="image" className="w-3.5 h-3.5"></i>
            <span>Visual Guardian</span>
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        {[
          { label: t('kpi_total_scanned'), val: analytics?.total_scanned ?? 0, icon: "files", color: "text-blue-400" },
          { label: t('kpi_approved'), val: analytics?.approved_count ?? 0, icon: "check-circle", color: "text-emerald-400" },
          { label: t('kpi_pending'), val: analytics?.pending_count ?? 0, icon: "clock", color: "text-amber-400" },
          { label: t('kpi_rejected'), val: analytics?.rejected_count ?? 0, icon: "x-circle", color: "text-rose-400" },
          { label: t('kpi_critical'), val: analytics?.critical_issues_count ?? 0, icon: "alert-triangle", color: "text-coral-400" },
          { label: t('kpi_avg_score'), val: `${analytics?.average_compliance_score ?? 100}%`, icon: "shield-check", color: "text-indigo-400" },
        ].map((kpi, idx) => (
          <div key={idx} className="glass-card p-4 rounded-xl border border-gray-800 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] text-gray-400 font-medium line-clamp-1">{kpi.label}</span>
              <i data-lucide={kpi.icon} className={`w-4 h-4 ${kpi.color}`}></i>
            </div>
            <p className="text-2xl font-extrabold text-white">{kpi.val}</p>
          </div>
        ))}
      </div>

      {/* Recent Submissions Table */}
      <div className="glass-card rounded-2xl border border-gray-800 overflow-hidden">
        <div className="p-4 border-b border-gray-800 flex items-center justify-between">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <i data-lucide="history" className="w-4 h-4 text-blue-400"></i>
            <span>Recent Content Governance Submissions</span>
          </h2>
          <button
            onClick={() => onNavigate('review')}
            className="text-xs text-blue-400 hover:text-blue-300 font-medium transition"
          >
            View All in Approval Hub →
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-900/60 text-gray-400 uppercase text-[10px] font-semibold border-b border-gray-800">
              <tr>
                <th className="py-3 px-4">Title / Campaign</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Department</th>
                <th className="py-3 px-4">Language</th>
                <th className="py-3 px-4">Score</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {submissions.map((s) => (
                <tr key={s.id} className="hover:bg-gray-800/30 transition">
                  <td className="py-3 px-4 font-medium text-white max-w-[220px] truncate">{s.title}</td>
                  <td className="py-3 px-4 text-gray-300 capitalize">{s.content_type.replace('_', ' ')}</td>
                  <td className="py-3 px-4 text-gray-400">{s.department}</td>
                  <td className="py-3 px-4 uppercase font-mono text-[10px] text-gray-300">{s.language}</td>
                  <td className="py-3 px-4 font-semibold text-blue-400">{s.overall_score !== null ? `${s.overall_score}%` : 'N/A'}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${
                      s.status === 'Approved' ? 'badge-low' :
                      s.status === 'Revision Requested' ? 'badge-high' :
                      s.status === 'Rejected' ? 'badge-critical' : 'badge-medium'
                    }`}>
                      {s.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => onNavigate('review')}
                      className="px-2.5 py-1 rounded bg-gray-800 hover:bg-gray-700 text-blue-400 text-[11px] font-medium transition"
                    >
                      Examine
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ----------------- 3. CONTENT SCANNER WORKSPACE -----------------
function ScannerPage({ t, user, onNavigate }) {
  const [tab, setTab] = useState('text'); // text, upload, url
  const [title, setTitle] = useState('');
  const [contentType, setContentType] = useState('press_release');
  const [language, setLanguage] = useState('en');
  const [department, setDepartment] = useState('Marketing');
  const [rawText, setRawText] = useState('');
  const [webUrl, setWebUrl] = useState('');
  const [file, setFile] = useState(null);

  const [scanning, setScanning] = useState(false);
  const [scanStep, setScanStep] = useState(0);
  const [scanResult, setScanResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  // Preload test case with known violations
  const loadViolationDemo = () => {
    setTitle("Q4 Enterprise Product Launch Copy");
    setContentType("press_release");
    setLanguage("en");
    setRawText("Nexura is proud to announce Product X. Product X offers a lifetime warranty with zero downtime forever! It is a cheap, foolproof solution that cuts costs by 99% guaranteed. Our revolutionary secret sauce is gonna blow away the competition!!!");
  };

  const loadTamilDemo = () => {
    setTitle("தமிழ் தயாரிப்பு வெளியீட்டு அறிவிப்பு");
    setContentType("social");
    setLanguage("ta");
    setRawText("நெக்சுரா கிளவுட் தளம் மூலம் உங்கள் நிறுவனத்தை பாதுகாக்கவும். 100% இலவசம் மற்றும் வாழ்நாள் உத்தரவாதம் வழங்குகிறோம்.");
  };

  const handleScan = async () => {
    setErrorMsg('');
    if (!title.trim()) {
      setErrorMsg('Please specify a Content Title or Campaign Name.');
      return;
    }
    if (tab === 'text' && !rawText.trim()) {
      setErrorMsg('Please enter or paste the content to analyze.');
      return;
    }
    if (tab === 'url' && !webUrl.trim()) {
      setErrorMsg('Please enter a valid website URL.');
      return;
    }
    if (tab === 'upload' && !file) {
      setErrorMsg('Please select a file to upload (PDF, DOCX, TXT, CSV).');
      return;
    }

    setScanning(true);
    setScanStep(1);

    const stepInterval = setInterval(() => {
      setScanStep((prev) => (prev < 4 ? prev + 1 : prev));
    }, 450);

    try {
      let res;
      if (tab === 'upload') {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', title);
        formData.append('content_type', contentType);
        formData.append('language', language);
        formData.append('department', department);
        res = await fetch('/api/scanner/upload', { method: 'POST', body: formData });
      } else {
        const body = {
          title,
          content_type: contentType,
          raw_text: tab === 'text' ? rawText : undefined,
          source_url: tab === 'url' ? webUrl : undefined,
          language,
          department
        };
        res = await fetch('/api/scanner/scan', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        });
      }

      clearInterval(stepInterval);
      if (res.ok) {
        const data = await res.json();
        setScanResult(data);
      } else {
        const err = await res.json();
        setErrorMsg(err.detail || 'Scan processing failed.');
      }
    } catch (e) {
      clearInterval(stepInterval);
      setErrorMsg('Network error connecting to analysis engine: ' + e.toString());
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Title & Description */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <i data-lucide="scan-text" className="w-5 h-5 text-blue-400"></i>
            <span>{t('scanner_title')}</span>
          </h1>
          <p className="text-xs text-gray-400 mt-1">{t('scanner_desc')}</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={loadViolationDemo}
            className="px-3 py-1.5 rounded-lg bg-indigo-900/40 hover:bg-indigo-900/60 text-indigo-300 border border-indigo-700/50 text-xs font-medium transition"
          >
            Load Sample Violations (EN)
          </button>
          <button
            onClick={loadTamilDemo}
            className="px-3 py-1.5 rounded-lg bg-blue-900/40 hover:bg-blue-900/60 text-blue-300 border border-blue-700/50 text-xs font-medium transition"
          >
            Load Tamil Sample (தமிழ்)
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="p-3 rounded-lg bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
          <i data-lucide="alert-circle" className="w-4 h-4"></i>
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Input Form & Tab Selector */}
      <div className="glass-card p-5 rounded-2xl border border-gray-800 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-[11px] font-semibold text-gray-300 mb-1">{t('label_content_name')}</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Q4 Cloud Launch Release"
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-[11px] font-semibold text-gray-300 mb-1">{t('label_content_type')}</label>
            <select
              value={contentType}
              onChange={(e) => setContentType(e.target.value)}
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
            >
              <option value="press_release">Press Release</option>
              <option value="ad">Advertisement / Ad Copy</option>
              <option value="social">Social Media Post</option>
              <option value="email">Marketing Email / Newsletter</option>
              <option value="blog">Technical Blog Post</option>
              <option value="website">Website Landing Page</option>
              <option value="product_description">Product Description</option>
            </select>
          </div>
          <div>
            <label className="block text-[11px] font-semibold text-gray-300 mb-1">{t('label_department')}</label>
            <select
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
            >
              <option value="Marketing">Marketing</option>
              <option value="Product">Product Management</option>
              <option value="Public Relations">Public Relations (PR)</option>
              <option value="Social Media">Social Media Team</option>
              <option value="Legal">Legal & Compliance</option>
            </select>
          </div>
          <div>
            <label className="block text-[11px] font-semibold text-gray-300 mb-1">{t('label_language')}</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
            >
              <option value="en">English (US/UK)</option>
              <option value="ta">தமிழ் (Tamil)</option>
            </select>
          </div>
        </div>

        {/* Input Method Selector */}
        <div className="flex border-b border-gray-800 pt-2 gap-4">
          {[
            { id: 'text', label: t('input_paste_text'), icon: 'align-left' },
            { id: 'upload', label: t('input_upload_file'), icon: 'upload-cloud' },
            { id: 'url', label: t('input_web_url'), icon: 'globe' },
          ].map((tabItem) => (
            <button
              key={tabItem.id}
              onClick={() => setTab(tabItem.id)}
              className={`pb-2 text-xs font-semibold flex items-center gap-2 border-b-2 transition ${
                tab === tabItem.id
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-gray-400 hover:text-gray-200'
              }`}
            >
              <i data-lucide={tabItem.icon} className="w-3.5 h-3.5"></i>
              <span>{tabItem.label}</span>
            </button>
          ))}
        </div>

        {/* Dynamic Inputs based on Tab */}
        {tab === 'text' && (
          <div>
            <textarea
              rows={6}
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              placeholder={t('placeholder_text')}
              className="w-full p-3 bg-gray-900/90 border border-gray-700 rounded-xl text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 font-mono leading-relaxed"
            ></textarea>
          </div>
        )}

        {tab === 'upload' && (
          <div className="border-2 border-dashed border-gray-700 rounded-xl p-8 text-center bg-gray-900/40 hover:bg-gray-900/60 transition">
            <i data-lucide="file-up" className="w-8 h-8 text-blue-400 mx-auto mb-2"></i>
            <p className="text-xs font-medium text-white mb-1">Click to browse or drag & drop documents</p>
            <p className="text-[10px] text-gray-500 mb-3">Supported: PDF, DOCX, TXT, CSV (Max 15MB)</p>
            <input
              type="file"
              accept=".pdf,.docx,.doc,.txt,.csv"
              onChange={(e) => setFile(e.target.files[0])}
              className="text-xs text-gray-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-500 cursor-pointer"
            />
            {file && <p className="text-xs text-emerald-400 font-medium mt-2">Selected: {file.name}</p>}
          </div>
        )}

        {tab === 'url' && (
          <div>
            <label className="block text-[11px] font-semibold text-gray-300 mb-1">Target Webpage URL</label>
            <input
              type="url"
              value={webUrl}
              onChange={(e) => setWebUrl(e.target.value)}
              placeholder="https://example.com/press-release"
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 font-mono"
            />
            <p className="text-[10px] text-gray-500 mt-1 flex items-center gap-1">
              <i data-lucide="shield" className="w-3 h-3 text-emerald-400"></i>
              <span>Protected against SSRF & internal network probing.</span>
            </p>
          </div>
        )}

        {/* Action Button & Processing Indicator */}
        <div className="pt-2 flex items-center justify-between">
          <p className="text-[11px] text-gray-400">
            Audit includes 15 governance dimensions & claim verification.
          </p>
          <button
            onClick={handleScan}
            disabled={scanning}
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-xs shadow-lg shadow-blue-500/25 transition flex items-center gap-2 disabled:opacity-50"
          >
            {scanning ? (
              <>
                <i data-lucide="loader-2" className="w-4 h-4 animate-spin"></i>
                <span>Analyzing Draft...</span>
              </>
            ) : (
              <>
                <i data-lucide="scan" className="w-4 h-4"></i>
                <span>{t('btn_run_scan')}</span>
              </>
            )}
          </button>
        </div>

        {scanning && (
          <div className="p-4 rounded-xl bg-blue-900/20 border border-blue-500/30 space-y-2 animate-pulse">
            <div className="flex items-center justify-between text-xs text-blue-300 font-medium">
              <span>{t(`scanning_state_${scanStep}`)}</span>
              <span>{scanStep * 25}%</span>
            </div>
            <div className="w-full h-1.5 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 via-indigo-500 to-cyan-400 transition-all duration-300"
                style={{ width: `${scanStep * 25}%` }}
              ></div>
            </div>
          </div>
        )}
      </div>

      {/* SCAN RESULTS PRESENTATION */}
      {scanResult && scanResult.analysis && (
        <div className="space-y-6">
          {/* Header Score Overview */}
          <div className="glass-card p-6 rounded-2xl border border-gray-800">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-gray-800">
              <div>
                <span className="text-[10px] font-mono uppercase tracking-widest text-blue-400">Audit Completed</span>
                <h2 className="text-xl font-extrabold text-white mt-0.5">{scanResult.title}</h2>
                <p className="text-xs text-gray-400 mt-1">
                  Status: <span className="font-semibold text-amber-400">{scanResult.status}</span> • Language: <span className="uppercase font-mono text-blue-400">{scanResult.language}</span>
                </p>
              </div>

              <div className="flex items-center gap-6">
                <div className="text-center">
                  <p className="text-[10px] uppercase text-gray-400 font-semibold mb-1">{t('overall_compliance')}</p>
                  <div className="text-3xl font-black bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
                    {scanResult.analysis.overall_score}%
                  </div>
                </div>

                <div className="text-center pl-6 border-l border-gray-800">
                  <p className="text-[10px] uppercase text-gray-400 font-semibold mb-1">{t('risk_level')}</p>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                    scanResult.analysis.risk_level === 'Low' ? 'badge-low' :
                    scanResult.analysis.risk_level === 'Moderate' ? 'badge-medium' :
                    scanResult.analysis.risk_level === 'High' ? 'badge-high' : 'badge-critical'
                  }`}>
                    {scanResult.analysis.risk_level} Risk
                  </span>
                </div>
              </div>
            </div>

            {/* Category Scores */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 pt-6">
              {[
                { label: t('dim_factual'), val: scanResult.analysis.factual_score, weight: "35% Weight" },
                { label: t('dim_terminology'), val: scanResult.analysis.terminology_score, weight: "25% Weight" },
                { label: t('dim_voice'), val: scanResult.analysis.voice_score, weight: "20% Weight" },
                { label: t('dim_accessibility'), val: scanResult.analysis.accessibility_score, weight: "10% Weight" },
                { label: t('dim_visual'), val: scanResult.analysis.visual_score, weight: "10% Weight" },
              ].map((cat, idx) => (
                <div key={idx} className="bg-gray-900/60 p-3 rounded-xl border border-gray-800">
                  <div className="flex justify-between items-center text-[10px] text-gray-400 mb-1">
                    <span className="font-semibold truncate">{cat.label}</span>
                    <span className="font-mono text-gray-500">{cat.weight}</span>
                  </div>
                  <p className="text-lg font-bold text-white">{cat.val}%</p>
                  <div className="w-full h-1 bg-gray-800 rounded-full mt-2 overflow-hidden">
                    <div
                      className={`h-full ${
                        cat.val >= 85 ? 'bg-emerald-400' :
                        cat.val >= 70 ? 'bg-amber-400' : 'bg-rose-500'
                      }`}
                      style={{ width: `${cat.val}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>

            {/* Deterministic Explanation Formula */}
            <div className="mt-4 p-3 rounded-xl bg-blue-950/30 border border-blue-900/40 text-[11px] text-blue-300 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <i data-lucide="info" className="w-4 h-4 text-blue-400 flex-shrink-0"></i>
                <span>Deterministic Scoring Engine: Bounded 0–100 weighted calculation. Zero arbitrary AI hallucinations.</span>
              </span>
              <span className="font-mono text-[10px] text-blue-400">Verified Rule Set v2.0</span>
            </div>
          </div>

          {/* Detected Violations List */}
          <div className="glass-card rounded-2xl border border-gray-800 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <i data-lucide="alert-octagon" className="w-4 h-4 text-rose-400"></i>
                <span>{t('issues_detected_header')} ({scanResult.analysis.issues.length})</span>
              </h3>
              <span className="text-xs text-gray-400">Human review required before publishing</span>
            </div>

            {scanResult.analysis.issues.length === 0 ? (
              <div className="text-center py-8 text-emerald-400 text-xs">
                <i data-lucide="check-circle-2" className="w-8 h-8 mx-auto mb-2"></i>
                <p className="font-bold">No guideline violations detected. Content perfectly aligned with brand standards.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {scanResult.analysis.issues.map((issue, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-gray-900/70 border border-gray-800 space-y-3 hover:border-gray-700 transition">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2.5">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                          issue.severity === 'Critical' ? 'badge-critical' :
                          issue.severity === 'High' ? 'badge-high' :
                          issue.severity === 'Medium' ? 'badge-medium' : 'badge-low'
                        }`}>
                          {issue.severity}
                        </span>
                        <span className="text-xs font-bold text-white">{issue.title}</span>
                      </div>
                      <span className="text-[10px] text-gray-500 font-mono">Dimension: {issue.dimension}</span>
                    </div>

                    {/* Problematic Sentence */}
                    <div className="p-2.5 rounded-lg bg-rose-950/20 border border-rose-900/30 text-rose-200 text-xs font-mono">
                      "{issue.sentence}"
                    </div>

                    {/* Explanation */}
                    <p className="text-xs text-gray-300 leading-relaxed">
                      <span className="font-semibold text-gray-200">Problem: </span>{issue.explanation}
                    </p>

                    {/* Evidence Source (Citations or Unverified) */}
                    <div className="p-2.5 rounded-lg bg-gray-950 border border-gray-800 text-[11px] space-y-1">
                      <div className="flex items-center gap-1.5 text-blue-400 font-semibold">
                        <i data-lucide="file-text" className="w-3.5 h-3.5"></i>
                        <span>{t('label_evidence')}</span>
                      </div>
                      <p className={`font-mono ${issue.evidence.includes('Unable to verify') ? 'text-amber-400 font-bold' : 'text-emerald-300'}`}>
                        {issue.evidence}
                      </p>
                      {issue.guideline_citation && (
                        <p className="text-gray-400 text-[10px] pt-1">
                          <span className="text-gray-500">{t('label_citation')} </span>{issue.guideline_citation}
                        </p>
                      )}
                    </div>

                    {/* Suggested Correction */}
                    {issue.suggested_correction && (
                      <div className="p-2.5 rounded-lg bg-emerald-950/20 border border-emerald-900/30 text-xs text-emerald-200 flex items-center justify-between">
                        <div>
                          <span className="font-semibold text-emerald-400">{t('label_suggested_fix')} </span>
                          <span>"{issue.suggested_correction}"</span>
                        </div>
                        <button
                          onClick={() => onNavigate('rewrite')}
                          className="px-3 py-1 rounded bg-blue-600 hover:bg-blue-500 text-white text-[10px] font-semibold transition flex items-center gap-1 flex-shrink-0 ml-4"
                        >
                          <i data-lucide="wand2" className="w-3 h-3"></i>
                          <span>Rewrite Studio</span>
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// ----------------- 4. BRAND INTELLIGENCE BRAIN PAGE -----------------
function BrainPage({ t, user }) {
  const [activeTab, setActiveTab] = useState('facts');
  const [facts, setFacts] = useState([]);
  const [terms, setTerms] = useState([]);
  const [guidelines, setGuidelines] = useState([]);
  const [assets, setAssets] = useState([]);
  const [clarityData, setClarityData] = useState(null);

  // New Fact Form
  const [newTopic, setNewTopic] = useState('');
  const [newFactText, setNewFactText] = useState('');
  const [newSource, setNewSource] = useState('');
  const [newDate, setNewDate] = useState('2026-11-14');

  // New Term Form
  const [newPref, setNewPref] = useState('');
  const [newProhib, setNewProhib] = useState('');
  const [newRationale, setNewRationale] = useState('');

  const loadBrainData = async () => {
    try {
      const [fR, tR, gR, aR, cR] = await Promise.all([
        fetch('/api/brand/facts'),
        fetch('/api/brand/terminology'),
        fetch('/api/brand/guidelines'),
        fetch('/api/brand/assets'),
        fetch('/api/clarity/analyze')
      ]);
      if (fR.ok) setFacts(await fR.json());
      if (tR.ok) setTerms(await tR.json());
      if (gR.ok) setGuidelines(await gR.json());
      if (aR.ok) setAssets(await aR.json());
      if (cR.ok) setClarityData(await cR.json());
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadBrainData();
  }, []);

  const handleAddFact = async (e) => {
    e.preventDefault();
    if (!newTopic || !newFactText || !newSource) return;
    const res = await fetch('/api/brand/facts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: newTopic,
        fact_text: newFactText,
        source_doc: newSource,
        verified_date: newDate,
        category: "Product"
      })
    });
    if (res.ok) {
      setNewTopic('');
      setNewFactText('');
      setNewSource('');
      loadBrainData();
    }
  };

  const handleDeleteFact = async (id) => {
    await fetch(`/api/brand/facts/${id}`, { method: 'DELETE' });
    loadBrainData();
  };

  const handleAddTerm = async (e) => {
    e.preventDefault();
    if (!newPref || !newProhib) return;
    const res = await fetch('/api/brand/terminology', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        preferred_term: newPref,
        prohibited_term: newProhib,
        rationale: newRationale,
        is_strict: true,
        language: "en"
      })
    });
    if (res.ok) {
      setNewPref('');
      setNewProhib('');
      setNewRationale('');
      loadBrainData();
    }
  };

  const handleDeleteTerm = async (id) => {
    await fetch(`/api/brand/terminology/${id}`, { method: 'DELETE' });
    loadBrainData();
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <i data-lucide="brain-circuit" className="w-5 h-5 text-blue-400"></i>
          <span>{t('brain_title')}</span>
        </h1>
        <p className="text-xs text-gray-400 mt-1">{t('brain_desc')}</p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-800 gap-6">
        {[
          { id: 'facts', label: t('tab_facts'), icon: 'check-square' },
          { id: 'terms', label: t('tab_terminology'), icon: 'book-open' },
          { id: 'assets', label: t('tab_assets'), icon: 'palette' },
          { id: 'clarity', label: t('tab_clarity'), icon: 'sparkles' },
        ].map((tb) => (
          <button
            key={tb.id}
            onClick={() => setActiveTab(tb.id)}
            className={`pb-3 text-xs font-semibold flex items-center gap-2 border-b-2 transition ${
              activeTab === tb.id ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-gray-200'
            }`}
          >
            <i data-lucide={tb.icon} className="w-4 h-4"></i>
            <span>{tb.label}</span>
          </button>
        ))}
      </div>

      {/* 1. Approved Facts Tab */}
      {activeTab === 'facts' && (
        <div className="space-y-6">
          {/* Add Fact Form */}
          {user.role === 'ADMIN' && (
            <form onSubmit={handleAddFact} className="glass-card p-5 rounded-2xl border border-gray-800 space-y-4">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <i data-lucide="plus" className="w-3.5 h-3.5 text-blue-400"></i>
                <span>Register New Approved Company Fact</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                <input
                  type="text"
                  placeholder="Topic (e.g. Product Warranty)"
                  value={newTopic}
                  onChange={(e) => setNewTopic(e.target.value)}
                  className="px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                />
                <input
                  type="text"
                  placeholder="Approved Fact Statement"
                  value={newFactText}
                  onChange={(e) => setNewFactText(e.target.value)}
                  className="px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 md:col-span-2"
                />
                <input
                  type="text"
                  placeholder="Source Document (e.g. Legal Charter)"
                  value={newSource}
                  onChange={(e) => setNewSource(e.target.value)}
                  className="px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div className="flex justify-end">
                <button type="submit" className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow transition">
                  {t('btn_add_fact')}
                </button>
              </div>
            </form>
          )}

          {/* Facts Table */}
          <div className="glass-card rounded-2xl border border-gray-800 overflow-hidden">
            <table className="w-full text-left text-xs">
              <thead className="bg-gray-900/70 text-gray-400 uppercase text-[10px] font-semibold border-b border-gray-800">
                <tr>
                  <th className="py-3 px-4">Topic</th>
                  <th className="py-3 px-4">Approved Fact Specification</th>
                  <th className="py-3 px-4">Source Document</th>
                  <th className="py-3 px-4">Verified Date</th>
                  {user.role === 'ADMIN' && <th className="py-3 px-4 text-right">Action</th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {facts.map((f) => (
                  <tr key={f.id} className="hover:bg-gray-800/30 transition">
                    <td className="py-3 px-4 font-bold text-white whitespace-nowrap">{f.topic}</td>
                    <td className="py-3 px-4 text-emerald-300 font-mono text-[11px]">{f.fact_text}</td>
                    <td className="py-3 px-4 text-gray-300 text-xs">{f.source_doc}</td>
                    <td className="py-3 px-4 text-gray-400 font-mono text-[11px]">{f.verified_date}</td>
                    {user.role === 'ADMIN' && (
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => handleDeleteFact(f.id)}
                          className="text-rose-400 hover:text-rose-300 transition"
                        >
                          <i data-lucide="trash-2" className="w-4 h-4"></i>
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 2. Terminology Rules Tab */}
      {activeTab === 'terms' && (
        <div className="space-y-6">
          {user.role === 'ADMIN' && (
            <form onSubmit={handleAddTerm} className="glass-card p-5 rounded-2xl border border-gray-800 space-y-4">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <i data-lucide="plus" className="w-3.5 h-3.5 text-blue-400"></i>
                <span>Add Prohibited vs Preferred Terminology Rule</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <input
                  type="text"
                  placeholder="Prohibited Term (e.g. cheap)"
                  value={newProhib}
                  onChange={(e) => setNewProhib(e.target.value)}
                  className="px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                />
                <input
                  type="text"
                  placeholder="Preferred Term (e.g. cost-effective)"
                  value={newPref}
                  onChange={(e) => setNewPref(e.target.value)}
                  className="px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                />
                <input
                  type="text"
                  placeholder="Rationale & Context"
                  value={newRationale}
                  onChange={(e) => setNewRationale(e.target.value)}
                  className="px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div className="flex justify-end">
                <button type="submit" className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow transition">
                  {t('btn_add_term')}
                </button>
              </div>
            </form>
          )}

          <div className="glass-card rounded-2xl border border-gray-800 overflow-hidden">
            <table className="w-full text-left text-xs">
              <thead className="bg-gray-900/70 text-gray-400 uppercase text-[10px] font-semibold border-b border-gray-800">
                <tr>
                  <th className="py-3 px-4">Prohibited Term</th>
                  <th className="py-3 px-4">Official Preferred Term</th>
                  <th className="py-3 px-4">Language</th>
                  <th className="py-3 px-4">Rationale</th>
                  {user.role === 'ADMIN' && <th className="py-3 px-4 text-right">Action</th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {terms.map((t) => (
                  <tr key={t.id} className="hover:bg-gray-800/30 transition">
                    <td className="py-3 px-4 text-rose-400 font-mono line-through font-semibold">{t.prohibited_term}</td>
                    <td className="py-3 px-4 text-emerald-400 font-mono font-bold">{t.preferred_term}</td>
                    <td className="py-3 px-4 uppercase font-mono text-[10px] text-gray-400">{t.language}</td>
                    <td className="py-3 px-4 text-gray-300">{t.rationale || 'Brand standard requirement'}</td>
                    {user.role === 'ADMIN' && (
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => handleDeleteTerm(t.id)}
                          className="text-rose-400 hover:text-rose-300 transition"
                        >
                          <i data-lucide="trash-2" className="w-4 h-4"></i>
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 3. Visual Assets Tab */}
      {activeTab === 'assets' && (
        <div className="space-y-6">
          <div className="glass-card p-6 rounded-2xl border border-gray-800 space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <i data-lucide="palette" className="w-4 h-4 text-blue-400"></i>
              <span>Registered Brand Color Palettes</span>
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {assets.filter(a => a.asset_type === 'COLOR_PALETTE').map((c) => (
                <div key={c.id} className="p-4 rounded-xl bg-gray-900 border border-gray-800 space-y-2">
                  <div
                    className="w-full h-16 rounded-lg shadow-inner border border-white/10"
                    style={{ backgroundColor: c.color_hex }}
                  ></div>
                  <p className="text-xs font-bold text-white">{c.name}</p>
                  <p className="text-[11px] font-mono text-gray-400">{c.color_hex}</p>
                  <p className="text-[10px] text-gray-500">{c.meta_info?.role || 'Brand Accent'}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="glass-card p-6 rounded-2xl border border-gray-800 space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <i data-lucide="image" className="w-4 h-4 text-indigo-400"></i>
              <span>Brand Logo & Clearance Standards</span>
            </h3>
            <div className="flex items-center gap-6 p-4 rounded-xl bg-gray-900/60 border border-gray-800">
              <img src="/static/logo.png" alt="Nexura Logo" className="w-20 h-20 rounded-xl bg-gray-950 p-2 border border-gray-700 shadow-md" />
              <div className="space-y-1">
                <p className="text-sm font-bold text-white">Nexura Primary Vector Mark</p>
                <p className="text-xs text-gray-300">Format: Lossless PNG / SVG • Aspect Ratio: 1:1</p>
                <p className="text-xs text-blue-400">Placement Rule: Position in top-left or top-right quadrant with minimum 24px exclusion zone.</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 4. Guideline Clarity Analyzer Tab */}
      {activeTab === 'clarity' && (
        <div className="space-y-6">
          <div className="p-4 rounded-2xl bg-amber-950/20 border border-amber-900/40 text-amber-200 text-xs flex items-center gap-3">
            <i data-lucide="alert-triangle" className="w-5 h-5 text-amber-400 flex-shrink-0"></i>
            <div>
              <p className="font-bold text-sm text-amber-300">{t('clarity_alert_title')}</p>
              <p className="text-[11px] text-amber-200/80 mt-0.5">
                Analyzes existing guidelines for contradictory rules, ambiguous criteria, and missing specifications before they impact creators.
              </p>
            </div>
          </div>

          {clarityData && (
            <div className="space-y-4">
              {clarityData.conflicts.map((conf, idx) => (
                <div key={idx} className="glass-card p-5 rounded-2xl border border-gray-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider badge-high">
                      {conf.type}
                    </span>
                    <span className="text-xs text-gray-400 font-mono">Severity: {conf.severity}</span>
                  </div>

                  <div className="space-y-1">
                    <p className="text-xs font-semibold text-white">Conflicting Rule A: <span className="text-blue-300 font-mono">{conf.guideline_a}</span></p>
                    {conf.guideline_b && (
                      <p className="text-xs font-semibold text-white">Conflicting Rule B: <span className="text-indigo-300 font-mono">{conf.guideline_b}</span></p>
                    )}
                  </div>

                  <p className="text-xs text-gray-300 leading-relaxed">
                    <span className="font-semibold text-gray-200">Analysis: </span>{conf.explanation}
                  </p>

                  <div className="p-3 rounded-xl bg-blue-950/30 border border-blue-900/40 text-xs text-blue-200 flex items-start gap-2">
                    <i data-lucide="lightbulb" className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5"></i>
                    <div>
                      <span className="font-bold text-blue-400">Admin Action Recommended: </span>
                      <span>{conf.recommendation}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ----------------- 5. VISUAL BRAND GUARDIAN PAGE -----------------
function VisualPage({ t, user }) {
  const [imageFile, setImageFile] = useState(null);
  const [altText, setAltText] = useState('');
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState('/static/sample_creative_violation.png');

  const runVisualAudit = async (filePath, customAlt) => {
    setLoading(true);
    try {
      // Fetch sample image as blob to send to API
      const imgBlob = await fetch(filePath).then(r => r.blob());
      const formData = new FormData();
      formData.append('file', imgBlob, 'creative.png');
      if (customAlt) formData.append('alt_text', customAlt);

      const res = await fetch('/api/visual/audit-image', { method: 'POST', body: formData });
      if (res.ok) {
        const data = await res.json();
        setReport(data);
        setPreviewUrl(filePath);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial run on sample creative with violations
    runVisualAudit('/static/sample_creative_violation.png', '');
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <i data-lucide="eye" className="w-5 h-5 text-blue-400"></i>
            <span>{t('visual_title')}</span>
          </h1>
          <p className="text-xs text-gray-400 mt-1">{t('visual_desc')}</p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => runVisualAudit('/static/sample_creative_violation.png', '')}
            className="px-3 py-1.5 rounded-lg bg-rose-950/40 hover:bg-rose-950/60 text-rose-300 border border-rose-800/40 text-xs font-medium transition"
          >
            {t('btn_test_violation')}
          </button>
          <button
            onClick={() => runVisualAudit('/static/sample_creative_compliant.png', 'Nexura enterprise cloud launch banner with brand logo')}
            className="px-3 py-1.5 rounded-lg bg-emerald-950/40 hover:bg-emerald-950/60 text-emerald-300 border border-emerald-800/40 text-xs font-medium transition"
          >
            {t('btn_test_compliant')}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Left: Interactive Image Canvas with Bounding Box Highlights */}
        <div className="md:col-span-5 glass-card p-5 rounded-2xl border border-gray-800 flex flex-col items-center">
          <div className="relative max-w-full rounded-xl overflow-hidden border border-gray-700 bg-gray-950 shadow-2xl">
            <img src={previewUrl} alt="Analyzed Creative" className="w-full max-h-[460px] object-contain" />
            
            {/* Render Visual Bounding Boxes if issues present */}
            {report && report.issues && report.issues.map((iss, i) => {
              if (!iss.visual_bbox) return null;
              const [ymin, xmin, ymax, xmax] = iss.visual_bbox;
              return (
                <div
                  key={i}
                  className="absolute border-2 border-rose-500 bg-rose-500/20 pointer-events-none transition-all duration-300"
                  style={{
                    top: `${ymin}%`,
                    left: `${xmin}%`,
                    width: `${xmax - xmin}%`,
                    height: `${ymax - ymin}%`
                  }}
                >
                  <span className="absolute -top-5 left-0 px-1.5 py-0.5 rounded text-[9px] bg-rose-600 text-white font-mono font-bold whitespace-nowrap">
                    {iss.title}
                  </span>
                </div>
              );
            })}
          </div>
          <p className="text-[11px] text-gray-500 mt-3 text-center">
            Interactive overlay highlights detected off-brand colors, logo positioning, and low-contrast regions.
          </p>
        </div>

        {/* Right: Computer Vision Telemetry & Findings */}
        <div className="md:col-span-7 space-y-4">
          {report && (
            <>
              {/* Score Meter & Quick Stats */}
              <div className="glass-card p-5 rounded-2xl border border-gray-800 grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-[10px] uppercase font-semibold text-gray-400 mb-1">{t('visual_score')}</p>
                  <p className="text-2xl font-black text-white">{report.visual_compliance_score}%</p>
                </div>
                <div className="border-x border-gray-800">
                  <p className="text-[10px] uppercase font-semibold text-gray-400 mb-1">{t('dimensions_aspect')}</p>
                  <p className="text-sm font-bold text-blue-400 font-mono">{report.dimensions} ({report.aspect_ratio}:1)</p>
                </div>
                <div>
                  <p className="text-[10px] uppercase font-semibold text-gray-400 mb-1">{t('contrast_ratio')}</p>
                  <p className={`text-sm font-bold font-mono ${report.contrast_ratio >= 4.5 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {report.contrast_ratio}:1 {report.contrast_ratio >= 4.5 ? '✓ (WCAG AA)' : '✗ (Fail)'}
                  </p>
                </div>
              </div>

              {/* Dominant Color Palette */}
              <div className="glass-card p-5 rounded-2xl border border-gray-800 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                    <i data-lucide="palette" className="w-3.5 h-3.5 text-blue-400"></i>
                    <span>Extracted Dominant Color Palette</span>
                  </h3>
                  <span className="text-[11px] text-gray-400">Evaluated vs Registered Palette</span>
                </div>
                <div className="grid grid-cols-5 gap-3">
                  {report.dominant_colors.map((c, i) => (
                    <div key={i} className="text-center space-y-1.5 p-2 bg-gray-900 rounded-xl border border-gray-800">
                      <div className="w-full h-12 rounded-lg shadow-inner border border-white/10" style={{ backgroundColor: c.hex }}></div>
                      <p className="text-[10px] font-mono text-gray-300 font-bold">{c.hex}</p>
                      <span className={`inline-block px-1.5 py-0.5 rounded text-[8px] font-bold ${
                        c.is_brand_color ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'
                      }`}>
                        {c.is_brand_color ? 'Brand Match' : 'Off-Brand'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Detected Visual Issues List */}
              <div className="glass-card p-5 rounded-2xl border border-gray-800 space-y-3">
                <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                  <i data-lucide="alert-triangle" className="w-3.5 h-3.5 text-amber-400"></i>
                  <span>Visual Audit Findings ({report.issues.length})</span>
                </h3>

                {report.issues.length === 0 ? (
                  <p className="text-xs text-emerald-400 font-medium py-3 text-center">
                    All visual dimensions conform to enterprise brand guidelines.
                  </p>
                ) : (
                  <div className="space-y-3">
                    {report.issues.map((iss, i) => (
                      <div key={i} className="p-3.5 rounded-xl bg-gray-900/60 border border-gray-800 space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-white">{iss.title}</span>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                            iss.severity === 'Critical' ? 'badge-critical' : 'badge-high'
                          }`}>
                            {iss.severity}
                          </span>
                        </div>
                        <p className="text-xs text-gray-300">{iss.explanation}</p>
                        <div className="text-[11px] text-emerald-300 bg-emerald-950/20 p-2 rounded-lg border border-emerald-900/30">
                          <span className="font-semibold text-emerald-400">Fix: </span>{iss.suggested_correction}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// ----------------- 6. AI SMART REWRITE STUDIO -----------------
function RewritePage({ t, user }) {
  const [sentence, setSentence] = useState("Product X offers a lifetime warranty with zero downtime forever!");
  const [dimension, setDimension] = useState("Fact");
  const [options, setOptions] = useState([]);
  const [selectedOption, setSelectedOption] = useState(null);
  const [loading, setLoading] = useState(false);
  const [appliedMsg, setAppliedMsg] = useState('');

  const handleGenerate = async () => {
    setLoading(true);
    setAppliedMsg('');
    try {
      const res = await fetch('/api/rewrite/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sentence, dimension })
      });
      if (res.ok) {
        const data = await res.json();
        setOptions(data.options);
        setSelectedOption(data.options[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleGenerate();
  }, []);

  const handleApply = async () => {
    if (!selectedOption) return;
    setAppliedMsg(`Successfully accepted & updated copy: "${selectedOption.rewritten_text}"`);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <i data-lucide="wand2" className="w-5 h-5 text-blue-400"></i>
          <span>{t('rewrite_title')}</span>
        </h1>
        <p className="text-xs text-gray-400 mt-1">{t('rewrite_desc')}</p>
      </div>

      {appliedMsg && (
        <div className="p-3 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
          <i data-lucide="check-circle" className="w-4 h-4"></i>
          <span>{appliedMsg}</span>
        </div>
      )}

      {/* Target Problematic Text Input */}
      <div className="glass-card p-5 rounded-2xl border border-gray-800 space-y-3">
        <label className="block text-xs font-semibold text-gray-300">Target Non-Compliant Sentence to Rephrase</label>
        <div className="flex gap-3">
          <input
            type="text"
            value={sentence}
            onChange={(e) => setSentence(e.target.value)}
            className="flex-1 px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-xs text-white focus:outline-none focus:border-blue-500 font-mono"
          />
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold shadow transition flex items-center gap-2"
          >
            {loading ? <i data-lucide="loader-2" className="w-4 h-4 animate-spin"></i> : <i data-lucide="sparkles" className="w-4 h-4"></i>}
            <span>Generate Rewrites</span>
          </button>
        </div>
      </div>

      {/* 3 Rewrite Variations Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {options.map((opt, idx) => {
          const isSelected = selectedOption?.option_type === opt.option_type;
          return (
            <div
              key={idx}
              onClick={() => setSelectedOption(opt)}
              className={`glass-card p-5 rounded-2xl border cursor-pointer transition-all duration-200 flex flex-col justify-between ${
                isSelected ? 'border-blue-500 ring-2 ring-blue-500/30 bg-blue-950/20' : 'border-gray-800 hover:border-gray-700'
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-blue-500/20 text-blue-300 border border-blue-500/30">
                    {opt.option_type} Mode
                  </span>
                  {isSelected && <i data-lucide="check-circle-2" className="w-4 h-4 text-blue-400"></i>}
                </div>

                <p className="text-xs text-white font-mono p-3 bg-gray-900/90 rounded-xl border border-gray-800 leading-relaxed">
                  "{opt.rewritten_text}"
                </p>

                <p className="text-[11px] text-gray-400 leading-relaxed">
                  <span className="font-semibold text-gray-300">Stylistic Rationale: </span>{opt.rationale}
                </p>
              </div>

              <div className="pt-4 mt-4 border-t border-gray-800/60">
                <button
                  type="button"
                  className={`w-full py-2 rounded-lg text-xs font-semibold transition ${
                    isSelected ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  {isSelected ? 'Selected Variation' : 'Select Option'}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Side-by-Side Diff Comparison */}
      {selectedOption && (
        <div className="glass-card p-6 rounded-2xl border border-gray-800 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <i data-lucide="columns-2" className="w-4 h-4 text-blue-400"></i>
            <span>Side-by-Side Before & After Alignment</span>
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-900/30 space-y-1.5">
              <span className="text-[10px] font-bold uppercase tracking-wider text-rose-400">{t('original_text')}</span>
              <p className="text-xs text-rose-200 font-mono leading-relaxed">"{sentence}"</p>
            </div>
            <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-900/30 space-y-1.5">
              <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400">{t('corrected_preview')}</span>
              <p className="text-xs text-emerald-200 font-mono leading-relaxed">"{selectedOption.rewritten_text}"</p>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              onClick={handleApply}
              className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow transition flex items-center gap-2"
            >
              <i data-lucide="check" className="w-4 h-4"></i>
              <span>{t('btn_accept_apply')}</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// ----------------- 7. HUMAN REVIEW AND APPROVAL WORKSPACE -----------------
function ReviewPage({ t, user }) {
  const [submissions, setSubmissions] = useState([]);
  const [selectedSub, setSelectedSub] = useState(null);
  const [filter, setFilter] = useState('ALL');
  const [newComment, setNewComment] = useState('');
  const [actionNotes, setActionNotes] = useState('');

  const loadSubmissions = async () => {
    try {
      const res = await fetch('/api/scanner/submissions');
      if (res.ok) {
        const data = await res.json();
        setSubmissions(data);
        if (data.length > 0 && !selectedSub) {
          loadSubDetail(data[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const loadSubDetail = async (id) => {
    try {
      const res = await fetch(`/api/scanner/submissions/${id}`);
      if (res.ok) {
        setSelectedSub(await res.json());
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadSubmissions();
  }, []);

  const handleWorkflowAction = async (action) => {
    if (!selectedSub) return;
    try {
      const res = await fetch(`/api/review/action/${selectedSub.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, notes: actionNotes })
      });
      if (res.ok) {
        setActionNotes('');
        await loadSubDetail(selectedSub.id);
        await loadSubmissions();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handlePostComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim() || !selectedSub) return;
    try {
      const res = await fetch(`/api/review/comment/${selectedSub.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: newComment })
      });
      if (res.ok) {
        setNewComment('');
        await loadSubDetail(selectedSub.id);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const filtered = filter === 'ALL' ? submissions : submissions.filter(s => s.status === filter);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <i data-lucide="clipboard-check" className="w-5 h-5 text-blue-400"></i>
          <span>{t('review_title')}</span>
        </h1>
        <p className="text-xs text-gray-400 mt-1">{t('review_desc')}</p>
      </div>

      {/* Filter Tabs */}
      <div className="flex border-b border-gray-800 gap-3 overflow-x-auto pb-2">
        {['ALL', 'Review Required', 'Revision Requested', 'Resubmitted', 'Approved', 'Rejected'].map((st) => (
          <button
            key={st}
            onClick={() => setFilter(st)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition ${
              filter === st ? 'bg-blue-600 text-white font-bold' : 'text-gray-400 hover:text-gray-200 bg-gray-900/60'
            }`}
          >
            {st}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Left Submissions Column */}
        <div className="md:col-span-4 space-y-3">
          {filtered.map((s) => (
            <div
              key={s.id}
              onClick={() => loadSubDetail(s.id)}
              className={`p-4 rounded-xl border cursor-pointer transition ${
                selectedSub?.id === s.id
                  ? 'bg-blue-950/30 border-blue-500 shadow-lg shadow-blue-500/10'
                  : 'glass-card border-gray-800 hover:border-gray-700'
              }`}
            >
              <div className="flex justify-between items-start mb-1">
                <span className="text-xs font-bold text-white truncate max-w-[180px]">{s.title}</span>
                <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold ${
                  s.status === 'Approved' ? 'badge-low' :
                  s.status === 'Revision Requested' ? 'badge-high' :
                  s.status === 'Rejected' ? 'badge-critical' : 'badge-medium'
                }`}>
                  {s.status}
                </span>
              </div>
              <p className="text-[11px] text-gray-400">{s.department} • {s.creator_name}</p>
              <div className="flex items-center justify-between text-[10px] text-gray-500 mt-2 font-mono">
                <span>Score: {s.overall_score}%</span>
                <span>{s.issue_count} Issues</span>
              </div>
            </div>
          ))}
        </div>

        {/* Right Detail Pane */}
        <div className="md:col-span-8 space-y-6">
          {selectedSub && (
            <div className="glass-card p-6 rounded-2xl border border-gray-800 space-y-6">
              {/* Header Info */}
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-gray-800">
                <div>
                  <h2 className="text-lg font-extrabold text-white">{selectedSub.title}</h2>
                  <p className="text-xs text-gray-400 mt-0.5">
                    Creator: <span className="text-white font-medium">{selectedSub.creator_name}</span> ({selectedSub.department})
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30">
                    Compliance Score: {selectedSub.analysis.overall_score}%
                  </span>
                </div>
              </div>

              {/* Side-by-Side Content Display */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">Original Submitted Text</label>
                  <div className="p-3 bg-gray-900 rounded-xl border border-gray-800 text-xs text-gray-300 font-mono leading-relaxed max-h-48 overflow-y-auto">
                    {selectedSub.raw_text}
                  </div>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">Corrected / Revised Version</label>
                  <div className="p-3 bg-gray-900 rounded-xl border border-emerald-900/40 text-xs text-emerald-200 font-mono leading-relaxed max-h-48 overflow-y-auto">
                    {selectedSub.corrected_text || selectedSub.raw_text}
                  </div>
                </div>
              </div>

              {/* Workflow Actions with RBAC */}
              <div className="p-4 rounded-xl bg-gray-900/80 border border-gray-800 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                    <i data-lucide="shield-check" className="w-4 h-4 text-blue-400"></i>
                    <span>Governance Decision Actions</span>
                  </span>
                  <span className="text-[10px] text-gray-400">Current Role: <span className="font-mono text-blue-400">{user.role}</span></span>
                </div>

                <input
                  type="text"
                  placeholder="Optional decision notes / feedback..."
                  value={actionNotes}
                  onChange={(e) => setActionNotes(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-950 border border-gray-700 rounded-lg text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                />

                <div className="flex flex-wrap items-center gap-3 pt-1">
                  {(user.role === 'ADMIN' || user.role === 'REVIEWER') && (
                    <>
                      <button
                        onClick={() => handleWorkflowAction('APPROVE')}
                        className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold shadow transition flex items-center gap-1.5"
                      >
                        <i data-lucide="check" className="w-3.5 h-3.5"></i>
                        <span>{t('btn_approve')}</span>
                      </button>
                      <button
                        onClick={() => handleWorkflowAction('REQUEST_REVISION')}
                        className="px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-xs font-bold shadow transition flex items-center gap-1.5"
                      >
                        <i data-lucide="rotate-ccw" className="w-3.5 h-3.5"></i>
                        <span>{t('btn_request_revision')}</span>
                      </button>
                      <button
                        onClick={() => handleWorkflowAction('REJECT')}
                        className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-bold shadow transition flex items-center gap-1.5"
                      >
                        <i data-lucide="x" className="w-3.5 h-3.5"></i>
                        <span>{t('btn_reject')}</span>
                      </button>
                    </>
                  )}

                  {(user.role === 'ADMIN' || user.role === 'CREATOR') && (
                    <button
                      onClick={() => handleWorkflowAction('RESUBMIT')}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-bold shadow transition flex items-center gap-1.5"
                    >
                      <i data-lucide="send" className="w-3.5 h-3.5"></i>
                      <span>{t('btn_resubmit')}</span>
                    </button>
                  )}
                </div>
              </div>

              {/* Discussion & Audit Log Tabs */}
              <div className="space-y-4">
                <h4 className="text-xs font-bold text-white uppercase tracking-wider">{t('tab_comments')}</h4>
                
                {/* Comments Thread */}
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {selectedSub.comments.length === 0 ? (
                    <p className="text-xs text-gray-500 italic">No feedback comments recorded yet.</p>
                  ) : (
                    selectedSub.comments.map((c, i) => (
                      <div key={i} className="p-3 rounded-lg bg-gray-900 border border-gray-800 text-xs space-y-1">
                        <div className="flex items-center justify-between text-[10px] text-gray-400">
                          <span className="font-semibold text-blue-300">{c.user_name} ({c.user_role})</span>
                          <span>{new Date(c.created_at).toLocaleTimeString()}</span>
                        </div>
                        <p className="text-gray-200">{c.content}</p>
                      </div>
                    ))
                  )}
                </div>

                {/* Comment Input */}
                <form onSubmit={handlePostComment} className="flex gap-2">
                  <input
                    type="text"
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    placeholder="Add team feedback note..."
                    className="flex-1 px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  />
                  <button type="submit" className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white text-xs font-semibold rounded-lg transition">
                    {t('btn_send_comment')}
                  </button>
                </form>

                {/* Audit Trail */}
                <div className="pt-4 border-t border-gray-800">
                  <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-2">{t('tab_history')}</h4>
                  <div className="space-y-1.5">
                    {selectedSub.history.map((h, i) => (
                      <div key={i} className="text-[11px] text-gray-400 flex items-center justify-between p-2 rounded bg-gray-950/50">
                        <span>
                          <strong className="text-gray-200">{h.reviewer_name}</strong> transitioned status: <span className="text-amber-400 font-mono">{h.previous_status || 'Draft'} → {h.new_status}</span>
                        </span>
                        <span className="font-mono text-[10px] text-gray-500">{new Date(h.created_at).toLocaleDateString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ----------------- 8. GOVERNANCE ANALYTICS PAGE -----------------
function AnalyticsPage({ t, user }) {
  const [analytics, setAnalytics] = useState(null);
  const [memory, setMemory] = useState([]);
  const [deptFilter, setDeptFilter] = useState('');

  const chartRefs = {
    pie: useRef(null),
    doughnut: useRef(null),
    bar: useRef(null),
    line: useRef(null),
    hBar: useRef(null)
  };
  const chartInstances = useRef({});

  const loadAnalytics = async () => {
    try {
      const q = deptFilter ? `?department=${deptFilter}` : '';
      const [aR, mR] = await Promise.all([
        fetch(`/api/analytics/overview${q}`),
        fetch('/api/memory/recurring')
      ]);
      if (aR.ok) setAnalytics(await aR.json());
      if (mR.ok) {
        const mem = await mR.json();
        setMemory(mem.recurring_errors || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, [deptFilter]);

  // Render Chart.js charts
  useEffect(() => {
    if (!analytics || !window.Chart) return;

    // Destroy prior instances
    Object.values(chartInstances.current).forEach(c => c && c.destroy());

    // 1. Status Pie Chart
    if (chartRefs.pie.current) {
      const ctx = chartRefs.pie.current.getContext('2d');
      chartInstances.current.pie = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: Object.keys(analytics.status_distribution),
          datasets: [{
            data: Object.values(analytics.status_distribution),
            backgroundColor: ['#10B981', '#3B82F6', '#F59E0B', '#F43F5E', '#8B5CF6']
          }]
        },
        options: { responsive: true, plugins: { legend: { position: 'bottom', labels: { color: '#9CA3AF', font: { size: 10 } } } } }
      });
    }

    // 2. Severity Doughnut Chart
    if (chartRefs.doughnut.current) {
      const ctx = chartRefs.doughnut.current.getContext('2d');
      chartInstances.current.doughnut = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: Object.keys(analytics.severity_distribution),
          datasets: [{
            data: Object.values(analytics.severity_distribution),
            backgroundColor: ['#F43F5E', '#FB923C', '#FACC15', '#34D399']
          }]
        },
        options: { responsive: true, plugins: { legend: { position: 'bottom', labels: { color: '#9CA3AF', font: { size: 10 } } } } }
      });
    }

    // 3. Category Violations Bar Chart
    if (chartRefs.bar.current) {
      const ctx = chartRefs.bar.current.getContext('2d');
      chartInstances.current.bar = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: Object.keys(analytics.category_violations),
          datasets: [{
            label: 'Violations',
            data: Object.values(analytics.category_violations),
            backgroundColor: '#6366F1'
          }]
        },
        options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { ticks: { color: '#9CA3AF' } }, x: { ticks: { color: '#9CA3AF' } } } }
      });
    }

    // 4. Compliance Trends Line Chart
    if (chartRefs.line.current) {
      const ctx = chartRefs.line.current.getContext('2d');
      chartInstances.current.line = new Chart(ctx, {
        type: 'line',
        data: {
          labels: analytics.monthly_trends.map(m => m.month),
          datasets: [{
            label: 'Avg Score %',
            data: analytics.monthly_trends.map(m => m.avg_score),
            borderColor: '#06B6D4',
            backgroundColor: 'rgba(6, 182, 212, 0.1)',
            fill: true,
            tension: 0.3
          }]
        },
        options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { min: 0, max: 100, ticks: { color: '#9CA3AF' } }, x: { ticks: { color: '#9CA3AF' } } } }
      });
    }

    // 5. Top Violations Horizontal Bar
    if (chartRefs.hBar.current) {
      const ctx = chartRefs.hBar.current.getContext('2d');
      chartInstances.current.hBar = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: analytics.top_violations.map(v => v.title.substring(0, 24) + '...'),
          datasets: [{
            label: 'Occurrences',
            data: analytics.top_violations.map(v => v.count),
            backgroundColor: '#F43F5E'
          }]
        },
        options: { indexAxis: 'y', responsive: true, plugins: { legend: { display: false } }, scales: { y: { ticks: { color: '#9CA3AF' } }, x: { ticks: { color: '#9CA3AF' } } } }
      });
    }

    return () => {
      Object.values(chartInstances.current).forEach(c => c && c.destroy());
    };
  }, [analytics]);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <i data-lucide="bar-chart-3" className="w-5 h-5 text-blue-400"></i>
            <span>{t('analytics_title')}</span>
          </h1>
          <p className="text-xs text-gray-400 mt-1">{t('analytics_desc')}</p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={deptFilter}
            onChange={(e) => setDeptFilter(e.target.value)}
            className="px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
          >
            <option value="">All Departments</option>
            <option value="Marketing">Marketing</option>
            <option value="Product">Product</option>
            <option value="Public Relations">Public Relations</option>
            <option value="Social Media">Social Media</option>
          </select>

          <a
            href="/api/analytics/export-csv"
            download
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold shadow transition flex items-center gap-1.5"
          >
            <i data-lucide="download" className="w-3.5 h-3.5"></i>
            <span>{t('btn_download_csv')}</span>
          </a>
        </div>
      </div>

      {/* 5 Real Charts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-card p-5 rounded-2xl border border-gray-800 space-y-2">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">{t('chart_status')}</h3>
          <canvas ref={chartRefs.pie} height="200"></canvas>
        </div>
        <div className="glass-card p-5 rounded-2xl border border-gray-800 space-y-2">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">{t('chart_severity')}</h3>
          <canvas ref={chartRefs.doughnut} height="200"></canvas>
        </div>
        <div className="glass-card p-5 rounded-2xl border border-gray-800 space-y-2">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">{t('chart_categories')}</h3>
          <canvas ref={chartRefs.bar} height="200"></canvas>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-card p-5 rounded-2xl border border-gray-800 space-y-2">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">{t('chart_trends')}</h3>
          <canvas ref={chartRefs.line} height="180"></canvas>
        </div>
        <div className="glass-card p-5 rounded-2xl border border-gray-800 space-y-2">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">{t('chart_top_violations')}</h3>
          <canvas ref={chartRefs.hBar} height="180"></canvas>
        </div>
      </div>

      {/* Brand Memory & Recurring Error Detection */}
      <div className="glass-card p-6 rounded-2xl border border-gray-800 space-y-4">
        <div className="flex items-center gap-2">
          <i data-lucide="history" className="w-5 h-5 text-indigo-400"></i>
          <div>
            <h3 className="text-sm font-bold text-white">{t('brand_memory_title')}</h3>
            <p className="text-xs text-gray-400">{t('brand_memory_desc')}</p>
          </div>
        </div>

        <div className="space-y-3 pt-2">
          {memory.map((rec, i) => (
            <div key={i} className="p-4 rounded-xl bg-gray-900/60 border border-gray-800 flex flex-col md:flex-row md:items-center justify-between gap-3">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-rose-500/20 text-rose-300 border border-rose-500/30">
                    Recurring {rec.frequency}x
                  </span>
                  <span className="text-xs font-bold text-white">{rec.violation_title}</span>
                </div>
                <p className="text-xs text-gray-300">
                  <span className="text-gray-400">Departments: </span>{rec.affected_departments.join(', ')}
                </p>
                <p className="text-xs text-emerald-300">
                  <span className="font-semibold text-emerald-400">Recommendation: </span>{rec.suggested_action}
                </p>
              </div>
              <span className="text-[10px] text-gray-500 font-mono self-start md:self-center">Category: {rec.dimension}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ----------------- 9. SETTINGS & DISCLOSURE PAGE -----------------
function SettingsPage({ t, user }) {
  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <i data-lucide="settings" className="w-5 h-5 text-blue-400"></i>
          <span>{t('nav_settings')}</span>
        </h1>
        <p className="text-xs text-gray-400 mt-1">Platform configuration, model disclosures, and compliance settings.</p>
      </div>

      <div className="glass-card p-6 rounded-2xl border border-gray-800 space-y-4">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <i data-lucide="shield" className="w-4 h-4 text-emerald-400"></i>
          <span>Responsible AI & Fallback Architecture</span>
        </h3>
        <p className="text-xs text-gray-300 leading-relaxed">
          BrandGuard AI utilizes a deterministic, zero-hallucination local engine for fact verification, terminology checking, readability scoring, and color distance calculation. In offline or private environments, local algorithms ensure 100% functionality without leaking corporate confidential material to public third-party endpoints.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <div className="p-3 rounded-xl bg-gray-900 border border-gray-800 space-y-1">
            <span className="text-[10px] text-gray-400 font-semibold uppercase">Active Engine</span>
            <p className="text-xs font-mono font-bold text-emerald-400">Deterministic Rule + NLP Engine (Online)</p>
          </div>
          <div className="p-3 rounded-xl bg-gray-900 border border-gray-800 space-y-1">
            <span className="text-[10px] text-gray-400 font-semibold uppercase">Data Isolation</span>
            <p className="text-xs font-mono font-bold text-blue-400">Tenant-Level SQLite/PostgreSQL Isolation</p>
          </div>
        </div>
      </div>

      <div className="glass-card p-6 rounded-2xl border border-gray-800 space-y-4">
        <h3 className="text-sm font-bold text-white">Organization Profile</h3>
        <div className="grid grid-cols-2 gap-4 text-xs">
          <div>
            <span className="text-gray-400 block mb-1">Company Name</span>
            <p className="font-bold text-white">Nexura Technologies Inc.</p>
          </div>
          <div>
            <span className="text-gray-400 block mb-1">Industry</span>
            <p className="font-bold text-white">Enterprise Cloud Software</p>
          </div>
        </div>
      </div>
    </div>
  );
}

// Mount React Root
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<BrandGuardApp />);
