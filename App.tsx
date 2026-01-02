
import React, { useState, useEffect, useMemo, useRef } from 'react';
import { Video, Category } from './types';
import { CATEGORIES, FALLBACK_VIDEOS } from './constants';

const App: React.FC = () => {
  const [videos, setVideos] = useState<Video[]>([]);
  const [search, setSearch] = useState('');
  const [activeCategory, setActiveCategory] = useState('all');
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null);
  const [loading, setLoading] = useState(true);

  const playerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const loadVideos = async () => {
      setLoading(true);
      try {
        const response = await fetch('videos.json');
        let data: Video[] = [];
        if (response.ok) {
          data = await response.json();
        } else {
          data = FALLBACK_VIDEOS;
        }

        // Process videos: Parse dates and categories
        const processed = data.map(v => {
          const dateMatch = v.title.match(/(\d{2})\.(\d{2})\.(\d{4})/);
          const parsedDate = dateMatch ? new Date(parseInt(dateMatch[3]), parseInt(dateMatch[2]) - 1, parseInt(dateMatch[1])) : null;
          
          let category = 'Diğer';
          for (const cat of CATEGORIES) {
            if (cat.id === 'all') continue;
            const normTitle = v.title.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
            const normCat = cat.id.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
            if (normTitle.includes(normCat)) {
              category = cat.name;
              break;
            }
          }

          return { ...v, parsedDate, category };
        });

        // Sort by date descending
        processed.sort((a, b) => {
          const timeA = a.parsedDate?.getTime() || 0;
          const timeB = b.parsedDate?.getTime() || 0;
          return timeB - timeA;
        });

        setVideos(processed);
      } catch (err) {
        setVideos(FALLBACK_VIDEOS);
      } finally {
        setLoading(false);
      }
    };

    loadVideos();
  }, []);

  const filteredVideos = useMemo(() => {
    return videos.filter(v => {
      const searchLower = search.toLowerCase();
      const matchesSearch = v.title.toLowerCase().includes(searchLower);
      
      let matchesCategory = true;
      if (activeCategory !== 'all') {
        const normTitle = v.title.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        const normCat = activeCategory.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        matchesCategory = normTitle.includes(normCat);
      }

      return matchesSearch && matchesCategory;
    });
  }, [videos, search, activeCategory]);

  const handleVideoSelect = (video: Video) => {
    setSelectedVideo(video);
    if (window.innerWidth < 1024) {
      playerRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const formatDate = (date: Date | null | undefined) => {
    if (!date) return 'Tarih Bilinmiyor';
    return new Intl.DateTimeFormat('tr-TR', { day: '2-digit', month: 'long', year: 'numeric' }).format(date);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      {/* Dynamic Background Glows */}
      <div className="fixed top-0 left-1/4 w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="fixed bottom-0 right-1/4 w-[400px] h-[400px] bg-purple-500/10 rounded-full blur-[100px] pointer-events-none" />

      {/* Header */}
      <header className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800/50">
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
            {/* Brand */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                <span className="text-xl">📼</span>
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-tight text-white">Volkan'ın Arşivi</h1>
                <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">Premium Experience</p>
              </div>
            </div>

            {/* Search */}
            <div className="relative w-full md:max-w-sm">
              <input
                type="text"
                placeholder="Video veya yayın ara..."
                className="w-full bg-slate-900 border border-slate-800 rounded-2xl py-2.5 pl-10 pr-4 text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all outline-none text-slate-200 placeholder-slate-500"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
              </span>
            </div>
          </div>

          {/* Categories */}
          <div className="mt-6 flex items-center gap-2 overflow-x-auto no-scrollbar pb-1">
            {CATEGORIES.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.id)}
                className={`px-4 py-2 rounded-full text-xs font-semibold whitespace-nowrap transition-all duration-200 border ${
                  activeCategory === cat.id
                    ? 'bg-white text-slate-950 border-white shadow-lg shadow-white/10'
                    : 'bg-slate-900/50 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-slate-200'
                }`}
              >
                {cat.name}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Area: Results List */}
        <div className="lg:col-span-7 xl:col-span-8 order-2 lg:order-1">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              {activeCategory === 'all' ? 'Tüm Videolar' : CATEGORIES.find(c => c.id === activeCategory)?.name + ' Koleksiyonu'}
              <span className="bg-slate-900 text-slate-400 text-[10px] px-2 py-0.5 rounded-full border border-slate-800">
                {filteredVideos.length}
              </span>
            </h2>
          </div>

          <div className="space-y-4">
            {loading ? (
              Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="animate-pulse bg-slate-900/50 rounded-2xl p-4 flex gap-4 border border-slate-800/50">
                  <div className="w-32 sm:w-48 aspect-video bg-slate-800 rounded-xl" />
                  <div className="flex-1 space-y-3 py-1">
                    <div className="h-4 bg-slate-800 rounded w-3/4" />
                    <div className="h-3 bg-slate-800 rounded w-1/4" />
                  </div>
                </div>
              ))
            ) : filteredVideos.length > 0 ? (
              filteredVideos.map((video) => (
                <div
                  key={video.embed_id}
                  onClick={() => handleVideoSelect(video)}
                  className={`group relative flex gap-4 p-3 sm:p-4 rounded-2xl border transition-all cursor-pointer ${
                    selectedVideo?.embed_id === video.embed_id
                      ? 'bg-indigo-500/5 border-indigo-500/50 ring-1 ring-indigo-500/20 shadow-lg shadow-indigo-500/5'
                      : 'bg-slate-900/30 border-slate-800/50 hover:bg-slate-900/60 hover:border-slate-700 shadow-sm'
                  }`}
                >
                  {/* Thumbnail Placeholder */}
                  <div className="relative w-32 sm:w-44 lg:w-48 flex-shrink-0 aspect-video rounded-xl bg-slate-800 overflow-hidden shadow-inner">
                    <div className="absolute inset-0 bg-gradient-to-br from-slate-700/20 to-slate-900/50" />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="w-10 h-10 rounded-full bg-slate-900/80 backdrop-blur-md flex items-center justify-center text-slate-400 group-hover:scale-110 group-hover:text-white transition-transform">
                        <svg className="w-5 h-5 ml-0.5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg>
                      </div>
                    </div>
                  </div>

                  {/* Info */}
                  <div className="flex-1 flex flex-col justify-center min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                        {video.category}
                      </span>
                      {selectedVideo?.embed_id === video.embed_id && (
                        <span className="flex h-2 w-2 rounded-full bg-indigo-500 animate-pulse" />
                      )}
                    </div>
                    <h3 className="text-sm sm:text-base font-semibold text-white line-clamp-2 leading-snug group-hover:text-indigo-300 transition-colors">
                      {video.title}
                    </h3>
                    <div className="mt-2 flex items-center gap-3 text-xs text-slate-500 font-medium">
                      <span className="flex items-center gap-1">
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                        {formatDate(video.parsedDate)}
                      </span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="py-20 flex flex-col items-center justify-center text-center">
                <div className="w-20 h-20 bg-slate-900 rounded-3xl flex items-center justify-center text-3xl mb-4 border border-slate-800">
                  🔭
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Sonuç Bulunamadı</h3>
                <p className="text-slate-500 text-sm max-w-xs">Aradığınız kriterlere uygun video bulamadık. Lütfen farklı bir anahtar kelime deneyin.</p>
                <button onClick={() => {setSearch(''); setActiveCategory('all');}} className="mt-6 text-indigo-400 font-semibold text-sm hover:underline">Aramayı Temizle</button>
              </div>
            )}
          </div>
        </div>

        {/* Right Area: Player (Sticky) */}
        <aside className="lg:col-span-5 xl:col-span-4 order-1 lg:order-2">
          <div ref={playerRef} className="sticky top-40 lg:top-[160px] space-y-6">
            <div className={`overflow-hidden rounded-3xl border transition-all duration-500 ${selectedVideo ? 'border-indigo-500/30 bg-slate-900 shadow-2xl shadow-indigo-500/10 scale-100' : 'border-slate-800 bg-slate-900/50 opacity-90'}`}>
              <div className="aspect-video relative bg-black">
                {selectedVideo ? (
                  <iframe
                    className="absolute inset-0 w-full h-full border-0"
                    src={`https://rumble.com/embed/${selectedVideo.embed_id}/?pub=4o7uxk&autoplay=1`}
                    title={selectedVideo.title}
                    allowFullScreen
                  />
                ) : (
                  <div className="absolute inset-0 flex flex-col items-center justify-center p-8 text-center bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-slate-800 to-black">
                    <div className="w-16 h-16 rounded-full bg-slate-900 border border-slate-700 flex items-center justify-center text-3xl mb-4">
                      🎬
                    </div>
                    <p className="text-slate-300 font-bold mb-1">Keyfinize Bakın</p>
                    <p className="text-slate-500 text-xs leading-relaxed">Başlamak için listeden bir video seçin. Arşivdeki binlerce saatlik içerik sizi bekliyor.</p>
                  </div>
                )}
              </div>
              
              <div className="p-6">
                {selectedVideo ? (
                  <>
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-[10px] font-bold uppercase tracking-widest px-2.5 py-1 rounded-full bg-white text-slate-950">
                        {selectedVideo.category}
                      </span>
                      <span className="flex items-center gap-1 text-[10px] font-bold text-indigo-400 uppercase tracking-widest">
                        <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
                        Şu an İzleniyor
                      </span>
                    </div>
                    <h2 className="text-lg font-bold text-white leading-tight mb-2">
                      {selectedVideo.title}
                    </h2>
                    <p className="text-xs text-slate-400 font-medium">
                      Yayın Tarihi: {formatDate(selectedVideo.parsedDate)}
                    </p>
                    
                    <div className="mt-8 pt-6 border-t border-slate-800 grid grid-cols-2 gap-4">
                       <button className="flex flex-col items-center gap-1.5 p-3 rounded-2xl bg-slate-800/50 hover:bg-slate-800 transition-colors border border-slate-700/50">
                          <span className="text-lg">🔗</span>
                          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">Bağlantıyı Kopyala</span>
                       </button>
                       <button className="flex flex-col items-center gap-1.5 p-3 rounded-2xl bg-slate-800/50 hover:bg-slate-800 transition-colors border border-slate-700/50">
                          <span className="text-lg">⭐</span>
                          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">Favorilere Ekle</span>
                       </button>
                    </div>
                  </>
                ) : (
                  <div className="py-2 text-center">
                    <p className="text-slate-600 text-[10px] font-bold uppercase tracking-widest">Premium Player v2.5</p>
                  </div>
                )}
              </div>
            </div>

            {/* AI Side Panel Placeholder */}
            <div className="p-5 rounded-3xl bg-indigo-500/5 border border-indigo-500/20 backdrop-blur-sm">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-indigo-400">✨</span>
                  <span className="text-xs font-bold text-indigo-200 uppercase tracking-wider">Arşiv İstatistiği</span>
                </div>
                <div className="grid grid-cols-2 gap-4">
                   <div className="space-y-1">
                      <p className="text-slate-500 text-[10px] font-bold uppercase">Toplam Video</p>
                      <p className="text-xl font-bold text-white">{videos.length}</p>
                   </div>
                   <div className="space-y-1">
                      <p className="text-slate-500 text-[10px] font-bold uppercase">En Aktif Kanal</p>
                      <p className="text-sm font-bold text-white">Hype (VOD)</p>
                   </div>
                </div>
            </div>
          </div>
        </aside>
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-900 bg-slate-950 py-12 px-4 sm:px-6 lg:px-8 text-center">
        <div className="max-w-screen-2xl mx-auto">
          <p className="text-slate-600 text-xs font-medium uppercase tracking-widest mb-4">Volkan'ın Arşivi &copy; 2025</p>
          <div className="flex items-center justify-center gap-6 text-slate-500">
             <a href="#" className="hover:text-indigo-400 transition-colors text-xs uppercase font-bold tracking-tighter">Kullanım Koşulları</a>
             <a href="#" className="hover:text-indigo-400 transition-colors text-xs uppercase font-bold tracking-tighter">Gizlilik</a>
             <a href="#" className="hover:text-indigo-400 transition-colors text-xs uppercase font-bold tracking-tighter">İletişim</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
