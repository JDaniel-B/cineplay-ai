"use client";

import { useAuth } from "@/features/auth/auth-context";
import { api, Page } from "@/shared/api";
import { Pencil, Plus, Search, Trash2, X } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";

type Row = Record<string, unknown>;
type Field = { key: string; label: string; type?: "text" | "email" | "password" | "number" | "select"; options?: string[]; required?: boolean; min?: number; max?: number; step?: string };
type Props = { title: string; eyebrow: string; endpoint: string; idKey: string; fields: Field[]; columns: Array<{ key: string; label: string }>; initial: Record<string, string | number> };
type FormValues = Record<string, string | number>;

export function ResourceManager({ title, eyebrow, endpoint, idKey, fields, columns, initial }: Props) {
  const { user, loading } = useAuth(); const router = useRouter();
  const [data, setData] = useState<Page<Row> | null>(null); const [page, setPage] = useState(1); const [search, setSearch] = useState(""); const [activeSearch, setActiveSearch] = useState(""); const [editing, setEditing] = useState<Row | null>(null); const [showForm, setShowForm] = useState(false); const [error, setError] = useState("");
  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<FormValues>({ defaultValues: initial });
  const url = useMemo(() => `${endpoint}?page=${page}&page_size=10&buscar=${encodeURIComponent(activeSearch)}`, [endpoint, page, activeSearch]);
  function load() { api<Page<Row>>(url).then(setData).catch((e: Error) => setError(e.message)); }
  useEffect(() => { if (!loading && user?.rol !== "admin") router.replace("/chat"); }, [loading, user, router]);
  useEffect(() => { if (user?.rol === "admin") load(); }, [url, user?.rol]); // eslint-disable-line react-hooks/exhaustive-deps
  if (loading || user?.rol !== "admin") return <p className="empty-state">Verificando permisos…</p>;
  function openCreate() { setEditing(null); reset(initial); setShowForm(true); }
  function openEdit(row: Row) { setEditing(row); const values: FormValues = { ...initial }; for (const field of fields) { if (field.type === "password") values[field.key] = ""; else values[field.key] = (row[field.key] as string | number) ?? ""; } reset(values); setShowForm(true); }
  async function save(values: FormValues) {
    setError(""); const payload: FormValues = { ...values }; if (editing && "password" in payload && !payload.password) delete payload.password;
    try { await api(editing ? `${endpoint}/${editing[idKey]}` : endpoint, { method: editing ? "PUT" : "POST", body: JSON.stringify(payload) }); setShowForm(false); load(); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "No fue posible guardar"); }
  }
  async function remove(row: Row) { if (!confirm(`¿Eliminar ${String(row.titulo ?? row.nombre)}? Esta acción no se puede deshacer.`)) return; try { await api(`${endpoint}/${row[idKey]}`, { method: "DELETE" }); load(); } catch (cause) { setError(cause instanceof Error ? cause.message : "No fue posible eliminar"); } }
  const pages = Math.max(1, Math.ceil((data?.total ?? 0) / 10));
  return <><header className="page-heading"><span className="eyebrow">{eyebrow}</span><h1>{title}</h1><p className="muted">Crea, edita, busca y elimina registros del sistema.</p></header>{error && <p className="error-banner" role="alert">{error}</p>}{showForm && <section className="panel" style={{ marginBottom: 20 }}><div className="toolbar"><h2>{editing ? "Editar registro" : "Nuevo registro"}</h2><button className="icon-button" onClick={() => setShowForm(false)} aria-label="Cerrar formulario"><X /></button></div><form className="form-grid" onSubmit={handleSubmit(save)}>{fields.map((field) => <div className="field-group" key={field.key}><label htmlFor={field.key}>{field.label}</label>{field.type === "select" ? <select id={field.key} className="field" {...register(field.key, { required: field.required ? "Este campo es obligatorio" : false })}>{field.options?.map((option) => <option value={option} key={option}>{option}</option>)}</select> : <input id={field.key} className="field" type={field.type ?? "text"} step={field.step} {...register(field.key, { required: field.required && !(editing && field.type === "password") ? "Este campo es obligatorio" : false, min: field.min, max: field.max, valueAsNumber: field.type === "number" })} />}{errors[field.key] && <span className="field-error">{String(errors[field.key]?.message)}</span>}</div>)}<div className="form-actions"><button type="button" className="button secondary" onClick={() => setShowForm(false)}>Cancelar</button><button className="button" disabled={isSubmitting}>{isSubmitting ? "Guardando…" : "Guardar"}</button></div></form></section>}<section className="panel"><div className="toolbar"><form className="field-group" onSubmit={(e) => { e.preventDefault(); setPage(1); setActiveSearch(search); }}><label htmlFor="search">Buscar</label><div style={{ display: "flex", gap: 8 }}><input id="search" className="field" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Título, género, plataforma…" /><button className="button secondary" aria-label="Buscar"><Search /></button></div></form><button className="button" onClick={openCreate}><Plus /> Nuevo</button></div>{!data ? <p className="empty-state">Cargando…</p> : data.items.length === 0 ? <p className="empty-state">No se encontraron registros.</p> : <><div className="table-wrap"><table><thead><tr>{columns.map((column) => <th key={column.key}>{column.label}</th>)}<th>Acciones</th></tr></thead><tbody>{data.items.map((row) => <tr key={String(row[idKey])}>{columns.map((column) => <td key={column.key}>{column.key === "rol" ? <span className="badge">{String(row[column.key])}</span> : String(row[column.key] ?? "—")}</td>)}<td><div className="actions"><button className="button secondary" onClick={() => openEdit(row)} aria-label="Editar"><Pencil /></button><button className="button danger" onClick={() => void remove(row)} aria-label="Eliminar"><Trash2 /></button></div></td></tr>)}</tbody></table></div><div className="pagination"><span>{data.total} registros</span><div className="actions"><button className="button secondary" disabled={page <= 1} onClick={() => setPage(page - 1)}>Anterior</button><span>Página {page} de {pages}</span><button className="button secondary" disabled={page >= pages} onClick={() => setPage(page + 1)}>Siguiente</button></div></div></>}</section></>;
}
