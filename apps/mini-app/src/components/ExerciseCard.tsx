import { useState } from "react";

import { addSet } from "../api/client";
import type { WorkoutExercise, WorkoutSet } from "../types/workouts";
import { ExerciseModal } from "./ExerciseModal";
import { SetEditor } from "./SetEditor";
import { StatusPill } from "./StatusPill";

type ExerciseCardProps = {
  token: string;
  workoutExercise: WorkoutExercise;
  onChanged: (exercise: WorkoutExercise) => void;
  onComplete: (workoutExerciseId: string) => Promise<void>;
  onSkip: (workoutExerciseId: string) => Promise<void>;
};

export function ExerciseCard({ token, workoutExercise, onChanged, onComplete, onSkip }: ExerciseCardProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const exercise = workoutExercise.exercise;

  async function handleAddSet(payload: Parameters<typeof addSet>[2]) {
    const savedSet = await addSet(token, workoutExercise.id, payload);
    onChanged({ ...workoutExercise, sets: [...workoutExercise.sets, savedSet] });
  }

  return (
    <article className="exercise-card" aria-label={workoutExercise.slot_name}>
      <div className="exercise-card__head">
        <div>
          <h2>{exercise?.ru_name || workoutExercise.slot_name}</h2>
          <p>{exercise?.name ?? workoutExercise.slot_name}</p>
        </div>
        <StatusPill label={workoutExercise.status} tone={workoutExercise.status === "completed" ? "ready" : "pending"} />
      </div>

      <div className="exercise-card__body">
        {exercise?.image_url ? <img src={exercise.image_url} alt={exercise.name} /> : <div className="image-placeholder">Нет медиа</div>}
        <dl className="plan-grid">
          <div>
            <dt>Сеты</dt>
            <dd>{workoutExercise.planned_sets}</dd>
          </div>
          <div>
            <dt>Повторы</dt>
            <dd>{workoutExercise.planned_reps ?? "-"}</dd>
          </div>
          <div>
            <dt>RPE</dt>
            <dd>{workoutExercise.planned_rpe ?? "-"}</dd>
          </div>
          <div>
            <dt>Отдых</dt>
            <dd>{workoutExercise.rest ?? "-"}</dd>
          </div>
        </dl>
      </div>

      {exercise?.instruction_steps?.length ? (
        <details className="technique">
          <summary>Техника</summary>
          <ol>
            {exercise.instruction_steps.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </details>
      ) : null}

      <div className="set-list">
        {workoutExercise.sets.map((set) => (
          <SetRow key={set.id} set={set} />
        ))}
      </div>

      <SetEditor onSubmit={handleAddSet} />

      <div className="card-actions">
        <button type="button" className="secondary" onClick={() => setIsModalOpen(true)} disabled={!exercise?.gif_url}>
          GIF
        </button>
        <button type="button" onClick={() => onComplete(workoutExercise.id)}>
          Готово
        </button>
        <button type="button" className="secondary" onClick={() => onSkip(workoutExercise.id)}>
          Skip
        </button>
        <button type="button" className="secondary">
          Replace
        </button>
      </div>

      {isModalOpen && exercise ? <ExerciseModal exercise={exercise} onClose={() => setIsModalOpen(false)} /> : null}
    </article>
  );
}

function SetRow({ set }: { set: WorkoutSet }) {
  return (
    <div className="set-row">
      <span>#{set.set_index}</span>
      <strong>
        {set.weight ?? "-"} кг × {set.reps ?? "-"}
      </strong>
      <span>RPE {set.rpe ?? "-"}</span>
      {set.notes ? <small>{set.notes}</small> : null}
    </div>
  );
}
