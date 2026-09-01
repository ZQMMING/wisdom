"use client";
import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const theme = {
  bg: "#08090a",
  bgPanel: "#0f1011",
  bgSurface: "#191a1b",
  bgElevated: "#28282c",
  text: "#f7f8f8",
  textSecondary: "#d0d6e0",
  textMuted: "#8a8f98",
  textSubtle: "#62666d",
  gold: "#c9a84c",
  goldLight: "#e8d48b",
  border: "rgba(255,255,255,0.08)",
  borderSubtle: "rgba(255,255,255,0.05)",
};

export default function ProfilePage() {
  const [form, setForm] = useState({
    birth_date: "",
    birth_time: "",
    gender: "male",
    city: "",
  });
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const r = await fetch(`${API}/profiles`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          device_id: "web-" + Date.now(),
          ...form,
        }),
      });
      const data = await r.json();
      setResult(data);
    } catch (err: any) {
      setResult({ error: err.message });
    }
    setLoading(false);
  };

  return (
    <main style={{ maxWidth: 480, margin: "0 auto", padding: "0 0 40px", minHeight: "100vh", background: theme.bg, color: theme.text }}>
      {/* Header */}
      <header style={{ padding: "24px 20px 16px", background: theme.bgPanel, borderBottom: `1px solid ${theme.border}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: 18, fontWeight: 600, letterSpacing: 3, color: theme.gold }}>TONGSHU</span>
        <span style={{ fontSize: 13, fontWeight: 500, color: theme.textMuted }}>Profil</span>
      </header>

      {/* Form */}
      <div style={{ padding: "20px 20px 0" }}>
        <h2 style={{ margin: 0, fontSize: 14, fontWeight: 600, color: theme.text, letterSpacing: "0.3px", marginBottom: 20 }}>
          Dein Geburtsprofil
        </h2>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div>
            <label style={labelStyle}>Geburtsdatum</label>
            <input type="date" required value={form.birth_date} onChange={(e) => setForm({ ...form, birth_date: e.target.value })} style={inputStyle} />
          </div>
          <div>
            <label style={labelStyle}>Geburtszeit</label>
            <input type="time" required value={form.birth_time} onChange={(e) => setForm({ ...form, birth_time: e.target.value })} style={inputStyle} />
          </div>
          <div>
            <label style={labelStyle}>Geschlecht</label>
            <select value={form.gender} onChange={(e) => setForm({ ...form, gender: e.target.value })} style={inputStyle}>
              <option value="male">Männlich</option>
              <option value="female">Weiblich</option>
            </select>
          </div>
          <div>
            <label style={labelStyle}>Geburtsort</label>
            <input type="text" value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} style={inputStyle} placeholder="z.B. Berlin, Shanghai, New York" />
            <p style={{ margin: "4px 0 0", fontSize: 11, color: theme.textSubtle }}>Wir unterstützen 100+ Städte weltweit</p>
          </div>
          <button type="submit" disabled={loading} style={{
            ...buttonStyle,
            opacity: loading ? 0.5 : 1,
            cursor: loading ? "not-allowed" : "pointer",
          }}>
            {loading ? "Berechne..." : "Profil erstellen"}
          </button>
        </form>
      </div>

      {/* Result */}
      {result && (
        <div style={{ margin: "20px 20px 0", padding: "20px", background: theme.bgSurface, borderRadius: 10, border: `1px solid ${theme.border}` }}>
          {result.error ? (
            <p style={{ color: "#b84a4a", fontSize: 14, margin: 0 }}>Fehler: {result.error}</p>
          ) : (
            <>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                <h3 style={{ margin: 0, fontSize: 14, fontWeight: 600, color: theme.gold }}>Dein BaZi-Profil</h3>
                <span style={{ fontSize: 10, fontWeight: 600, color: theme.textMuted, background: theme.bgElevated, padding: "2px 8px", borderRadius: 4, border: `1px solid ${theme.borderSubtle}`, letterSpacing: "0.5px" }}>四柱八字</span>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 8, marginBottom: 16 }}>
                {Object.entries(result.chart || {}).map(([key, val]: [string, any]) => (
                  <div key={key} style={{ textAlign: "center", padding: "10px 6px", background: theme.bgPanel, borderRadius: 6, border: `1px solid ${theme.borderSubtle}` }}>
                    <span style={{ display: "block", fontSize: 10, fontWeight: 500, color: theme.textMuted, textTransform: "uppercase", marginBottom: 4 }}>{key}</span>
                    <span style={{ display: "block", fontSize: 18, fontWeight: 600, color: theme.text, letterSpacing: "2px" }}>{val.stem}{val.branch}</span>
                  </div>
                ))}
              </div>
              {result.yongshen && (
                <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                  <div style={{ background: "rgba(45,157,111,0.12)", border: "1px solid rgba(45,157,111,0.2)", borderRadius: 6, padding: "8px 14px" }}>
                    <span style={{ display: "block", fontSize: 10, fontWeight: 600, color: "#2d9d6f", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 2 }}>喜用神</span>
                    <span style={{ fontSize: 14, fontWeight: 500, color: theme.text }}>{result.yongshen.favorable?.join(" · ") || "—"}</span>
                  </div>
                  <div style={{ background: "rgba(184,74,74,0.12)", border: "1px solid rgba(184,74,74,0.2)", borderRadius: 6, padding: "8px 14px" }}>
                    <span style={{ display: "block", fontSize: 10, fontWeight: 600, color: "#b84a4a", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 2 }}>忌神</span>
                    <span style={{ fontSize: 14, fontWeight: 500, color: theme.text }}>{result.yongshen.avoid?.join(" · ") || "—"}</span>
                  </div>
                </div>
              )}
              <p style={{ margin: "16px 0 0", fontSize: 10, color: theme.textSubtle, wordBreak: "break-all" }}>ID: {result.id}</p>
            </>
          )}
        </div>
      )}

      {/* Back */}
      <div style={{ textAlign: "center", padding: "24px 20px 0" }}>
        <a href="/" style={{ fontSize: 13, fontWeight: 500, color: theme.gold, textDecoration: "none", letterSpacing: "0.5px" }}>← Zurück zum Heute</a>
      </div>
    </main>
  );
}

const labelStyle: React.CSSProperties = {
  display: "block",
  fontSize: 12,
  fontWeight: 500,
  color: "#8a8f98",
  marginBottom: 6,
  letterSpacing: "0.3px",
};

const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "10px 14px",
  background: "#0f1011",
  color: "#f7f8f8",
  border: "1px solid rgba(255,255,255,0.08)",
  borderRadius: 8,
  fontSize: 15,
  fontWeight: 400,
  boxSizing: "border-box",
  outline: "none",
  fontFamily: "'Inter', system-ui, sans-serif",
};

const buttonStyle: React.CSSProperties = {
  padding: "12px 20px",
  background: "#c9a84c",
  color: "#08090a",
  border: "none",
  borderRadius: 8,
  fontSize: 15,
  fontWeight: 600,
  letterSpacing: "0.3px",
  cursor: "pointer",
  transition: "opacity 0.2s",
};