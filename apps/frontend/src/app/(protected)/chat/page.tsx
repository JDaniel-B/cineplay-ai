"use client";

import { api } from "@/shared/api";
import { zodResolver } from "@hookform/resolvers/zod";
import { Bot, Film, Gamepad2, Send, Sparkles } from "lucide-react";
import { useState } from "react";
import { useForm, useWatch } from "react-hook-form";
import { z } from "zod";

const schema = z.object({
  categoria: z.enum(["peliculas", "videojuegos", "ambas"]),
  pregunta: z.string().trim().min(3, "Escribe una pregunta más específica").max(500),
});
type Values = z.infer<typeof schema>;
type Result = { respuesta: string; fuentes: Record<string, Array<Record<string, unknown>>>; id_conversacion: number; consumo_palabras: number };

const suggestions = [
  "¿Cuáles son 3 películas de drama?",
  "¿Cuáles son 2 videojuegos de aventura?",
  "¿Qué juegos de disparos tienen una calificación mayor a 8.5?",
];

export default function ChatPage() {
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState("");
  const { register, handleSubmit, setValue, control, formState: { errors, isSubmitting } } = useForm<Values>({
    resolver: zodResolver(schema), defaultValues: { categoria: "peliculas", pregunta: "" },
  });
  const question = useWatch({ control, name: "pregunta" });
  async function submit(values: Values) {
    setError(""); setResult(null);
    try { setResult(await api<Result>("/chat/preguntar", { method: "POST", body: JSON.stringify(values) })); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "No fue posible consultar el catálogo"); }
  }
  return (
    <>
      <header className="page-heading"><span className="eyebrow">Asistente inteligente</span><h1>¿Qué quieres descubrir?</h1><p className="muted">Cada pregunta consulta el catálogo desde cero y usa solamente resultados reales.</p></header>
      <div className="chat-layout">
        <section className="panel">
          <form onSubmit={handleSubmit(submit)} noValidate>
            <div className="category-picker" aria-label="Categoría">
              <label className="category-option"><input type="radio" value="peliculas" {...register("categoria")} /><span><Film /> Películas</span></label>
              <label className="category-option"><input type="radio" value="videojuegos" {...register("categoria")} /><span><Gamepad2 /> Videojuegos</span></label>
              <label className="category-option"><input type="radio" value="ambas" {...register("categoria")} /><span><Sparkles /> Ambas</span></label>
            </div>
            <div className="field-group"><label htmlFor="pregunta">Tu pregunta</label><textarea id="pregunta" className="field" placeholder="Ejemplo: ¿Qué juegos de disparos tienen calificación mayor a 8.5?" {...register("pregunta")} />{errors.pregunta && <span className="field-error">{errors.pregunta.message}</span>}</div>
            {error && <p className="error-banner" role="alert">{error}</p>}
            <div className="form-actions"><span className="muted" style={{ marginRight: "auto", fontSize: 11 }}>{question.length}/500</span><button className="button" disabled={isSubmitting}>{isSubmitting ? "Consultando…" : <><Send /> Preguntar</>}</button></div>
          </form>
          {result && <article className="chat-answer" aria-live="polite"><div className="answer-label"><Bot /> Respuesta de CinePlay</div><p>{result.respuesta}</p><small className="muted">Consulta #{result.id_conversacion} · {result.consumo_palabras} palabras procesadas</small></article>}
        </section>
        <aside className="panel">
          <h2>Prueba una pregunta</h2><p className="muted" style={{ fontSize: 12 }}>Selecciona la categoría adecuada y usa uno de estos ejemplos.</p>
          <div className="suggestions">{suggestions.map((text) => <button type="button" className="suggestion" key={text} onClick={() => setValue("pregunta", text)}>{text}</button>)}</div>
          {result && <div className="source-list"><h2 style={{ marginTop: 16 }}>Fuentes consultadas</h2>{Object.entries(result.fuentes).flatMap(([category, rows]) => rows.map((row, index) => <div className="source-card" key={`${category}-${index}`}><strong>{String(row.titulo)}</strong><span className="muted">{category} · {String(row.plataforma)} · {String(row.calificacion)}</span></div>))}</div>}
        </aside>
      </div>
    </>
  );
}
