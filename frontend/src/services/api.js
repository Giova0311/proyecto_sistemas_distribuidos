export const estados = [
  "pendiente", "en_proceso", "enviado", "entregado",
];

export const etiquetas = {
  pendiente: "Pendiente",
  en_proceso: "En proceso",
  enviado: "Enviado",
  entregado: "Entregado",
};

export const moneda = (valor) =>
  new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 2,
  }).format(Number(valor));

export async function api(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 20000);

  try {
    const response = await fetch(`/api${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    const text = await response.text();
    let data = null;
    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      data = null;
    }

    if (!response.ok) {
      const detail = data?.detail;
      const message = Array.isArray(detail)
        ? detail.map((item) => item.msg).join(". ")
        : detail;

      throw new Error(
        message || `Servicio no disponible (HTTP ${response.status}).`
      );
    }

    return {
      data,
      node: response.headers.get("X-Node-ID"),
    };
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error(
        "La solicitud tardó demasiado. Recarga para comprobar el resultado; " +
        "si estabas creando un pedido, puedes reintentar con los mismos datos."
      );
    }
    throw error;
  } finally {
    clearTimeout(timer);
  }
}
