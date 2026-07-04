export type AuthUser = {
  id: string;
  telegram_id: number;
  username?: string | null;
  first_name?: string | null;
};

export type AuthResponse = {
  access_token: string;
  user: AuthUser;
};

export type ExerciseSummary = {
  id: string;
  name: string;
  ru_name?: string | null;
  equipment?: string | null;
  target?: string | null;
  body_part?: string | null;
  movement_pattern?: string | null;
  curation_status?: string | null;
  image_url?: string | null;
  gif_url?: string | null;
  instruction_steps?: string[] | null;
};

export type WorkoutSet = {
  id: string;
  set_index: number;
  weight?: string | null;
  reps?: number | null;
  rpe?: string | null;
  is_warmup: boolean;
  notes?: string | null;
};

export type SetPayload = {
  weight?: string | null;
  reps?: number | null;
  rpe?: string | null;
  is_warmup: boolean;
  notes?: string | null;
};

export type TodaySession = {
  id: string | null;
  date: string;
  title: string;
  day_type: string;
  focus: string;
  status: string;
};

export type WorkoutExercise = {
  id: string;
  slot_name: string;
  status: string;
  planned_sets: string;
  planned_reps?: string | null;
  planned_rpe?: string | null;
  rest?: string | null;
  exercise?: ExerciseSummary | null;
  sets: WorkoutSet[];
};

export type TodayWorkout = {
  session: TodaySession;
  exercises: WorkoutExercise[];
};

export type WorkoutHistory = {
  sessions: TodayWorkout[];
};

export type ExerciseSearchFilters = {
  q?: string;
  equipment?: string;
  body_part?: string;
  movement_pattern?: string;
  curation_status?: string;
};
