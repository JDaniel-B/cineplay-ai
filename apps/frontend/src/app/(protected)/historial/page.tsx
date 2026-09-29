"use client";

import { api } from "@/shared/api";
import { Clock3 } from "lucide-react";
import { useEffect, useState } from "react";

type History = { id_conversacion: number; fecha: string; pregunta: string; respuesta: string };
type HistoryPage = { items: History[]; total: number; page: number; page_size: number };

export default function HistoryPageView() {
  const [data, setData] = useState<HistoryPage | null>(null);
  const [page, setPage] = useState(1);
  const [error, setError] = useState("");
  useEffect(() => { api<HistoryPage>(`/historial?page=${page}&page_size=10`).then(setData).catch((e: Error) => setError(e.message)); }, [page]);
  const pages = Math.max(1, Math.ceil((data?.total ?? 0) / 10));
  return <><header className="page-heading"><span className="eyebrow">Tu actividad</span><h1>Historial de consultas</h1><p className="muted">Solo tú puedes ver estas preguntas y respuestas.</p></header><section className="panel">{error && <p className="error-banner">{error}</p>}{!data ? <p className="empty-state">Cargando historial…</p> : data.items.length === 0 ? <div className="empty-state"><Clock3 /><p>Aún no has realizado consultas.</p></div> : <><div className="table-wrap"><table><thead><tr><th>Fecha</th><th>Pregunta</th><th>Respuesta</th></tr></thead><tbody>{data.items.map((item) => <tr key={item.id_conversacion}><td>{new Intl.DateTimeFormat("es-GT", { dateStyle: "medium", timeStyle: "short" }).format(new Date(item.fecha))}</td><td className="history-question">{item.pregunta}</td><td className="history-answer">{item.respuesta}</td></tr>)}</tbody></table></div><div className="pagination"><span>{data.total} consultas</span><div className="actions"><button className="button secondary" disabled={page <= 1} onClick={() => setPage(page - 1)}>Anterior</button><span>Página {page} de {pages}</span><button className="button secondary" disabled={page >= pages} onClick={() => setPage(page + 1)}>Siguiente</button></div></div></>}</section></>;
}
