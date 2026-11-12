import { etiquetas, moneda } from "../services/api";

export default function PedidoTable({ items, busy, onEdit, onDelete }) {
  if (!items.length) {
    return (
      <div className="empty">
        <div className="empty-icon">＋</div>
        <h3>No hay pedidos para mostrar</h3>
        <p>Crea un pedido o modifica los filtros de búsqueda.</p>
      </div>
    );
  }

  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Pedido / cliente</th>
            <th>Producto</th>
            <th>Total</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {items.map((pedido) => (
            <tr key={pedido.id}>
              <td>
                <strong>#{pedido.id} · {pedido.cliente}</strong>
                <small>Versión {pedido.version}</small>
              </td>
              <td>
                {pedido.producto}
                <small>{pedido.cantidad} × {moneda(pedido.precio_unitario)}</small>
              </td>
              <td className="money">{moneda(pedido.total)}</td>
              <td>
                <span className={`badge ${pedido.estado}`}>
                  {etiquetas[pedido.estado]}
                </span>
              </td>
              <td>
                <div className="actions">
                  <button
                    disabled={busy}
                    onClick={() => onEdit(pedido)}
                    aria-label={`Editar pedido ${pedido.id}`}
                  >
                    Editar
                  </button>
                  <button
                    disabled={busy}
                    className="danger"
                    onClick={() => onDelete(pedido)}
                    aria-label={`Eliminar pedido ${pedido.id}`}
                  >
                    Eliminar
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
