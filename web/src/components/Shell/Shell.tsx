import { useEffect, useRef, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router";
import { APP_NAME, routes } from "../../routes";
import { ServerStatus } from "./ServerStatus";
import "./Shell.css";

const DRAWER_QUERY = "(max-width: 899px)";

export function Shell() {
  // The drawer is open only on the route where it was opened, so navigating closes it.
  const location = useLocation();
  const [openAt, setOpenAt] = useState<string | null>(null);
  const open = openAt === location.pathname;
  const setOpen = (value: boolean) => setOpenAt(value ? location.pathname : null);
  const mainRef = useRef<HTMLElement>(null);
  const menuRef = useRef<HTMLButtonElement>(null);
  const navRef = useRef<HTMLElement>(null);
  const firstRender = useRef(true);
  const returnFocus = useRef(false);

  const closeToMenu = () => {
    returnFocus.current = true; // applied after render: the header is inert while the drawer is open
    setOpenAt(null);
  };

  useEffect(() => {
    if (!open && returnFocus.current) {
      returnFocus.current = false;
      menuRef.current?.focus();
    }
  }, [open]);

  // Route change: update the title, move focus to the content.
  useEffect(() => {
    const route = routes.find((r) => r.path === location.pathname);
    document.title = route ? `${route.label} — ${APP_NAME}` : APP_NAME;
    if (firstRender.current) firstRender.current = false;
    else mainRef.current?.focus();
  }, [location.pathname]);

  // Drawer: Escape closes and returns focus to the menu button; leaving the drawer layout resets it.
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") closeToMenu();
    };
    const mq = window.matchMedia(DRAWER_QUERY);
    const onChange = () => !mq.matches && setOpenAt(null);
    document.addEventListener("keydown", onKey);
    mq.addEventListener("change", onChange);
    navRef.current?.querySelector<HTMLElement>("a[aria-current='page']")?.focus();
    return () => {
      document.removeEventListener("keydown", onKey);
      mq.removeEventListener("change", onChange);
    };
  }, [open]);

  return (
    <div className="shell">
      <a
        className="skip-link"
        href="#main"
        onClick={(e) => {
          e.preventDefault(); // the hash belongs to the router
          mainRef.current?.focus();
        }}
      >
        Skip to content
      </a>
      <header className="topbar" inert={open}>
        <button
          ref={menuRef}
          type="button"
          className="menu-button"
          aria-expanded={open}
          aria-controls="main-nav"
          onClick={() => setOpen(true)}
        >
          Menu
        </button>
        <span className="brand">{APP_NAME}</span>
      </header>
      <nav id="main-nav" ref={navRef} aria-label="Main" className={open ? "open" : undefined}>
        <div className="brand">
          <span aria-hidden="true" className="brand-mark">
            ◆
          </span>
          {APP_NAME}
        </div>
        <ul>
          {routes.map((r) => (
            <li key={r.path}>
              <NavLink to={r.path} end className="nav-link" onClick={() => setOpenAt(null)}>
                {r.label}
              </NavLink>
            </li>
          ))}
        </ul>
        <ServerStatus />
      </nav>
      <div className="scrim" hidden={!open} onClick={closeToMenu} />
      <main id="main" ref={mainRef} tabIndex={-1} inert={open}>
        <Outlet />
      </main>
    </div>
  );
}
