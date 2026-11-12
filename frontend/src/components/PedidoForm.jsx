import { useState } from "react";
import { estados, etiquetas, moneda } from "../services/api";

export default function PedidoForm({ pedido, busy, onSave, onCancel }) {
  const [form, setForm] = useState({
    cliente: pedido?.cliente || "",
    producto: pedido?.producto || "",
    cantidad: pedido?.cantidad || 1,
    precio_unitario: pedido?.precio_unitario || "",
    estado: pedido?.estado || "pendiente",
  });

  const change = (event) => {
    setForm({ ...form, [event.target.name]: event.target.value });
  };

  const submit = (event) => {
    event.preventDefault();

    const body = {
      cliente: form.cliente.trim(),
      producto: form.producto.trim(),
      cantidad: Number(form.cantidad),
      precio_unitario: String(form.precio_unitario),
    };

    if (pedido) {
      body.estado = form.estado;
      body.version = pedido.version;
    }

    onSave(body);
  };

  const actual = estados.indexOf(pedido?.estado || "pendiente");

  return (
    <section className="panel form-panel">
      <div className="section-heading">
        <span className="eyebrow">{pedido ? "ACTUALIZAR" : "REGISTRO"}</span>
        <h2>{pedido ? `Editar pedido #${pedido.id}` : "Nuevo pedido"}</h2>
        <p>Registra los datos de la compra.</p>
      </div>

      <form onSubmit={submit}>
        <fieldset disabled={busy}>
          <label>
            Cliente
            <input
              name="cliente"
              value={form.cliente}
              onChange={change}
              placeholder="Nombre del cliente"
              minLength={2}
              maxLength={100}
              required
            />
          </label>

          <label>
            Producto
            <input
              name="producto"
              value={form.producto}
              onChange={change}
              placeholder="Nombre del producto"
              minLength={2}
              maxLength={150}
              required
            />
          </label>

          <div className="two-columns">
            <label>
              Cantidad
              <input
                name="cantidad"
                type="number"
                value={form.cantidad}
                onChange={change}
                min="1"
                max="100000"
                step="1"
                required
              />
            </label>

            <label>
              Precio unitario
              <input
                name="precio_unitario"
                type="number"
                value={form.precio_unitario}
                onChange={change}
                min="0.01"
                max="9999999999.99"
                step="0.01"
                required
              />
            </label>
          </div>

          {pedido && (
            <label>
              Estado
              <select name="estado" value={form.estado} onChange={change}>
                {estados
                  .filter((_, index) => index === actual || index === actual + 1)
                  .map((estado) => (
                    <option key={estado} value={estado}>
                      {etiquetas[estado]}
                    </option>
                  ))}
              </select>
            </label>
          )}

          <div className="total">
            <span>Total del pedido</span>
            <strong>
              {moneda(Number(form.cantidad) * Number(form.precio_unitario))}
            </strong>
          </div>

          <button className="primary full" type="submit">
            {busy ? "Guardando..." : pedido ? "Guardar cambios" : "Crear pedido"}
          </button>

          {pedido && (
            <button type="button" className="secondary full" onClick={onCancel}>
              Cancelar edición
            </button>
          )}
        </fieldset>
      </form>
    </section>
  );
}
