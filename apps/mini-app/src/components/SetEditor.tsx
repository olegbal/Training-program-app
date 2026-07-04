import { useState } from "react";

import type { SetPayload } from "../types/workouts";

type SetEditorProps = {
  onSubmit: (payload: SetPayload) => Promise<void>;
};

export function SetEditor({ onSubmit }: SetEditorProps) {
  const [weight, setWeight] = useState("");
  const [reps, setReps] = useState("");
  const [rpe, setRpe] = useState("");
  const [notes, setNotes] = useState("");
  const [isWarmup, setIsWarmup] = useState(false);

  async function handleSubmit() {
    await onSubmit({
      weight: weight || null,
      reps: reps ? Number(reps) : null,
      rpe: rpe || null,
      is_warmup: isWarmup,
      notes: notes || null,
    });
    setWeight("");
    setReps("");
    setRpe("");
    setNotes("");
    setIsWarmup(false);
  }

  return (
    <div className="set-editor">
      <label>
        Вес
        <input inputMode="decimal" value={weight} onChange={(event) => setWeight(event.target.value)} />
      </label>
      <label>
        Повторы
        <input inputMode="numeric" value={reps} onChange={(event) => setReps(event.target.value)} />
      </label>
      <label>
        RPE
        <input inputMode="decimal" value={rpe} onChange={(event) => setRpe(event.target.value)} />
      </label>
      <label className="warmup-toggle">
        <input type="checkbox" checked={isWarmup} onChange={(event) => setIsWarmup(event.target.checked)} />
        warmup
      </label>
      <label className="notes-field">
        Заметка
        <input value={notes} onChange={(event) => setNotes(event.target.value)} />
      </label>
      <button type="button" onClick={handleSubmit}>
        Добавить подход
      </button>
    </div>
  );
}
