"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Film, LogIn } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useAuth } from "@/features/auth/auth-context";

const schema = z.object({
  correo: z.email("Ingresa un correo válido"),
  password: z.string().min(8, "La contraseña debe tener al menos 8 caracteres"),
});
type Values = z.infer<typeof schema>;

export default function LoginPage() {
  const { user, login } = useAuth();
  const router = useRouter();
  const [error, setError] = useState("");
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<Values>({ resolver: zodResolver(schema) });
  useEffect(() => { if (user) router.replace("/chat"); }, [user, router]);
  async function submit(values: Values) {
    setError("");
    try { await login(values.correo, values.password); router.replace("/chat"); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "No fue posible iniciar sesión"); }
  }
  return (
    <main className="login-page">
      <section className="login-visual">
        <span className="eyebrow">Películas · Videojuegos · IA</span>
        <h1>Tu próxima historia comienza aquí.</h1>
        <p>Consulta el catálogo con lenguaje natural y descubre títulos respaldados por datos reales.</p>
      </section>
      <section className="login-form-wrap">
        <div className="login-card">
          <div className="brand"><span className="brand-mark"><Film /></span><div><strong>CinePlay AI</strong><small>Acceso privado</small></div></div>
          <span className="eyebrow">Bienvenido</span>
          <h1>Inicia sesión</h1>
          <p className="muted">Usa la cuenta creada por el administrador.</p>
          <form onSubmit={handleSubmit(submit)} noValidate>
            {error && <div className="error-banner" role="alert">{error}</div>}
            <div className="field-group"><label htmlFor="correo">Correo electrónico</label><input id="correo" className="field" autoComplete="email" {...register("correo")} />{errors.correo && <span className="field-error">{errors.correo.message}</span>}</div>
            <div className="field-group"><label htmlFor="password">Contraseña</label><input id="password" className="field" type="password" autoComplete="current-password" {...register("password")} />{errors.password && <span className="field-error">{errors.password.message}</span>}</div>
            <button className="button" disabled={isSubmitting}>{isSubmitting ? "Ingresando…" : <><LogIn /> Ingresar</>}</button>
          </form>
        </div>
      </section>
    </main>
  );
}
