import { ExerciseCard } from "../components/ExerciseCard";
import type { TodayWorkout, WorkoutExercise } from "../types/workouts";

type WorkoutScreenProps = {
  token: string;
  workout: TodayWorkout;
  onExerciseComplete: (workoutExerciseId: string) => Promise<void>;
  onExerciseSkip: (workoutExerciseId: string) => Promise<void>;
  onExerciseChanged: (exercise: WorkoutExercise) => void;
  onCompleteWorkout: () => Promise<void>;
  onSkipWorkout: () => Promise<void>;
};

export function WorkoutScreen({
  token,
  workout,
  onExerciseComplete,
  onExerciseSkip,
  onExerciseChanged,
  onCompleteWorkout,
  onSkipWorkout,
}: WorkoutScreenProps) {
  return (
    <section className="screen workout-screen" aria-labelledby="workout-title">
      <div className="top-row">
        <span className="day-label">{workout.session.date}</span>
        <strong>{workout.session.status}</strong>
      </div>
      <h1 id="workout-title">{workout.session.title}</h1>
      <p className="focus">{workout.session.focus}</p>

      <div className="exercise-list">
        {workout.exercises.map((exercise) => (
          <ExerciseCard
            key={exercise.id}
            token={token}
            workoutExercise={exercise}
            onChanged={onExerciseChanged}
            onComplete={onExerciseComplete}
            onSkip={onExerciseSkip}
          />
        ))}
      </div>

      <div className="sticky-actions">
        <button type="button" onClick={onCompleteWorkout}>
          Завершить тренировку
        </button>
        <button type="button" className="secondary" onClick={onSkipWorkout}>
          Пропустить
        </button>
      </div>
    </section>
  );
}
