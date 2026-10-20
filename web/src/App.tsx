import { HashRouter, Route, Routes } from "react-router";
import { Shell } from "./components/Shell/Shell";
import { Placeholder } from "./screens/Placeholder";
import { routes } from "./routes";

// Hash routing: the server serves static files only, so deep links cannot use the history API.
export function App() {
  return (
    <HashRouter>
      <Routes>
        <Route element={<Shell />}>
          {routes.map((r) => (
            <Route key={r.path} path={r.path} element={<Placeholder route={r} />} />
          ))}
        </Route>
      </Routes>
    </HashRouter>
  );
}
