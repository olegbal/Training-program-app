import { useEffect, useMemo, useState } from "react";

import {
  authTelegram,
  completeExercise,
  completeWorkout,
  getHistory,
  getTodayWorkout,
  searchExercises,
  skipExercise,
  skipWorkout,
  startTodayWorkout,
} from "./api/client";
import { HistoryScreen } from "./screens/HistoryScreen";
import { LibraryScreen } from "./screens/LibraryScreen";
import { TodayScreen } from "./screens/TodayScreen";
import { WorkoutScreen } from "./screens/WorkoutScreen";
import type { ExerciseSearchFilters, ExerciseSummary, TodayWorkout, WorkoutHistory, WorkoutExercise } from "./types/workouts";

type Screen = "today" | "workout" | "history" | "library";

const TOKEN_STORAGE_KEY = "training-agent-token";

export function App() {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_STORAGE_KEY));
  const [screen, setScreen] = useState<Screen>("today");
  const [workout, setWorkout] = useState<TodayWorkout | null>(null);
  const [history, setHistory] = useState<WorkoutHistory>({ sessions: [] });
  const [library, setLibrary] = useState<ExerciseSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function boot() {
      try {
        setIsLoading(true);
        setError(null);
        const authToken = token ?? (await authenticate());
        if (!active) {
          return;
        }
        setToken(authToken);
        localStorage.setItem(TOKEN_STORAGE_KEY, authToken);
        setWorkout(await getTodayWorkout(authToken));
      } catch (err) {
        if (active) {
          setError(err instanceof Error ? err.message : "Не удалось загрузить тренировку");
        }
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    }

    boot();

    return () => {
      active = false;
    };
  }, []);

  const completedCount = useMemo(
    () => workout?.exercises.filter((exercise) => exercise.status === "completed").length ?? 0,
    [workout],
  );

  async function authenticate(): Promise<string> {
    const initData = window.Telegram?.WebApp?.initData;
    const devToken = import.meta.env.VITE_DEV_ACCESS_TOKEN as string | undefined;
    if (!initData && devToken) {
      return devToken;
    }
    if (!initData) {
      throw new Error("Telegram initData отсутствует");
    }
    const auth = await authTelegram(initData);
    return auth.access_token;
  }

  async function requireToken(): Promise<string> {
    if (token) {
      return token;
    }
    const authToken = await authenticate();
    setToken(authToken);
    localStorage.setItem(TOKEN_STORAGE_KEY, authToken);
    return authToken;
  }

  async function handleStartWorkout() {
    const authToken = await requireToken();
    setWorkout(await startTodayWorkout(authToken));
    setScreen("workout");
  }

  async function handleOpenHistory() {
    const authToken = await requireToken();
    setHistory(await getHistory(authToken));
    setScreen("history");
  }

  async function handleSearch(filters: ExerciseSearchFilters) {
    const authToken = await requireToken();
    setLibrary(await searchExercises(authToken, filters));
  }

  async function handleCompleteWorkout() {
    if (!workout?.session.id) {
      return;
    }
    const authToken = await requireToken();
    setWorkout(await completeWorkout(authToken, workout.session.id));
  }

  async function handleSkipWorkout() {
    if (!workout?.session.id) {
      return;
    }
    const authToken = await requireToken();
    setWorkout(await skipWorkout(authToken, workout.session.id));
  }

  async function handleExerciseChanged(nextExercise: WorkoutExercise) {
    setWorkout((current) => {
      if (!current) {
        return current;
      }
      return {
        ...current,
        exercises: current.exercises.map((exercise) => (exercise.id === nextExercise.id ? nextExercise : exercise)),
      };
    });
  }

  async function handleCompleteExercise(workoutExerciseId: string) {
    const authToken = await requireToken();
    await handleExerciseChanged(await completeExercise(authToken, workoutExerciseId));
  }

  async function handleSkipExercise(workoutExerciseId: string) {
    const authToken = await requireToken();
    await handleExerciseChanged(await skipExercise(authToken, workoutExerciseId));
  }

  if (isLoading) {
    return <main className="app-shell">Загрузка...</main>;
  }

  if (error) {
    return (
      <main className="app-shell">
        <section className="empty-state">
          <h1>Training Agent</h1>
          <p>{error}</p>
        </section>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <nav className="bottom-nav" aria-label="Разделы">
        <button type="button" className={screen === "today" ? "active" : ""} onClick={() => setScreen("today")}>
          Сегодня
        </button>
        <button type="button" className={screen === "workout" ? "active" : ""} onClick={() => setScreen("workout")}>
          Тренировка
        </button>
        <button type="button" className={screen === "history" ? "active" : ""} onClick={handleOpenHistory}>
          Журнал
        </button>
        <button type="button" className={screen === "library" ? "active" : ""} onClick={() => setScreen("library")}>
          База
        </button>
      </nav>

      {screen === "today" && workout ? (
        <TodayScreen
          workout={workout}
          completedCount={completedCount}
          onStart={handleStartWorkout}
          onHistory={handleOpenHistory}
        />
      ) : null}

      {screen === "workout" && workout ? (
        <WorkoutScreen
          token={token ?? ""}
          workout={workout}
          onExerciseComplete={handleCompleteExercise}
          onExerciseSkip={handleSkipExercise}
          onExerciseChanged={handleExerciseChanged}
          onCompleteWorkout={handleCompleteWorkout}
          onSkipWorkout={handleSkipWorkout}
        />
      ) : null}

      {screen === "history" ? <HistoryScreen history={history} onBack={() => setScreen("today")} /> : null}
      {screen === "library" ? <LibraryScreen exercises={library} onSearch={handleSearch} /> : null}
    </main>
  );
}
