import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "./api";

describe("api", () => {
  afterEach(() => vi.unstubAllGlobals());
  it("envía cookies en las solicitudes", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ status: "ok" }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    await api("/health");
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/health"), expect.objectContaining({ credentials: "include" }));
  });
  it("convierte errores del API en ApiError", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: "Sin permiso" }), { status: 403 })));
    await expect(api("/admin/usuarios")).rejects.toEqual(expect.objectContaining({ message: "Sin permiso", status: 403 }));
  });
});
