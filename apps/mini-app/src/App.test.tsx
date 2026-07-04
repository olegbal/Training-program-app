import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";
import * as api from "./api/client";
import type { TodayWorkout, WorkoutSet } from "./types/workouts";

vi.mock("./api/client");

const mockedApi = vi.mocked(api);

describe("Mini App tracker", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    localStorage.clear();
    window.Telegram = {
      WebApp: {
        initData: "tg-init-data",
        ready: vi.fn(),
        expand: vi.fn(),
      },
    };

    mockedApi.authTelegram.mockResolvedValue({
      access_token: "jwt",
      user: { id: "user-1", telegram_id: 123456789, username: "coach" },
    });
    mockedApi.getTodayWorkout.mockResolvedValue(sampleWorkout());
    mockedApi.startTodayWorkout.mockResolvedValue(sampleWorkout({ sessionStatus: "started" }));
    mockedApi.addSet.mockResolvedValue(sampleSet());
    mockedApi.completeExercise.mockResolvedValue({
      ...sampleWorkout().exercises[0],
      status: "completed",
    });
  });

  it("renders today's workout after Telegram auth", async () => {
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Ноги A" })).toBeInTheDocument();
    expect(screen.getByText("квадрицепсы + ягодицы + икры")).toBeInTheDocument();
    expect(screen.getByText("0 / 2")).toBeInTheDocument();
    expect(mockedApi.authTelegram).toHaveBeenCalledWith("tg-init-data");
    expect(mockedApi.getTodayWorkout).toHaveBeenCalledWith("jwt");
  });

  it("opens an exercise GIF modal from the workout screen", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(await screen.findByRole("button", { name: "Начать тренировку" }));
    await user.click(await screen.findAllByRole("button", { name: "GIF" }).then((buttons) => buttons[0]));

    expect(screen.getByRole("dialog", { name: "sled 45 degrees leg press" })).toBeInTheDocument();
    expect(screen.getByText("Raw GIF")).toHaveAttribute(
      "href",
      "https://raw.githubusercontent.com/olegbal/exercises-dataset/main/exercises/sled-45-degrees-leg-press/1.gif",
    );
  });

  it("submits a set from an exercise card", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(await screen.findByRole("button", { name: "Начать тренировку" }));
    const card = screen.getByRole("article", { name: "Жим ногами" });
    await user.type(within(card).getByLabelText("Вес"), "82.5");
    await user.type(within(card).getByLabelText("Повторы"), "9");
    await user.type(within(card).getByLabelText("RPE"), "8.5");
    await user.type(within(card).getByLabelText("Заметка"), "solid");
    await user.click(within(card).getByRole("button", { name: "Добавить подход" }));

    expect(mockedApi.addSet).toHaveBeenCalledWith("jwt", "we-1", {
      weight: "82.5",
      reps: 9,
      rpe: "8.5",
      is_warmup: false,
      notes: "solid",
    });
    expect(await within(card).findByText("82.5 кг × 9")).toBeInTheDocument();
  });

  it("marks an exercise completed", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(await screen.findByRole("button", { name: "Начать тренировку" }));
    const card = screen.getByRole("article", { name: "Жим ногами" });
    await user.click(within(card).getByRole("button", { name: "Готово" }));

    expect(mockedApi.completeExercise).toHaveBeenCalledWith("jwt", "we-1");
    await waitFor(() => expect(within(card).getByText("completed")).toBeInTheDocument());
  });
});

function sampleWorkout({ sessionStatus = "planned" }: { sessionStatus?: string } = {}): TodayWorkout {
  return {
    session: {
      id: "session-1",
      date: "2026-07-06",
      title: "Ноги A",
      day_type: "legs_a",
      focus: "квадрицепсы + ягодицы + икры",
      status: sessionStatus,
    },
    exercises: [
      {
        id: "we-1",
        slot_name: "Жим ногами",
        status: "planned",
        planned_sets: "4",
        planned_reps: "6-10",
        planned_rpe: "7.5-9",
        rest: "2-3 min",
        exercise: {
          id: "ex-1",
          name: "sled 45 degrees leg press",
          ru_name: "Жим ногами",
          equipment: "sled machine",
          target: "quadriceps",
          image_url:
            "https://raw.githubusercontent.com/olegbal/exercises-dataset/main/exercises/sled-45-degrees-leg-press/0.jpg",
          gif_url:
            "https://raw.githubusercontent.com/olegbal/exercises-dataset/main/exercises/sled-45-degrees-leg-press/1.gif",
          instruction_steps: ["Brace hard.", "Press without locking knees."],
        },
        sets: [],
      },
      {
        id: "we-2",
        slot_name: "Планка",
        status: "planned",
        planned_sets: "2-3",
        planned_reps: "time",
        planned_rpe: "control",
        rest: "45-60 sec",
        exercise: null,
        sets: [],
      },
    ],
  };
}

function sampleSet(): WorkoutSet {
  return {
    id: "set-1",
    set_index: 1,
    weight: "82.5",
    reps: 9,
    rpe: "8.5",
    is_warmup: false,
    notes: "solid",
  };
}
