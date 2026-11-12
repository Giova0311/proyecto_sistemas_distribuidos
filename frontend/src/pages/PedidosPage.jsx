import { useCallback, useEffect, useRef, useState } from "react";

import Navbar from "../components/Navbar";
import PedidoForm from "../components/PedidoForm";
import PedidoTable from "../components/PedidoTable";
import { api, estados, etiquetas } from "../services/api";

const KEY = "pedidos-solicitud-pendiente";

export default function PedidosPage() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [pagina, setPagina] = useState(1);
  const [estado, setEstado] = useState("");
  const [buscar, setBuscar] = useState("");
  const [filtro, setFiltro] = useState("");
  const [editing, setEditing] = useState(null);
  const [formKey, setFormKey] = useState(0);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(false);
  const [online, setOnline] = useState(false);
  const [node, setNode] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const generation = useRef(0);

  const load = useCallback(async () => {
    const current = ++generation.current;
    setLoading(true);

    try {
      const params = new URLSearchParams({
        pagina: String(pagina),
        limite: "10",
        buscar: filtro,
      });
      if (estado) params.set("estado", estado);

      const response = await api(`/pedidos?${params}`);

      if (current !== generation.current) return;
      setItems(response.data.items);
      setTotal(response.data.total);
      setNode(response.node);
      setOnline(true);
      setError("");

      if (!response.data.items.length && pagina > 1) {
        setPagina(pagina - 1);
      }
    } catch (err) {
      if (current !== generation.current) return;
      setOnline(false);
      setError(err.message);
    } finally {
      if (current === generation.current) setLoading(false);
    }
  }, [pagina, estado, filtro]);

  useEffect(() => {
    load();
    return () => { generation.current += 1; };
  }, [load]);

  useEffect(() => {
    let alive = true;

    const health = async () => {
      try {
        const response = await api("/health/ready");
        if (alive) {
          setOnline(true);
          setNode(response.node);
        }
      } catch {
        if (alive) setOnline(false);
      }
    };

    const timer = setInterval(health, 10000);
    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, []);

  function cancelEdit() {
    setEditing(null);
    setFormKey((value) => value + 1);
  }

  async function save(body) {
    setBusy(true);
    setError("");
    setMessage("");

    try {
      let response;

      if (editing) {
        response = await api(`/pedidos/${editing.id}`, {
          method: "PUT",
          body: JSON.stringify(body),
        });
      } else {
        const serialized = JSON.stringify(body);
        let pending = null;

        try {
          pending = JSON.parse(localStorage.getItem(KEY));
        } catch {
          pending = null;
        }

        if (!pending || pending.body !== serialized) {
          pending = {
            body: serialized,
            key: crypto.randomUUID(),
          };
          localStorage.setItem(KEY, JSON.stringify(pending));
        }

        response = await api("/pedidos", {
          method: "POST",
          headers: { "Idempotency-Key": pending.key },
          body: serialized,
        });

        localStorage.removeItem(KEY);
      }

      setNode(response.node);
      setMessage(
        editing
          ? "Pedido actualizado."
          : `Pedido #${response.data.id} registrado.`
      );
      cancelEdit();
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function remove(pedido) {
    if (!window.confirm(`¿Eliminar el pedido #${pedido.id}?`)) return;

    setBusy(true);
    setError("");
    setMessage("");

    try {
      await api(`/pedidos/${pedido.id}?version=${pedido.version}`, {
        method: "DELETE",
      });

      if (editing?.id === pedido.id) cancelEdit();
      setMessage("Pedido eliminado.");
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Navbar online={online} node={node} />

      <main>
        <section className="hero">
          <div>
            <span className="eyebrow">GESTIÓN DE PEDIDOS</span>
            <h1>Cada pedido,<br /><span>bajo control.</span></h1>
            <p>Organiza tus ventas y sigue cada entrega desde un solo lugar.</p>
          </div>
          <div className="hero-summary">
            <strong>{total}</strong>
            <span>pedidos encontrados</span>
          </div>
        </section>

        {error && <div className="notice error" role="alert">{error}</div>}
        {message && <div className="notice success" role="status">{message}</div>}

        <div className="workspace">
          <PedidoForm
            key={`${editing?.id || "nuevo"}-${formKey}`}
            pedido={editing}
            busy={busy}
            onSave={save}
            onCancel={cancelEdit}
          />

          <section className="panel orders-panel" aria-busy={loading}>
            <div className="orders-heading">
              <div>
                <span className="eyebrow">SEGUIMIENTO</span>
                <h2>Listado de pedidos</h2>
              </div>
              <button
                className="secondary"
                disabled={loading || busy}
                onClick={load}
              >
                {loading ? "Cargando..." : "Actualizar"}
              </button>
            </div>

            <form
              className="filters"
              onSubmit={(event) => {
                event.preventDefault();
                setPagina(1);
                setFiltro(buscar.trim());
              }}
            >
              <input
                aria-label="Buscar cliente o producto"
                placeholder="Buscar cliente o producto..."
                value={buscar}
                maxLength={100}
                onChange={(event) => setBuscar(event.target.value)}
              />
              <select
                aria-label="Filtrar por estado"
                value={estado}
                onChange={(event) => {
                  setPagina(1);
                  setEstado(event.target.value);
                }}
              >
                <option value="">Todos los estados</option>
                {estados.map((item) => (
                  <option key={item} value={item}>{etiquetas[item]}</option>
                ))}
              </select>
              <button className="primary" type="submit">Buscar</button>
            </form>

            <PedidoTable
              items={items}
              busy={busy || loading}
              onEdit={(pedido) => {
                setEditing(pedido);
                setFormKey((value) => value + 1);
                setMessage("");
                setError("");
              }}
              onDelete={remove}
            />

            <div className="pagination">
              <span>Página {pagina} de {Math.max(1, Math.ceil(total / 10))}</span>
              <div className="actions">
                <button
                  disabled={pagina <= 1 || loading || busy}
                  onClick={() => setPagina((value) => value - 1)}
                >Anterior</button>
                <button
                  disabled={pagina * 10 >= total || loading || busy}
                  onClick={() => setPagina((value) => value + 1)}
                >Siguiente</button>
              </div>
            </div>
          </section>
        </div>
      </main>

      <footer>Proyecto académico · Sistema distribuido de gestión de pedidos</footer>
    </>
  );
}
