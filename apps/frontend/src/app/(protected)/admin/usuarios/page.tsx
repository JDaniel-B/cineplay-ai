import { ResourceManager } from "@/features/admin/resource-manager";

export default function UsersPage() {
  return <ResourceManager title="Usuarios" eyebrow="Administración" endpoint="/admin/usuarios" idKey="id_usuario" initial={{ nombre: "", correo: "", password: "", rol: "usuario" }} fields={[{ key: "nombre", label: "Nombre", required: true }, { key: "correo", label: "Correo", type: "email", required: true }, { key: "password", label: "Contraseña (vacía conserva la actual)", type: "password", required: true }, { key: "rol", label: "Rol", type: "select", options: ["usuario", "admin"], required: true }]} columns={[{ key: "nombre", label: "Nombre" }, { key: "correo", label: "Correo" }, { key: "rol", label: "Rol" }]} />;
}
