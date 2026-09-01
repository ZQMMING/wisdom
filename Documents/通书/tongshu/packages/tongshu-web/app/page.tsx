"use client";
import { useState, useEffect } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type DailyData = {
  date: string;
  lunar: string;
  ganzhi: { year: string; month: string; day: string };
  solar_term: string | null;
  moduls: {
    id: string;
    title_de: string;
    title_zh: string;
    content_de: string;
    content_zh: string;
    [key: string]: any;
  }[];
  personal?: {
    match: string;
    match_zh: string;
    advice_de: string;
    advice_zh: string;
  };
  disclaimer: string;
};

export default function Home() {
  const [data, setData] = useState<DailyData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API}/daily`)
      .then((r) => r.json())
      .then((d) => {
        setData(d);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <LoadingScreen />;
  if (error) return <ErrorScreen message={error} />;
  if (!data) return null;

  const hexagram = data.moduls.find((m) => m.id === "hexagram");
  const rhythm = data.moduls.find((m) => m.id === "rhythm");
  const health = data.moduls.find((m) => m.id === "health");
  const quote = data.moduls.find((m) => m.id === "quote");
  const yiji = data.moduls.find((m) => m.id === "yiji");

  return (
    <main style={styles.main}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerTop}>
          <span style={styles.logo}>TONGSHU</span>
          <div style={styles.headerRight}>
            <span style={styles.dateLabel}>{data.date}</span>
            {data.solar_term && (
              <span style={styles.termBadge}>{data.solar_term}</span>
            )}
          </div>
        </div>
        <div style={styles.headerDivider} />
        <div style={styles.headerBottom}>
          <span style={styles.lunarLabel}>{data.lunar}</span>
          <span style={styles.ganzhiLabel}>{data.ganzhi.day}</span>
        </div>
      </header>

      {/* Personalization */}
      {data.personal && (
        <section style={{
          ...styles.personalSection,
          borderLeft: `3px solid ${data.personal.match === "harmonious" ? "#2d9d6f" : data.personal.match === "clashing" ? "#b84a4a" : "#c9a84c"}`,
        }}>
          <div style={styles.personalDot} />
          <p style={styles.personalAdvice}>{data.personal.advice_de}</p>
        </section>
      )}

      {/* Hexagram Hero */}
      {hexagram && (
        <section style={styles.hexagramSection}>
          <div style={styles.hexagramLabel}>HEUTE</div>
          <h2 style={styles.hexagramTitle}>{hexagram.title_de}</h2>
          <p style={styles.hexagramSub}>{hexagram.title_zh}</p>
          <div style={styles.hexagramDivider} />
          <p style={styles.hexagramContent}>{hexagram.content_de}</p>
          {hexagram.content_zh && (
            <p style={styles.hexagramZh}>{hexagram.content_zh}</p>
          )}
        </section>
      )}

      {/* Content Grid */}
      <div style={styles.contentGrid}>
        {/* Rhythm — left column */}
        {rhythm && (
          <div style={styles.cardWide}>
            <div style={styles.cardHeader}>
              <span style={styles.cardIcon}>◷</span>
              <h3 style={styles.cardTitle}>{rhythm.title_de}</h3>
            </div>
            <p style={styles.cardBody}>{rhythm.content_de}</p>
            <div style={styles.rhythmGrid}>
              <div style={styles.rhythmItem}>
                <span style={styles.rhythmEmoji}>☀️</span>
                <div>
                  <span style={styles.rhythmLabel}>Vormittag</span>
                  <span style={styles.rhythmValue}>{rhythm.morning_de?.split(": ")[1] || "—"}</span>
                </div>
              </div>
              <div style={styles.rhythmItem}>
                <span style={styles.rhythmEmoji}>🌤</span>
                <div>
                  <span style={styles.rhythmLabel}>Nachmittag</span>
                  <span style={styles.rhythmValue}>{rhythm.afternoon_de?.split(": ")[1] || "—"}</span>
                </div>
              </div>
              <div style={styles.rhythmItem}>
                <span style={styles.rhythmEmoji}>🌙</span>
                <div>
                  <span style={styles.rhythmLabel}>Abend</span>
                  <span style={styles.rhythmValue}>{rhythm.evening_de?.split(": ")[1] || "—"}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Health — right column */}
        {health && (
          <div style={styles.cardNarrow}>
            <div style={styles.cardHeader}>
              <span style={styles.cardIcon}>🪷</span>
              <h3 style={styles.cardTitle}>{health.title_de}</h3>
            </div>
            <p style={styles.cardBody}>{health.content_de}</p>
          </div>
        )}

        {/* Quote — full width */}
        {quote && (
          <div style={styles.cardWide}>
            <div style={styles.cardHeader}>
              <span style={styles.cardIcon}>「</span>
              <h3 style={styles.cardTitle}>{quote.title_de}</h3>
            </div>
            <p style={styles.quoteText}>{quote.content_de}</p>
            {quote.author && (
              <p style={styles.quoteAuthor}>— {quote.author}</p>
            )}
          </div>
        )}

        {/* YiJi — full width */}
        {yiji && (
          <div style={styles.cardWide}>
            <div style={styles.cardHeader}>
              <span style={styles.cardIcon}>⚖</span>
              <h3 style={styles.cardTitle}>{yiji.title_de}</h3>
            </div>
            <div style={styles.yijiGrid}>
              {yiji.yi_zh && yiji.yi_zh.length > 0 && (
                <div>
                  <span style={styles.yijiLabel}>Günstig</span>
                  <div style={styles.yijiTags}>
                    {yiji.yi_zh.map((y: string, i: number) => (
                      <span key={i} style={styles.yijiTagGreen}>{y}</span>
                    ))}
                  </div>
                </div>
              )}
              {yiji.ji_zh && yiji.ji_zh.length > 0 && (
                <div>
                  <span style={styles.yijiLabel}>Weniger</span>
                  <div style={styles.yijiTags}>
                    {yiji.ji_zh.map((j: string, i: number) => (
                      <span key={i} style={styles.yijiTagRed}>{j}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer style={styles.footer}>
        <nav style={styles.nav}>
          <a href="/" style={styles.navLinkActive}>Heute</a>
          <a href="/profile" style={styles.navLink}>Profil</a>
        </nav>
        <p style={styles.disclaimer}>{data.disclaimer}</p>
      </footer>
    </main>
  );
}

function LoadingScreen() {
  return (
    <div style={styles.loadingContainer}>
      <div style={styles.loadingSpinner} />
      <p style={styles.loadingText}>Lade TONGSHU</p>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

function ErrorScreen({ message }: { message: string }) {
  return (
    <div style={styles.loadingContainer}>
      <p style={{ fontSize: 40, margin: 0, opacity: 0.2 }}>🪷</p>
      <h2 style={{ margin: "16px 0 8px", fontWeight: 500, fontSize: 20, color: "#f7f8f8" }}>Keine Verbindung</h2>
      <p style={{ margin: 0, fontSize: 14, color: "#8a8f98", textAlign: "center" }}>{message}</p>
      <button onClick={() => window.location.reload()} style={styles.retryButton}>Erneut versuchen</button>
    </div>
  );
}

// ============================================================
// Design Tokens
// ============================================================
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
  goldDark: "#a68a2e",
  border: "rgba(255,255,255,0.08)",
  borderSubtle: "rgba(255,255,255,0.05)",
  green: "#2d9d6f",
  red: "#b84a4a",
  font: "'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
};

// ============================================================
// Styles
// ============================================================
const styles: Record<string, React.CSSProperties> = {
  main: {
    maxWidth: 480,
    margin: "0 auto",
    padding: "0 0 80px",
    minHeight: "100vh",
    background: theme.bg,
  },

  // Header
  header: {
    padding: "24px 20px 16px",
    background: theme.bgPanel,
    borderBottom: `1px solid ${theme.border}`,
  },
  headerTop: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  logo: {
    fontSize: 18,
    fontWeight: 600,
    letterSpacing: 3,
    color: theme.gold,
  },
  headerRight: {
    display: "flex",
    alignItems: "center",
    gap: 8,
  },
  dateLabel: {
    fontSize: 13,
    fontWeight: 500,
    color: theme.textSecondary,
    fontFeatureSettings: "'tnum'",
  },
  termBadge: {
    fontSize: 11,
    fontWeight: 500,
    color: theme.gold,
    background: `${theme.gold}15`,
    padding: "2px 8px",
    borderRadius: 4,
    border: `1px solid ${theme.gold}30`,
  },
  headerDivider: {
    height: "1px",
    background: theme.border,
    margin: "12px 0",
  },
  headerBottom: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  lunarLabel: {
    fontSize: 13,
    fontWeight: 400,
    color: theme.textMuted,
  },
  ganzhiLabel: {
    fontSize: 13,
    fontWeight: 500,
    color: theme.textSecondary,
    fontFeatureSettings: "'tnum'",
  },

  // Personal
  personalSection: {
    margin: "16px 20px 0",
    padding: "14px 16px",
    background: theme.bgSurface,
    borderRadius: 8,
    display: "flex",
    alignItems: "flex-start",
    gap: 10,
  },
  personalDot: {
    width: 8,
    height: 8,
    borderRadius: "50%",
    background: theme.gold,
    marginTop: 6,
    flexShrink: 0,
  },
  personalAdvice: {
    margin: 0,
    fontSize: 14,
    lineHeight: 1.55,
    color: theme.textSecondary,
    fontWeight: 400,
  },

  // Hexagram
  hexagramSection: {
    margin: "16px 20px 0",
    padding: "28px 24px",
    background: `linear-gradient(135deg, ${theme.bgSurface} 0%, ${theme.bg} 100%)`,
    borderRadius: 12,
    border: `1px solid ${theme.border}`,
    position: "relative" as const,
    overflow: "hidden",
  },
  hexagramLabel: {
    fontSize: 10,
    fontWeight: 600,
    letterSpacing: 2,
    color: theme.gold,
    textTransform: "uppercase" as const,
    marginBottom: 8,
  },
  hexagramTitle: {
    margin: 0,
    fontSize: 26,
    fontWeight: 510,
    letterSpacing: "-0.5px",
    lineHeight: 1.15,
    color: theme.text,
  },
  hexagramSub: {
    margin: "4px 0 0",
    fontSize: 14,
    fontWeight: 400,
    color: theme.textMuted,
  },
  hexagramDivider: {
    height: "1px",
    background: theme.border,
    margin: "16px 0",
  },
  hexagramContent: {
    margin: 0,
    fontSize: 15,
    lineHeight: 1.6,
    color: theme.textSecondary,
    fontWeight: 400,
  },
  hexagramZh: {
    margin: "12px 0 0",
    fontSize: 13,
    lineHeight: 1.5,
    color: `${theme.gold}cc`,
    fontStyle: "italic",
  },

  // Content Grid
  contentGrid: {
    display: "flex",
    flexDirection: "column" as const,
    gap: 12,
    padding: "16px 20px 0",
  },

  // Cards
  cardWide: {
    background: theme.bgPanel,
    borderRadius: 10,
    padding: "18px 20px",
    border: `1px solid ${theme.border}`,
  },
  cardNarrow: {
    background: theme.bgPanel,
    borderRadius: 10,
    padding: "18px 20px",
    border: `1px solid ${theme.border}`,
  },
  cardHeader: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    marginBottom: 12,
  },
  cardIcon: {
    fontSize: 16,
    color: theme.gold,
    opacity: 0.8,
  },
  cardTitle: {
    margin: 0,
    fontSize: 14,
    fontWeight: 600,
    color: theme.text,
    letterSpacing: "0.3px",
  },
  cardBody: {
    margin: 0,
    fontSize: 14,
    lineHeight: 1.6,
    color: theme.textSecondary,
    fontWeight: 400,
  },

  // Rhythm
  rhythmGrid: {
    display: "flex",
    flexDirection: "column" as const,
    gap: 8,
    marginTop: 14,
    paddingTop: 14,
    borderTop: `1px solid ${theme.borderSubtle}`,
  },
  rhythmItem: {
    display: "flex",
    alignItems: "center",
    gap: 10,
  },
  rhythmEmoji: {
    fontSize: 16,
    width: 24,
    textAlign: "center" as const,
  },
  rhythmLabel: {
    fontSize: 12,
    fontWeight: 500,
    color: theme.textMuted,
    display: "block",
  },
  rhythmValue: {
    fontSize: 14,
    fontWeight: 500,
    color: theme.textSecondary,
    display: "block",
    marginTop: 1,
  },

  // Quote
  quoteText: {
    margin: 0,
    fontSize: 16,
    lineHeight: 1.65,
    color: theme.text,
    fontWeight: 400,
    fontStyle: "italic",
  },
  quoteAuthor: {
    margin: "8px 0 0",
    fontSize: 13,
    color: theme.textMuted,
    fontWeight: 400,
  },

  // YiJi
  yijiGrid: {
    display: "flex",
    flexDirection: "column" as const,
    gap: 12,
  },
  yijiLabel: {
    fontSize: 11,
    fontWeight: 600,
    color: theme.textMuted,
    textTransform: "uppercase" as const,
    letterSpacing: "0.5px",
    display: "block",
    marginBottom: 6,
  },
  yijiTags: {
    display: "flex",
    flexWrap: "wrap" as const,
    gap: 6,
  },
  yijiTagGreen: {
    fontSize: 12,
    fontWeight: 500,
    color: "#2d9d6f",
    background: "rgba(45,157,111,0.12)",
    padding: "3px 10px",
    borderRadius: 6,
    border: "1px solid rgba(45,157,111,0.2)",
  },
  yijiTagRed: {
    fontSize: 12,
    fontWeight: 500,
    color: "#b84a4a",
    background: "rgba(184,74,74,0.12)",
    padding: "3px 10px",
    borderRadius: 6,
    border: "1px solid rgba(184,74,74,0.2)",
  },

  // Loading
  loadingContainer: {
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    justifyContent: "center",
    minHeight: "100vh",
    background: theme.bg,
    padding: 20,
  },
  loadingSpinner: {
    width: 36,
    height: 36,
    border: "2px solid rgba(255,255,255,0.08)",
    borderTop: `2px solid ${theme.gold}`,
    borderRadius: "50%",
    animation: "spin 1s linear infinite",
  },
  loadingText: {
    marginTop: 16,
    fontSize: 14,
    color: theme.textMuted,
    letterSpacing: "1px",
  },

  // Error
  retryButton: {
    marginTop: 20,
    padding: "10px 28px",
    background: theme.bgElevated,
    color: theme.text,
    border: `1px solid ${theme.border}`,
    borderRadius: 8,
    fontSize: 14,
    fontWeight: 500,
    cursor: "pointer",
  },

  // Footer
  footer: {
    textAlign: "center" as const,
    padding: "24px 20px 32px",
  },
  nav: {
    display: "flex",
    gap: 24,
    justifyContent: "center",
    marginBottom: 16,
  },
  navLink: {
    fontSize: 13,
    fontWeight: 500,
    color: theme.textMuted,
    textDecoration: "none",
    letterSpacing: "0.5px",
  },
  navLinkActive: {
    fontSize: 13,
    fontWeight: 600,
    color: theme.gold,
    textDecoration: "none",
    letterSpacing: "0.5px",
  },
  disclaimer: {
    fontSize: 11,
    lineHeight: 1.5,
    color: theme.textSubtle,
    margin: 0,
  },
};