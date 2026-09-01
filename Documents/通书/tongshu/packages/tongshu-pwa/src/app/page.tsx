"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useTongshuStore } from "../store/useTongshuStore";

type Page = "today" | "setup";

export default function HomePage() {
  const [page, setPage] = useState<Page>("today");
  const [profile] = useTongshuStore((s) => [s.profile]);

  useEffect(() => {
    if (!profile) setPage("setup");
  }, [profile]);

  if (page === "setup") return <SetupPage />;
  return <TodayPage />;
}

function TodayPage() {
  const [daily, setDaily] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [profile] = useTongshuStore((s) => [s.profile]);

  useEffect(() => {
    fetch("/daily" + (profile?.profile_id ? `?profile_id=${profile.profile_id}` : ""))
      .then((r) => r.json()).then((d) => { setDaily(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [profile]);

  if (loading) return <Loader />;
  if (!daily) return <EmptyLink />;

  const hex = daily.moduls?.find((m: any) => m.id === "hexagram");
  const rhy = daily.moduls?.find((m: any) => m.id === "rhythm");
  const yij = daily.moduls?.find((m: any) => m.id === "yiji");
  const health = daily.moduls?.find((m: any) => m.id === "seasonal");
  const quote = daily.moduls?.find((m: any) => m.id === "quote");

  return (
    <div style={styles.root}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.flexBetween}>
          <span style={styles.logo}>TONGSHU</span>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={styles.dateLabel}>{daily.date}</span>
            {daily.solar_term && <span style={styles.termBadge}>{daily.solar_term}</span>}
          </div>
        </div>
        <div style={styles.divider} />
        <div style={styles.flexBetween}>
          <span style={styles.lunar}>{daily.lunar}</span>
          <span style={styles.ganzhi}>{daily.ganzhi?.day}</span>
        </div>
      </div>

      {/* Personal */}
      {daily.personal && (
        <div style={{ ...styles.personal, borderLeftColor: daily.personal.match === "clashing" ? "#b84a4a" : daily.personal.match === "harmonious" ? "#2d9d6f" : "#c9a84c" }}>
          <div style={styles.dot} />
          <p style={styles.personalText}>{daily.personal.advice_de}</p>
        </div>
      )}

      {/* Hexagram Hero */}
      {hex && (
        <div style={styles.hexSection}>
          <div style={styles.hexLabel}>HEUTE</div>
          <h2 style={styles.hexTitle}>{hex.title_de}</h2>
          <p style={styles.hexSub}>{hex.title_zh}</p>
          <div style={styles.divider} />
          <p style={styles.hexContent}>{hex.content_de}</p>
          {hex.content_zh && <p style={styles.hexZh}>{hex.content_zh}</p>}
        </div>
      )}

      {/* Health */}
      {health && <Card icon="🪷" title={health.title_de} body={health.content_de} />}

      {/* Rhythm */}
      {rhy && (
        <div style={styles.card}>
          <div style={styles.cardHeader}><span style={styles.cardIcon}>◷</span><h3 style={styles.cardTitle}>{rhy.title_de}</h3></div>
          <p style={styles.cardBody}>{rhy.content_de}</p>
          <div style={styles.rhythmGrid}>
            {[["☀️","Vormittag",rhy.morning_de],["🌤","Nachmittag",rhy.afternoon_de],["🌙","Abend",rhy.evening_de]].map(([emo,lab,val])=>(
              <div key={lab} style={{ display:"flex",alignItems:"center",gap:10 }}>
                <span style={{fontSize:16,width:24,textAlign:"center"}}>{emo}</span>
                <div>
                  <span style={{display:"block",fontSize:12,fontWeight:500,color:"#8a8f98"}}>{lab}</span>
                  <span style={{display:"block",fontSize:14,fontWeight:500,color:"#d0d6e0"}}>{val?.split(": ")[1]||"—"}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quote */}
      {quote && (
        <div style={styles.card}>
          <div style={styles.cardHeader}><span style={styles.cardIcon}>「</span><h3 style={styles.cardTitle}>{quote.title_de}</h3></div>
          <p style={styles.quoteText}>{quote.content_de}</p>
        </div>
      )}

      {/* YiJi */}
      {yij && (
        <div style={styles.card}>
          <div style={styles.cardHeader}><span style={styles.cardIcon}>⚖</span><h3 style={styles.cardTitle}>{yij.title_de}</h3></div>
          {yij.yi_zh?.length > 0 && (
            <div><span style={styles.tagLabel}>Günstig</span><div style={styles.tags}>
              {yij.yi_zh.map((y:string,i:number)=>(<span key={i} style={styles.tagGreen}>{y}</span>))}
            </div></div>
          )}
          {yij.ji_zh?.length > 0 && (
            <div style={{marginTop:10}}><span style={styles.tagLabel}>Weniger</span><div style={styles.tags}>
              {yij.ji_zh.map((j:string,i:number)=>(<span key={i} style={styles.tagRed}>{j}</span>))}
            </div></div>
          )}
        </div>
      )}

      {/* Footer */}
      <div style={styles.footer}>
        <div style={styles.nav}>
          <span style={styles.navActive}>Heute</span>
          <Link href="/setup" style={styles.navLink}>Profil</Link>
        </div>
        <p style={styles.disclaimer}>{daily.disclaimer}</p>
      </div>
    </div>
  );
}

function SetupPage() {
  const [form, setForm] = useState({ birth_date: "", birth_time: "", gender: "male", city: "" });
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState<string|null>(null);
  const setProfile = useTongshuStore((s) => s.setProfile);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const r = await fetch("/profiles", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ device_id: "web-" + Date.now(), ...form }),
      });
      const d = await r.json();
      if (d.id) { setProfile({ ...form, profile_id: d.id }); setDone(d.id); }
    } catch (err: any) { setDone("Fehler: " + err.message); }
    setLoading(false);
  };

  return (
    <div style={{...styles.root, padding:"20px"}}>
      <div style={styles.logo} style2="margin-bottom:24px">TONGSHU</div>
      <h2 style={{...styles.cardTitle, fontSize:18, marginBottom:20}}>Dein Geburtsprofil</h2>
      <form onSubmit={submit} style={{display:"flex",flexDirection:"column",gap:14}}>
        {["Geburtsdatum", "Geburtszeit", "Geschlecht", "Geburtsort"].map((label, i) => (
          <div key={label}>
            <label style={styles.label}>{label}</label>
            {i === 0 ? <input type="date" required value={form.birth_date} onChange={e=>setForm({...form,birth_date:e.target.value})} style={styles.input} /> :
             i === 1 ? <input type="time" required value={form.birth_time} onChange={e=>setForm({...form,birth_time:e.target.value})} style={styles.input} /> :
             i === 2 ? <select value={form.gender} onChange={e=>setForm({...form,gender:e.target.value})} style={styles.input}>
               <option value="male">Männlich</option><option value="female">Weiblich</option>
             </select> :
             <input type="text" value={form.city} onChange={e=>setForm({...form,city:e.target.value})} placeholder="Berlin, Shanghai, New York" style={styles.input} />}
          </div>
        ))}
        <button disabled={loading} style={styles.button}>{loading ? "Berechne..." : "Profil erstellen"}</button>
      </form>
      {done && <div style={styles.card}>
        <p style={{color:"#c9a84c",fontSize:14,fontWeight:500,marginBottom:6}}>Profil erstellt</p>
        <p style={{fontSize:10,color:"#62666d",wordBreak:"break-all"}}>{done}</p>
        <Link href="/" style={{display:"inline-block",marginTop:12,color:"#c9a84c",fontSize:13,fontWeight:500,letterSpacing:0.5}}>→ Zum Heute</Link>
      </div>}
    </div>
  );
}

function Card({ icon, title, body }: { icon: string; title: string; body: string }) {
  return (
    <div style={styles.card}>
      <div style={styles.cardHeader}><span style={styles.cardIcon}>{icon}</span><h3 style={styles.cardTitle}>{title}</h3></div>
      <p style={styles.cardBody}>{body}</p>
    </div>
  );
}

function Loader() {
  return <div style={{display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",minHeight:"100vh"}}>
    <div style={{width:36,height:36,border:"2px solid rgba(255,255,255,0.08)",borderTop:"2px solid #c9a84c",borderRadius:"50%",animation:"spin 1s linear infinite"}} />
    <p style={{marginTop:16,fontSize:14,color:"#8a8f98",letterSpacing:1}}>Lade TONGSHU</p>
  </div>;
}

function EmptyLink() {
  return <div style={{display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",minHeight:"100vh",padding:20,textAlign:"center"}}>
    <span style={{fontSize:40,opacity:0.2,marginBottom:16}}>🪷</span>
    <p style={{fontSize:14,color:"#8a8f98",marginBottom:16}}>Dein Geburtsprofil ist noch nicht eingerichtet.</p>
    <Link href="/setup" style={{padding:"10px 28px",background:"#c9a84c",color:"#08090a",borderRadius:8,fontWeight:600,fontSize:14,letterSpacing:0.3,textDecoration:"none"}}>Profil erstellen</Link>
  </div>;
}

const S = {
  root: { maxWidth: 480, margin: "0 auto", padding: "0 0 80px", minHeight: "100vh", background: "#08090a" },
  header: { padding:"24px 20px 16px", background:"#0f1011", borderBottom:"1px solid rgba(255,255,255,0.08)" },
  flexBetween: { display:"flex", justifyContent:"space-between", alignItems:"center" },
  logo: { fontSize:18, fontWeight:600, letterSpacing:3, color:"#c9a84c", marginBottom:12 },
  dateLabel: { fontSize:13, fontWeight:500, color:"#d0d6e0" },
  termBadge: { fontSize:11, fontWeight:500, color:"#c9a84c", background:"rgba(201,168,76,0.08)", padding:"2px 8px", borderRadius:4, border:"1px solid rgba(201,168,76,0.18)" },
  divider: { height:1, background:"rgba(255,255,255,0.08)", margin:"12px 0" },
  lunar: { fontSize:13, color:"#8a8f98" },
  ganzhi: { fontSize:13, fontWeight:500, color:"#d0d6e0" },
  personal: { margin:"16px 20px 0", padding:"14px 16px", background:"#191a1b", borderRadius:8, borderLeft:"3px solid #c9a84c", display:"flex", gap:10, alignItems:"flex-start" },
  dot: { width:8, height:8, borderRadius:"50%", background:"#c9a84c", marginTop:6, flexShrink:0 },
  personalText: { fontSize:14, lineHeight:1.55, color:"#d0d6e0", margin:0 },
  hexSection: { margin:"16px 20px 0", padding:"28px 24px", background:"linear-gradient(135deg,#191a1b 0%,#08090a 100%)", borderRadius:12, border:"1px solid rgba(255,255,255,0.08)" },
  hexLabel: { fontSize:10, fontWeight:600, letterSpacing:2, color:"#c9a84c", textTransform:"uppercase", marginBottom:8 },
  hexTitle: { fontSize:26, fontWeight:500, letterSpacing:-0.5, lineHeight:1.15, color:"#f7f8f8", margin:0 },
  hexSub: { fontSize:14, color:"#8a8f98", margin:"4px 0 0" },
  hexContent: { fontSize:15, lineHeight:1.6, color:"#d0d6e0", margin:0 },
  hexZh: { fontSize:13, lineHeight:1.5, color:"#c9a84ccb", fontStyle:"italic", margin:"12px 0 0" },
  card: { margin:"16px 20px 0", padding:"18px 20px", background:"#0f1011", borderRadius:10, border:"1px solid rgba(255,255,255,0.08)" },
  cardHeader: { display:"flex", alignItems:"center", gap:8, marginBottom:12 },
  cardIcon: { fontSize:16, color:"#c9a84c", opacity:0.8 },
  cardTitle: { fontSize:14, fontWeight:600, color:"#f7f8f8", letterSpacing:0.3, margin:0 },
  cardBody: { fontSize:14, lineHeight:1.6, color:"#d0d6e0", margin:0 },
  rhythmGrid: { display:"flex", flexDirection:"column", gap:8, marginTop:14, paddingTop:14, borderTop:"1px solid rgba(255,255,255,0.05)" },
  quoteText: { fontSize:16, lineHeight:1.65, color:"#f7f8f8", fontStyle:"italic", margin:0 },
  tagLabel: { display:"block", fontSize:11, fontWeight:600, color:"#8a8f98", textTransform:"uppercase", letterSpacing:0.5, marginBottom:6 },
  tags: { display:"flex", flexWrap:"wrap", gap:6 },
  tagGreen: { fontSize:12, fontWeight:500, color:"#2d9d6f", background:"rgba(45,157,111,0.12)", padding:"3px 10px", borderRadius:6, border:"1px solid rgba(45,157,111,0.2)" },
  tagRed: { fontSize:12, fontWeight:500, color:"#b84a4a", background:"rgba(184,74,74,0.12)", padding:"3px 10px", borderRadius:6, border:"1px solid rgba(184,74,74,0.2)" },
  footer: { padding:"24px 20px 32px", textAlign:"center" },
  nav: { display:"flex", gap:24, justifyContent:"center", marginBottom:16 },
  navActive: { fontSize:13, fontWeight:600, color:"#c9a84c" },
  navLink: { fontSize:13, fontWeight:500, color:"#8a8f98", textDecoration:"none" },
  disclaimer: { fontSize:11, lineHeight:1.5, color:"#62666d", margin:0 },
  label: { display:"block", fontSize:12, fontWeight:500, color:"#8a8f98", marginBottom:6, letterSpacing:0.3 },
  input: { width:"100%", padding:"10px 14px", background:"#0f1011", color:"#f7f8f8", border:"1px solid rgba(255,255,255,0.08)", borderRadius:8, fontSize:15, outline:"none" },
  button: { padding:"12px 20px", background:"#c9a84c", color:"#08090a", border:"none", borderRadius:8, fontSize:15, fontWeight:600, letterSpacing:0.3, cursor:"pointer" },
};

const styles: Record<string, React.CSSProperties> = S;