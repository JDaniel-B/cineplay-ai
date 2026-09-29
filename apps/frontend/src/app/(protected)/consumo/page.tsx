"use client";

import { api } from "@/shared/api";
import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type Summary = { items: Array<{ categoria: string; tokens: number }>; total: number; desde: string | null; hasta: string | null };

export default function ConsumptionPage() {
  const [data, setData] = useState<Summary | null>(null);
  const [desde, setDesde] = useState(""); const [hasta, setHasta] = useState(""); const [error, setError] = useState("");
  useEffect(() => { const params = new URLSearchParams(); if (desde) params.set("desde", desde); if (hasta) params.set("hasta", hasta); api<Summary>(`/consumo/resumen?${params}`).then(setData).catch((e: Error) => setError(e.message)); }, [desde, hasta]);
  const chart = data?.items.map((item) => ({ categoria: item.categoria === "peliculas" ? "Películas" : "Videojuegos", palabras: item.tokens })) ?? [];
  return <><header className="page-heading"><span className="eyebrow">Métrica académica</span><h1>Consumo por categoría</h1><p className="muted">Una palabra procesada equivale a un token académico; no representa facturación de Groq.</p></header><div className="toolbar panel"><div className="field-group"><label htmlFor="desde">Desde</label><input className="field" id="desde" type="date" value={desde} onChange={(e) => setDesde(e.target.value)} /></div><div className="field-group"><label htmlFor="hasta">Hasta</label><input className="field" id="hasta" type="date" value={hasta} onChange={(e) => setHasta(e.target.value)} /></div><button className="button secondary" onClick={() => { setDesde(""); setHasta(""); }}>Limpiar</button></div>{error && <p className="error-banner">{error}</p>}<div className="chart-grid"><section className="panel" style={{ height: 360 }}><h2>Palabras procesadas</h2>{data && <ResponsiveContainer width="100%" height="90%"><BarChart data={chart} margin={{ top: 25, right: 20, left: 0, bottom: 5 }}><CartesianGrid stroke="#302e40" vertical={false} /><XAxis dataKey="categoria" stroke="#9c9bae" /><YAxis stroke="#9c9bae" allowDecimals={false} /><Tooltip contentStyle={{ background: "#171621", border: "1px solid #302e40", borderRadius: 10 }} /><Bar dataKey="palabras" fill="#8b5cf6" radius={[8, 8, 0, 0]} /></BarChart></ResponsiveContainer>}</section><aside className="panel stat-card"><span className="eyebrow">Total</span><strong className="stat-number">{data?.total ?? "—"}</strong><span className="muted">palabras procesadas</span></aside></div></>;
}
