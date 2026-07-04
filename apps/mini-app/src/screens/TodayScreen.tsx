import { useEffect, useState } from "react";

import { getHealth } from "../api/client";
import { StatusPill } from "../components/StatusPill";

export function TodayScreen() {
  const [apiStatus, setApiStatus] = useState<"checking" | "ok" | "offline">("checking");

  useEffect(() => {
    let isMounted = true;

    getHealth()
      .then(() => {
        if (isMounted) {
          setApiStatus("ok");
        }
      })
      .catch(() => {
        if (isMounted) {
          setApiStatus("offline");
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <main className="app-shell">
      <section className="today-panel" aria-labelledby="today-title">
        <div className="top-row">
          <span className="day-label">Сегодня</span>
          <StatusPill
            label={apiStatus === "ok" ? "API online" : apiStatus === "checking" ? "Проверка API" : "API offline"}
            tone={apiStatus === "ok" ? "ready" : "pending"}
          />
        </div>

        <h1 id="today-title">Training Agent</h1>
        <p className="focus">Личный трекер тренировок для Telegram Mini App.</p>

        <div className="progress-line" aria-label="Прогресс тренировки">
          <span>Phase 1</span>
          <strong>Скелет приложения</strong>
        </div>

        <div className="actions">
          <button type="button">Начать тренировку</button>
          <button type="button" className="secondary">
            Журнал
          </button>
        </div>
      </section>
    </main>
  );
}
