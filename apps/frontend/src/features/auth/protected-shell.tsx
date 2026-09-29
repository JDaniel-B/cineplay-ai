"use client";

import { useAuth } from "@/features/auth/auth-context";
import { BarChart3, Bot, Clock3, Film, Gamepad2, LogOut, Menu, Users, X } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ReactNode, useEffect, useState } from "react";

const common = [
  ["/chat", "Asistente", Bot],
  ["/historial", "Historial", Clock3],
  ["/consumo", "Consumo", BarChart3],
] as const;
const admin = [
  ["/admin/usuarios", "Usuarios", Users],
  ["/admin/peliculas", "Películas", Film],
  ["/admin/videojuegos", "Videojuegos", Gamepad2],
] as const;

export function ProtectedShell({ children }: { children: ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const path = usePathname();
  const [open, setOpen] = useState(false);
  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);
  if (loading || !user) return <main className="center-screen">Verificando sesión…</main>;

  const links = user.rol === "admin" ? [...common, ...admin] : common;
  return (
    <div className="app-shell">
      <aside className={open ? "sidebar open" : "sidebar"}>
        <div className="brand">
          <span className="brand-mark"><Film /></span>
          <div><strong>CinePlay AI</strong><small>Tu catálogo inteligente</small></div>
          <button className="icon-button mobile-only" onClick={() => setOpen(false)} aria-label="Cerrar menú"><X /></button>
        </div>
        <nav aria-label="Navegación principal">
          <p className="nav-label">Mi espacio</p>
          {links.map(([href, label, Icon], index) => (
            <div key={href}>
              {index === common.length && <p className="nav-label admin-label">Administración</p>}
              <Link className={path === href ? "nav-link active" : "nav-link"} href={href} onClick={() => setOpen(false)}>
                <Icon /> {label}
              </Link>
            </div>
          ))}
        </nav>
        <div className="sidebar-user">
          <span className="avatar">{user.nombre.slice(0, 2).toUpperCase()}</span>
          <div><strong>{user.nombre}</strong><small>{user.rol}</small></div>
        </div>
      </aside>
      <div className="content-shell">
        <header className="topbar">
          <button className="icon-button mobile-only" onClick={() => setOpen(true)} aria-label="Abrir menú"><Menu /></button>
          <span className="topbar-title">CinePlay AI</span>
          <button className="button ghost" onClick={() => void logout().then(() => router.replace("/login"))}>
            <LogOut /> <span>Cerrar sesión</span>
          </button>
        </header>
        <main className="page-container">{children}</main>
      </div>
      {open && <button className="backdrop" aria-label="Cerrar menú" onClick={() => setOpen(false)} />}
    </div>
  );
}
