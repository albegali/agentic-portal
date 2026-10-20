import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./styles/base.css";
import { App } from "./App";
import { captureToken } from "./api/token";

// Read and strip the launch token before the router mounts (AP0102).
captureToken();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
