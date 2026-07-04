import { useState } from "react";

import type { ExerciseSearchFilters, ExerciseSummary } from "../types/workouts";

type LibraryScreenProps = {
  exercises: ExerciseSummary[];
  onSearch: (filters: ExerciseSearchFilters) => Promise<void>;
};

export function LibraryScreen({ exercises, onSearch }: LibraryScreenProps) {
  const [filters, setFilters] = useState<ExerciseSearchFilters>({});

  function updateFilter(key: keyof ExerciseSearchFilters, value: string) {
    setFilters((current) => ({ ...current, [key]: value }));
  }

  return (
    <section className="screen library-screen" aria-labelledby="library-title">
      <h1 id="library-title">База упражнений</h1>
      <div className="library-filters">
        <input aria-label="Поиск" placeholder="romanian, leg press..." onChange={(event) => updateFilter("q", event.target.value)} />
        <input aria-label="Equipment" placeholder="barbell" onChange={(event) => updateFilter("equipment", event.target.value)} />
        <input aria-label="Body part" placeholder="upper legs" onChange={(event) => updateFilter("body_part", event.target.value)} />
        <input
          aria-label="Movement"
          placeholder="hinge"
          onChange={(event) => updateFilter("movement_pattern", event.target.value)}
        />
        <select aria-label="Curation" onChange={(event) => updateFilter("curation_status", event.target.value)}>
          <option value="">any</option>
          <option value="preferred">preferred</option>
          <option value="acceptable">acceptable</option>
          <option value="backup">backup</option>
          <option value="avoid">avoid</option>
        </select>
        <button type="button" onClick={() => onSearch(filters)}>
          Найти
        </button>
      </div>
      <div className="library-results">
        {exercises.map((exercise) => (
          <article className="library-item" key={exercise.id}>
            {exercise.image_url ? <img src={exercise.image_url} alt={exercise.name} /> : null}
            <div>
              <h2>{exercise.ru_name || exercise.name}</h2>
              <p>{exercise.equipment ?? "-"} · {exercise.target ?? "-"}</p>
              <div className="raw-links">
                {exercise.image_url ? <a href={exercise.image_url}>image</a> : null}
                {exercise.gif_url ? <a href={exercise.gif_url}>gif</a> : null}
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
