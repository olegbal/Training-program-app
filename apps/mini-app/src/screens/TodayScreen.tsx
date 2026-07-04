import { StatusPill } from "../components/StatusPill";
import type { TodayWorkout } from "../types/workouts";

type TodayScreenProps = {
  workout: TodayWorkout;
  completedCount: number;
  onStart: () => void;
  onHistory: () => void;
};

export function TodayScreen({ workout, completedCount, onStart, onHistory }: TodayScreenProps) {
  const total = workout.exercises.length;
  const isStarted = workout.session.status !== "planned";

  return (
    <section className="screen today-panel" aria-labelledby="today-title">
      <div className="top-row">
        <span className="day-label">{new Date(workout.session.date).toLocaleDateString("ru-RU", { weekday: "long" })}</span>
        <StatusPill label={workout.session.status} tone={workout.session.status === "completed" ? "ready" : "pending"} />
      </div>

      <h1 id="today-title">{workout.session.title}</h1>
      <p className="focus">{workout.session.focus}</p>

      <div className="progress-line" aria-label="Прогресс тренировки">
        <span>Прогресс</span>
        <strong>
          {completedCount} / {total}
        </strong>
      </div>

      <div className="exercise-preview-list">
        {workout.exercises.map((exercise) => (
          <div className="exercise-preview" key={exercise.id}>
            <span>{exercise.slot_name}</span>
            <small>{exercise.planned_sets} x {exercise.planned_reps ?? "-"}</small>
          </div>
        ))}
      </div>

      <div className="actions">
        <button type="button" onClick={onStart}>
          {isStarted ? "Продолжить" : "Начать тренировку"}
        </button>
        <button type="button" className="secondary" onClick={onHistory}>
          Журнал
        </button>
      </div>
    </section>
  );
}
