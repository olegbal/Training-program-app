import type { ExerciseSummary } from "../types/workouts";

type ExerciseModalProps = {
  exercise: ExerciseSummary;
  onClose: () => void;
};

export function ExerciseModal({ exercise, onClose }: ExerciseModalProps) {
  return (
    <div className="modal-backdrop">
      <section className="exercise-modal" role="dialog" aria-modal="true" aria-label={exercise.name}>
        <div className="top-row">
          <h2>{exercise.ru_name || exercise.name}</h2>
          <button type="button" className="icon-button" onClick={onClose} aria-label="Закрыть">
            x
          </button>
        </div>
        {exercise.gif_url ? <img className="modal-media" src={exercise.gif_url} alt={`${exercise.name} GIF`} /> : null}
        {exercise.image_url ? <img className="modal-thumb" src={exercise.image_url} alt={exercise.name} /> : null}
        <dl className="modal-meta">
          <div>
            <dt>Dataset</dt>
            <dd>{exercise.name}</dd>
          </div>
          <div>
            <dt>Equipment</dt>
            <dd>{exercise.equipment ?? "-"}</dd>
          </div>
          <div>
            <dt>Target</dt>
            <dd>{exercise.target ?? "-"}</dd>
          </div>
        </dl>
        {exercise.instruction_steps?.length ? (
          <ol className="modal-steps">
            {exercise.instruction_steps.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        ) : null}
        <div className="raw-links">
          {exercise.image_url ? <a href={exercise.image_url}>Raw image</a> : null}
          {exercise.gif_url ? <a href={exercise.gif_url}>Raw GIF</a> : null}
        </div>
      </section>
    </div>
  );
}
