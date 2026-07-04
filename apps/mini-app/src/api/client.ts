import type {
  AuthResponse,
  ExerciseSearchFilters,
  ExerciseSummary,
  SetPayload,
  TodayWorkout,
  WorkoutExercise,
  WorkoutHistory,
  WorkoutSet,
} from "../types/workouts";

const API_URL = import.meta.env.VITE_API_URL ?? "/api";

export async function getHealth(): Promise<{ status: string }> {
  const response = await fetch(`${API_URL}/health`);
  if (!response.ok) {
    throw new Error("API health check failed");
  }
  return response.json() as Promise<{ status: string }>;
}

export async function authTelegram(initData: string): Promise<AuthResponse> {
  return request<AuthResponse>("/auth/telegram", {
    method: "POST",
    body: JSON.stringify({ init_data: initData }),
  });
}

export async function getTodayWorkout(token: string): Promise<TodayWorkout> {
  return request<TodayWorkout>("/workouts/today", { token });
}

export async function startTodayWorkout(token: string): Promise<TodayWorkout> {
  return request<TodayWorkout>("/workouts/today/start", { method: "POST", token });
}

export async function getWorkout(token: string, sessionId: string): Promise<TodayWorkout> {
  return request<TodayWorkout>(`/workouts/${sessionId}`, { token });
}

export async function completeWorkout(token: string, sessionId: string): Promise<TodayWorkout> {
  return request<TodayWorkout>(`/workouts/${sessionId}/complete`, { method: "POST", token });
}

export async function skipWorkout(token: string, sessionId: string): Promise<TodayWorkout> {
  return request<TodayWorkout>(`/workouts/${sessionId}/skip`, { method: "POST", token });
}

export async function getHistory(token: string): Promise<WorkoutHistory> {
  return request<WorkoutHistory>("/workouts/history", { token });
}

export async function addSet(token: string, workoutExerciseId: string, payload: SetPayload): Promise<WorkoutSet> {
  return request<WorkoutSet>(`/workout-exercises/${workoutExerciseId}/sets`, {
    method: "POST",
    token,
    body: JSON.stringify(payload),
  });
}

export async function updateSet(token: string, setId: string, payload: SetPayload): Promise<WorkoutSet> {
  return request<WorkoutSet>(`/sets/${setId}`, {
    method: "PUT",
    token,
    body: JSON.stringify(payload),
  });
}

export async function deleteSet(token: string, setId: string): Promise<void> {
  await request<void>(`/sets/${setId}`, { method: "DELETE", token });
}

export async function completeExercise(token: string, workoutExerciseId: string): Promise<WorkoutExercise> {
  return request<WorkoutExercise>(`/workout-exercises/${workoutExerciseId}/complete`, { method: "POST", token });
}

export async function skipExercise(token: string, workoutExerciseId: string): Promise<WorkoutExercise> {
  return request<WorkoutExercise>(`/workout-exercises/${workoutExerciseId}/skip`, { method: "POST", token });
}

export async function replaceExercise(
  token: string,
  workoutExerciseId: string,
  exerciseId: string,
  notes?: string,
): Promise<WorkoutExercise> {
  return request<WorkoutExercise>(`/workout-exercises/${workoutExerciseId}/replace`, {
    method: "POST",
    token,
    body: JSON.stringify({ exercise_id: exerciseId, notes }),
  });
}

export async function searchExercises(token: string, filters: ExerciseSearchFilters): Promise<ExerciseSummary[]> {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) {
      params.set(key, value);
    }
  });
  const suffix = params.toString() ? `?${params.toString()}` : "";
  return request<ExerciseSummary[]>(`/exercises/search${suffix}`, { token });
}

type RequestOptions = RequestInit & {
  token?: string;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { token, ...fetchOptions } = options;
  const headers: Record<string, string> = { Accept: "application/json" };
  new Headers(options.headers).forEach((value, key) => {
    headers[key] = value;
  });
  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...fetchOptions,
    headers,
  });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}
