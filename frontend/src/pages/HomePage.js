import { useState } from 'react';
import axios from 'axios';

export default function HomePage() {
  const [sentence, setSentence] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRecommend = async () => {
    if (!sentence.trim()) {
      setError('कृपया एक मराठी वाक्य प्रविष्ट करा.');
      setResult(null);
      return;
    }

    try {
      setError('');
      setLoading(true);
      const response = await axios.post('http://localhost:8000/api/recommend', { sentence });
      setResult(response.data);
    } catch (err) {
      const message = err.response?.data?.detail || 'Recommendation failed. Please check the backend and try again.';
      setError(message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const preprocessing = result ? (result.preprocessing || result.top_matches?.[0]?.preprocessing) : null;

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.2),_transparent_25%),radial-gradient(circle_at_bottom_right,_rgba(14,165,233,0.15),_transparent_20%),#f8fafc] py-10 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="relative overflow-hidden rounded-[2rem] border border-slate-200 bg-white/95 shadow-[0_40px_120px_-40px_rgba(14,165,233,0.35)]">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.12),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(14,165,233,0.14),_transparent_25%)] pointer-events-none" />
          <div className="relative grid gap-8 lg:grid-cols-[1.2fr_0.8fr] p-10 lg:p-12">
            <div className="space-y-6 animate-fade-in">
              <span className="inline-flex items-center gap-2 rounded-full bg-sky-50 px-4 py-2 text-sm font-semibold text-sky-700 shadow-sm shadow-sky-200/30">
                Marathi proverb recommender
              </span>
              <div>
                <h1 className="text-5xl font-extrabold tracking-tight text-slate-900 sm:text-6xl">Discover the right Marathi proverb for every moment.</h1>
                <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-600">Type a Marathi sentence and get the best proverb recommendation, complete with meaning, emotion, and confidence.</p>
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                <div className="rounded-3xl bg-slate-50 p-5 shadow-sm border border-slate-200 transition hover:-translate-y-1 hover:shadow-md">
                  <p className="text-sm uppercase tracking-[0.18em] text-slate-500">Fast</p>
                  <p className="mt-3 text-xl font-semibold text-slate-900">Instant results</p>
                </div>
                <div className="rounded-3xl bg-slate-50 p-5 shadow-sm border border-slate-200 transition hover:-translate-y-1 hover:shadow-md">
                  <p className="text-sm uppercase tracking-[0.18em] text-slate-500">Accurate</p>
                  <p className="mt-3 text-xl font-semibold text-slate-900">Semantic matching</p>
                </div>
                <div className="rounded-3xl bg-slate-50 p-5 shadow-sm border border-slate-200 transition hover:-translate-y-1 hover:shadow-md">
                  <p className="text-sm uppercase tracking-[0.18em] text-slate-500">Cultural</p>
                  <p className="mt-3 text-xl font-semibold text-slate-900">Marathi context</p>
                </div>
              </div>
            </div>

            <div className="rounded-[2rem] bg-slate-950 p-8 text-white shadow-2xl shadow-slate-600/30 animate-fade-in">
              <p className="text-sm uppercase tracking-[0.35em] text-sky-300/80">Interactive demo</p>
              <h2 className="mt-4 text-3xl font-bold">Try it now</h2>
              <p className="mt-3 text-slate-300">Enter a sentence, click Recommend, and see a proverb selected for your situation.</p>

              <div className="mt-8 space-y-4">
                <textarea
                  className="w-full min-h-[170px] rounded-3xl border border-slate-700 bg-slate-900/90 p-5 text-lg text-white placeholder-slate-500 focus:border-sky-400 focus:outline-none focus:ring-2 focus:ring-sky-400/40"
                  value={sentence}
                  onChange={e => setSentence(e.target.value)}
                  placeholder="उदाहरण: तो अभ्यास न करता परीक्षेला गेला..."
                />

                <button
                  className="w-full rounded-full bg-gradient-to-r from-sky-500 to-cyan-500 px-6 py-3 text-lg font-semibold text-white shadow-lg shadow-sky-500/30 transition hover:scale-[1.01] hover:shadow-sky-500/50 disabled:cursor-not-allowed disabled:opacity-60"
                  onClick={handleRecommend}
                  disabled={loading}
                >
                  {loading ? 'Recommending...' : 'Recommend Proverb'}
                </button>

                {error && <p className="rounded-3xl bg-rose-50 px-4 py-3 text-sm text-rose-700 border border-rose-200">{error}</p>}

                <div className="rounded-3xl border border-slate-800 bg-slate-900/90 p-5">
                  <p className="text-sm uppercase tracking-[0.18em] text-slate-400">Pro tip</p>
                  <p className="mt-3 text-slate-300">Use a sentence with clear context or a lesson to get the strongest proverb match.</p>
                </div>
              </div>
            </div>
          </div>

          <div className="border-t border-slate-200 bg-slate-50 p-10">
            {!result ? (
              <div className="mx-auto max-w-5xl text-center animate-fade-in">
                <p className="text-slate-500">No recommendation yet. Type a sentence and click Recommend to begin.</p>
              </div>
            ) : (
              <div className="mx-auto max-w-5xl space-y-8 animate-fade-in">
                <div className="rounded-[2rem] bg-white p-8 shadow-xl border border-slate-200">
                  <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                    <div>
                      <p className="text-sm uppercase tracking-[0.18em] text-sky-600">Recommended Proverb</p>
                      <h2 className="mt-2 text-4xl font-bold text-slate-900">{result.proverb}</h2>
                    </div>
                    <div className="space-y-2 text-right">
                      <div className="inline-flex items-center gap-2 rounded-full bg-sky-50 px-4 py-2 text-sky-700 font-semibold">{result.category}</div>
                      <p className="text-slate-500">Confidence: <span className="font-semibold text-slate-900">{result.confidence.toFixed(1)}%</span></p>
                    </div>
                  </div>

                  <div className="mt-8 grid gap-6 lg:grid-cols-3">
                    <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
                      <p className="text-sm uppercase tracking-[0.18em] text-slate-500">Meaning (in depth)</p>
                      <p className="mt-3 text-slate-700">{result.meaning_in_depth || result.meaning}</p>
                    </div>
                    <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
                      <p className="text-sm uppercase tracking-[0.18em] text-slate-500">Keywords</p>
                      <div className="mt-3 flex flex-wrap gap-2">
                        {result.keywords.map((keyword, idx) => (
                          <span key={idx} className="rounded-full bg-white px-3 py-1 text-xs text-slate-500 border border-slate-200">{keyword}</span>
                        ))}
                      </div>
                    </div>
                    <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
                      <p className="text-sm uppercase tracking-[0.18em] text-slate-500">(Input situation hidden)</p>
                      <p className="mt-3 text-slate-400">The raw input situation is not displayed here by request.</p>
                    </div>
                  </div>

                  <div className="mt-6 grid grid-cols-2 gap-4">
                    <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
                      <p className="text-sm uppercase tracking-[0.12em] text-slate-500">Category</p>
                      <p className="mt-1 text-slate-700">{result.category}</p>
                    </div>
                    <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
                      <p className="text-sm uppercase tracking-[0.12em] text-slate-500">Emotion</p>
                      <p className="mt-1 text-slate-700">{result.emotion}</p>
                    </div>
                  </div>

                  {preprocessing ? (
                    <div className="mt-6 rounded-3xl border border-slate-200 bg-slate-50 p-6">
                      <p className="text-sm uppercase tracking-[0.12em] text-slate-500">Preprocessing (tokens → lemma / stem / POS)</p>
                      <div className="mt-3 overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="text-left text-slate-500">
                              <th className="py-2 pr-4">Token</th>
                              <th className="py-2 pr-4">Lemma</th>
                              <th className="py-2 pr-4">Stem</th>
                              <th className="py-2 pr-4">POS</th>
                            </tr>
                          </thead>
                          <tbody>
                            {preprocessing.tokens?.map((tok, i) => (
                              <tr key={i} className="border-t border-slate-100">
                                <td className="py-2 pr-4 text-slate-700">{tok}</td>
                                <td className="py-2 pr-4 text-slate-700">{preprocessing.lemmas?.[i] || '-'}</td>
                                <td className="py-2 pr-4 text-slate-700">{preprocessing.stems?.[i] || '-'}</td>
                                <td className="py-2 pr-4 text-slate-700">{preprocessing.pos_tags?.[i] || '-'}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  ) : (
                    <div className="mt-6 text-sm text-slate-500">No preprocessing available for this recommendation.</div>
                  )}
                </div>

                {result.top_matches?.length > 0 && (
                  <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-xl overflow-x-auto">
                    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                      <div>
                        <p className="text-sm uppercase tracking-[0.18em] text-slate-500">Top Matches</p>
                        <h3 className="mt-2 text-2xl font-semibold text-slate-900">Other strong options</h3>
                      </div>
                      <span className="rounded-full bg-sky-50 px-4 py-2 text-sky-700 text-sm font-semibold">{result.top_matches.length} results</span>
                    </div>

                    <div className="mt-6 overflow-x-auto">
                      <table className="min-w-full text-left text-sm">
                        <thead>
                          <tr className="border-b border-slate-200 text-slate-500">
                            <th className="px-4 py-3">Proverb</th>
                            <th className="px-4 py-3">Confidence</th>
                            <th className="px-4 py-3">Category</th>
                            <th className="px-4 py-3">Emotion</th>
                            <th className="px-4 py-3">Keywords</th>
                          </tr>
                        </thead>
                        <tbody>
                          {result.top_matches.map((match, idx) => (
                            <tr key={(match.id || '') + '-' + idx} className="border-b border-slate-100 hover:bg-slate-50">
                              <td className="px-4 py-4 align-top font-medium text-slate-900">{match.proverb}</td>
                              <td className="px-4 py-4 align-top text-slate-700">{match.confidence.toFixed(1)}%</td>
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
