import { useState } from 'react';
import axios from 'axios';

export default function HomePage() {
  const [sentence, setSentence] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [dismissNotice, setDismissNotice] = useState(false);

  const handleRecommend = async () => {
    if (!sentence.trim()) {
      setError('कृपया एक मराठी वाक्य किंवा प्रसंग प्रविष्ट करा.');
      setResult(null);
      return;
    }

    try {
      setError('');
      setDismissNotice(false);
      setLoading(true);
      const payload = {
        sentence,
        threshold: 0.35,
      };
      const response = await axios.post('http://localhost:8000/api/recommend', payload);
      setResult(response.data);
    } catch (err) {
      const message = err.response?.data?.detail || 'शिफारस मिळवण्यात अडचण आली. कृपया पुन्हा प्रयत्न करा.';
      setError(message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const preprocessing = result ? (result.preprocessing || result.top_matches?.[0]?.preprocessing) : null;
  const isAIFallback = result?.source === 'ai_fallback';

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.2),_transparent_25%),radial-gradient(circle_at_bottom_right,_rgba(14,165,233,0.15),_transparent_20%),#f8fafc] py-10 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="relative overflow-hidden rounded-[2rem] border border-slate-200 bg-white/95 shadow-[0_40px_120px_-40px_rgba(14,165,233,0.35)]">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.12),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(14,165,233,0.14),_transparent_25%)] pointer-events-none" />
          
          <div className="relative grid gap-8 lg:grid-cols-[1.2fr_0.8fr] p-10 lg:p-12">
            {/* Left Header Section */}
            <div className="space-y-6 animate-fade-in">
              <span className="inline-flex items-center gap-2 rounded-full bg-sky-50 px-4 py-2 text-sm font-semibold text-sky-700 shadow-sm shadow-sky-200/30">
                मराठी म्हण शिफारस प्रणाली • Marathi Proverb Recommender
              </span>
              <div>
                <h1 className="text-5xl font-extrabold tracking-tight text-slate-900 sm:text-6xl">
                  Discover the right Marathi proverb for every moment.
                </h1>
                <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-600">
                  आपली परिस्थिती किंवा प्रसंग प्रविष्ट करा आणि त्याला सर्वात समर्पक असणारी पारंपरिक मराठी म्हण, तिचा सविस्तर अर्थ आणि सांस्कृतिक बोध सहजपणे मिळवा.
                </p>
              </div>

              {/* Natural Feature Highlights */}
              <div className="grid gap-4 sm:grid-cols-3">
                <div className="rounded-3xl bg-slate-50 p-5 shadow-sm border border-slate-200 transition hover:-translate-y-1 hover:shadow-md">
                  <p className="text-sm uppercase tracking-[0.18em] text-slate-500 font-semibold">वारसा</p>
                  <p className="mt-2 text-lg font-semibold text-slate-900">पारंपरिक म्हणी</p>
                  <p className="mt-1 text-xs text-slate-500">लोकसंस्कृती व साहित्यातील म्हणी</p>
                </div>
                <div className="rounded-3xl bg-slate-50 p-5 shadow-sm border border-slate-200 transition hover:-translate-y-1 hover:shadow-md">
                  <p className="text-sm uppercase tracking-[0.18em] text-slate-500 font-semibold">बोध</p>
                  <p className="mt-2 text-lg font-semibold text-slate-900">सविस्तर अर्थ</p>
                  <p className="mt-1 text-xs text-slate-500">प्रसंगानुरूप अचूक स्पष्टीकरण</p>
                </div>
                <div className="rounded-3xl bg-slate-50 p-5 shadow-sm border border-slate-200 transition hover:-translate-y-1 hover:shadow-md">
                  <p className="text-sm uppercase tracking-[0.18em] text-slate-500 font-semibold">संदर्भ</p>
                  <p className="mt-2 text-lg font-semibold text-slate-900">प्रमाणित स्त्रोत</p>
                  <p className="mt-1 text-xs text-slate-500">विश्वसनीय संदर्भ व पडताळणी</p>
                </div>
              </div>
            </div>

            {/* Right Input Form */}
            <div className="rounded-[2rem] bg-slate-950 p-8 text-white shadow-2xl shadow-slate-600/30 animate-fade-in flex flex-col justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.35em] text-sky-300/80">म्हण शोधा</p>
                <h2 className="mt-3 text-3xl font-bold">परिस्थिती प्रविष्ट करा</h2>
                <p className="mt-2 text-slate-300 text-sm">
                  कोणतीही परिस्थिती किंवा वाक्य लिहा आणि समर्पक म्हण मिळवा.
                </p>

                <div className="mt-6 space-y-4">
                  <textarea
                    className="w-full min-h-[160px] rounded-3xl border border-slate-700 bg-slate-900/90 p-5 text-lg text-white placeholder-slate-500 focus:border-sky-400 focus:outline-none focus:ring-2 focus:ring-sky-400/40"
                    value={sentence}
                    onChange={e => setSentence(e.target.value)}
                    placeholder="उदा. अभ्यास न करता परीक्षेला जाणे..."
                  />

                  <button
                    className="w-full rounded-full bg-gradient-to-r from-sky-500 to-cyan-500 px-6 py-3.5 text-lg font-semibold text-white shadow-lg shadow-sky-500/30 transition hover:scale-[1.01] hover:shadow-sky-500/50 disabled:cursor-not-allowed disabled:opacity-60"
                    onClick={handleRecommend}
                    disabled={loading}
                  >
                    {loading ? 'शोधत आहे... / Finding Proverb...' : 'म्हण शोधा / Recommend Proverb'}
                  </button>

                  {error && <p className="rounded-2xl bg-rose-50 px-4 py-3 text-sm text-rose-700 border border-rose-200">{error}</p>}
                </div>
              </div>

              <div className="mt-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
                <p className="text-xs uppercase tracking-wider text-slate-400 font-semibold">टीप / Tip</p>
                <p className="mt-1 text-xs text-slate-300">
                  प्रसंगाचे स्पष्ट वर्णन केल्यास सर्वात अचूक आणि समर्पक म्हण शोधता येते.
                </p>
              </div>
            </div>
          </div>

          {/* Results Area */}
          <div className="border-t border-slate-200 bg-slate-50 p-10">
            {!result ? (
              <div className="mx-auto max-w-5xl text-center py-8 animate-fade-in">
                <p className="text-slate-500 text-lg">कोणतीही परिस्थिती प्रविष्ट करून "म्हण शोधा" वर क्लिक करा.</p>
              </div>
            ) : (
              <div className="mx-auto max-w-5xl space-y-8 animate-fade-in">
                {/* Result Card */}
                <div className="rounded-[2rem] bg-white p-8 shadow-xl border border-slate-200">
                  {/* Top Status Badges */}
                  <div className="flex flex-wrap items-center justify-between gap-3 pb-6 border-b border-slate-100">
                    <div className="flex flex-wrap items-center gap-2">
                      {/* Collection Badge */}
                      <span className="inline-flex items-center gap-1.5 rounded-full bg-sky-50 px-3.5 py-1.5 text-xs font-semibold text-sky-700 border border-sky-200">
                        {isAIFallback ? '✨ विशेष शिफारस (Curated Match)' : '📚 प्रमाणित संग्रह (Traditional Collection)'}
                      </span>

                      {/* Verification Status Badge */}
                      {result.verification_status === 'verified' && (
                        <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3.5 py-1.5 text-xs font-semibold text-emerald-700 border border-emerald-200">
                          ✓ Verified Traditional Proverb
                        </span>
                      )}
                      {result.verification_status === 'unverified' && (
                        <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-50 px-3.5 py-1.5 text-xs font-semibold text-amber-700 border border-amber-200">
                          समीक्षणीय म्हण / Suggested Proverb
                        </span>
                      )}
                      {result.verification_status === 'not_found' && (
                        <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-100 px-3.5 py-1.5 text-xs font-semibold text-slate-700 border border-slate-200">
                          पर्यायी म्हण / Closest Available Match
                        </span>
                      )}
                    </div>

                    <div className="text-right">
                      {result.confidence !== null && result.confidence !== undefined ? (
                        <p className="text-sm text-slate-500">
                          सुसंगतता (Match):{' '}
                          <span className="font-semibold text-slate-900">{result.confidence.toFixed(1)}%</span>
                        </p>
                      ) : (
                        <span className="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                          सुसंगत शिफारस (Relevant Match)
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Gentle Fallback Notice if present */}
                  {result.fallback_notice && !dismissNotice && (
                    <div className="mt-5 rounded-2xl bg-slate-50 border border-slate-200 p-4 text-sm text-slate-700 shadow-sm animate-fade-in flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-sky-600 font-bold">ℹ️</span>
                        <span>{result.fallback_notice}</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => setDismissNotice(true)}
                        className="rounded-lg p-1 text-slate-400 hover:text-slate-700 transition focus:outline-none"
                        title="बंद करा"
                      >
                        ✕
                      </button>
                    </div>
                  )}

                  {/* Proverb Title Section */}
                  <div className="mt-6">
                    <p className="text-xs uppercase tracking-[0.2em] text-slate-400 font-semibold">शिफारस केलेली म्हण • Recommended Proverb</p>
                    <h2 className="mt-2 text-4xl sm:text-5xl font-extrabold text-slate-900 leading-tight">
                      {result.proverb}
                    </h2>
                  </div>

                  {/* Metadata and Context Grid */}
                  <div className="mt-8 grid gap-6 md:grid-cols-[1.4fr_1fr]">
                    {/* Meaning and Explanation */}
                    <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
                      <p className="text-xs uppercase tracking-[0.18em] text-slate-500 font-semibold">अर्थ व स्पष्टीकरण / Meaning</p>
                      <p className="mt-3 text-slate-800 leading-relaxed font-medium">
                        {result.meaning_in_depth || result.meaning}
                      </p>
                      {result.match_explanation && (
                        <div className="mt-4 pt-4 border-t border-slate-200">
                          <p className="text-xs uppercase tracking-[0.18em] text-slate-500 font-semibold">प्रसंगाशी सुसंगतता:</p>
                          <p className="mt-1.5 text-xs text-slate-600 italic">{result.match_explanation}</p>
                        </div>
                      )}
                    </div>

                    {/* Keywords */}
                    <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
                      <p className="text-xs uppercase tracking-[0.18em] text-slate-500 font-semibold">संबंधित शब्द / Keywords</p>
                      <div className="mt-3 flex flex-wrap gap-2">
                        {result.keywords?.map((keyword, idx) => (
                          <span key={idx} className="rounded-full bg-white px-3 py-1.5 text-xs text-slate-600 border border-slate-200 shadow-sm font-medium">
                            {keyword}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Category and Emotion */}
                  <div className="mt-6 grid grid-cols-2 gap-4">
                    <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
                      <p className="text-xs uppercase tracking-[0.12em] text-slate-500 font-semibold">श्रेणी / Category</p>
                      <p className="mt-1 text-base font-semibold text-slate-800">{result.category}</p>
                    </div>
                    <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
                      <p className="text-xs uppercase tracking-[0.12em] text-slate-500 font-semibold">भावना / Tone</p>
                      <p className="mt-1 text-base font-semibold text-slate-800">{result.emotion}</p>
                    </div>
                  </div>

                  {/* Preprocessing Breakdown */}
                  {preprocessing && preprocessing.tokens?.length > 0 && (
                    <div className="mt-6 rounded-3xl border border-slate-200 bg-slate-50 p-6">
                      <p className="text-xs uppercase tracking-[0.12em] text-slate-500 font-semibold">
                        भाषावैज्ञानिक विश्लेषण (Tokenization → Stemming → POS)
                      </p>
                      <div className="mt-3 overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="text-left text-slate-500 border-b border-slate-200">
                              <th className="py-2 pr-4 font-semibold">शब्द (Token)</th>
                              <th className="py-2 pr-4 font-semibold">मूळ रूप (Lemma)</th>
                              <th className="py-2 pr-4 font-semibold">धातू (Stem)</th>
                              <th className="py-2 pr-4 font-semibold">व्याकरण (POS)</th>
                            </tr>
                          </thead>
                          <tbody>
                            {preprocessing.tokens?.map((tok, i) => (
                              <tr key={i} className="border-t border-slate-100">
                                <td className="py-2 pr-4 text-slate-800 font-medium">{tok}</td>
                                <td className="py-2 pr-4 text-slate-600">{preprocessing.lemmas?.[i] || '-'}</td>
                                <td className="py-2 pr-4 text-slate-600">{preprocessing.stems?.[i] || '-'}</td>
                                <td className="py-2 pr-4 text-slate-600">
                                  <span className="rounded bg-slate-200 px-1.5 py-0.5 text-xs font-mono text-slate-700">
                                    {preprocessing.pos_tags?.[i] || '-'}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>

                {/* Top Related Proverbs Section */}
                {result.top_matches?.length > 0 && (
                  <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-xl overflow-x-auto">
                    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                      <div>
                        <p className="text-sm uppercase tracking-[0.18em] text-slate-500 font-semibold">
                          इतर संबंधित म्हणी • Other Related Options
                        </p>
                        <h3 className="mt-2 text-2xl font-bold text-slate-900">
                          या परिस्थितीशी जुळणाऱ्या इतर म्हणी
                        </h3>
                      </div>
                      <span className="rounded-full bg-sky-50 px-4 py-2 text-sky-700 text-sm font-semibold border border-sky-200">
                        {result.top_matches.length} म्हणी
                      </span>
                    </div>

                    <div className="mt-6 overflow-x-auto">
                      <table className="min-w-full text-left text-sm">
                        <thead>
                          <tr className="border-b border-slate-200 text-slate-500">
                            <th className="px-4 py-3 font-semibold">म्हण (Proverb)</th>
                            <th className="px-4 py-3 font-semibold">सुसंगतता (Match)</th>
                            <th className="px-4 py-3 font-semibold">श्रेणी (Category)</th>
                            <th className="px-4 py-3 font-semibold">भावना (Tone)</th>
                            <th className="px-4 py-3 font-semibold">कीवर्ड्स (Keywords)</th>
                          </tr>
                        </thead>
                        <tbody>
                          {result.top_matches.map((match, idx) => (
                            <tr key={(match.id || '') + '-' + idx} className="border-b border-slate-100 hover:bg-slate-50 transition">
                              <td className="px-4 py-4 align-top font-semibold text-slate-900">{match.proverb}</td>
                              <td className="px-4 py-4 align-top text-slate-700 font-medium">
                                {match.confidence !== null && match.confidence !== undefined ? `${match.confidence.toFixed(1)}%` : '-'}
                              </td>
                              <td className="px-4 py-4 align-top text-slate-700">{match.category}</td>
                              <td className="px-4 py-4 align-top text-slate-700">{match.emotion}</td>
                              <td className="px-4 py-4 align-top text-slate-700">{match.keywords?.join(', ')}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
