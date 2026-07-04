import type { WorkoutHistory } from "../types/workouts";

type HistoryScreenProps = {
  history: WorkoutHistory;
  onBack: () => void;
};

export function HistoryScreen({ history, onBack }: HistoryScreenProps) {
  return (
    <section className="screen history-screen" aria-labelledby="history-title">
      <div className="top-row">
        <h1 id="history-title">Журнал</h1>
        <button type="button" className="secondary" onClick={onBack}>
          Сегодня
        </button>
      </div>
      <div className="history-list">
        {history.sessions.map((entry) => (
          <article className="history-item" key={entry.session.id ?? entry.session.date}>
            <h2>{entry.session.title}</h2>
            <p>{entry.session.date} · {entry.session.status}</p>
            {entry.exercises.map((exercise) => (
              <details key={exercise.id}>
                <summary>{exercise.slot_name} · {exercise.status}</summary>
                {exercise.sets.map((set) => (
                  <div className="set-row" key={set.id}>
                    <span>#{set.set_index}</span>
                    <strong>{set.weight ?? "-"} кг × {set.reps ?? "-"}</strong>
                    <span>RPE {set.rpe ?? "-"}</span>
                  </div>
                ))}
              </details>
            ))}
          </article>
        ))}
      </div>
    </section>
  );
}
