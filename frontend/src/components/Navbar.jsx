export default function Navbar({ online, node }) {
  return (
    <header className="navbar">
      <a className="brand" href="/">
        <span className="brand-icon">P</span>
        <span>Pedidos<span className="brand-light"> / distribuido</span></span>
      </a>
      <div className="connection" role="status">
        <span className={`dot ${online ? "on" : ""}`} />
        {online ? "API disponible" : "Sin conexión confirmada"}
        <small>{node || "Esperando respuesta"}</small>
      </div>
    </header>
  );
}
