import { beforeEach, describe, expect, it, vi } from "vitest";

import { addSet, authTelegram, getHistory, getTodayWorkout } from "./client";

describe("api client", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("authenticates Telegram initData without exposing unsafe user data", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ access_token: "jwt", user: { id: "u1" } }));
    vi.stubGlobal("fetch", fetchMock);

    const result = await authTelegram("query-string-from-telegram");

    expect(result.access_token).toBe("jwt");
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/auth/telegram",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ init_data: "query-string-from-telegram" }),
      }),
    );
  });

  it("loads today's workout with a bearer token", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ session: { status: "planned" }, exercises: [] }));
    vi.stubGlobal("fetch", fetchMock);

    const workout = await getTodayWorkout("jwt");

    expect(workout.session.status).toBe("planned");
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/workouts/today",
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: "Bearer jwt" }),
      }),
    );
  });

  it("submits a set payload for a workout exercise", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ id: "s1", set_index: 2, reps: 9 }));
    vi.stubGlobal("fetch", fetchMock);

    const saved = await addSet("jwt", "we1", {
      weight: "82.50",
      reps: 9,
      rpe: "8.5",
      is_warmup: false,
      notes: "solid",
    });

    expect(saved.set_index).toBe(2);
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/workout-exercises/we1/sets",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({ Authorization: "Bearer jwt" }),
        body: JSON.stringify({
          weight: "82.50",
          reps: 9,
          rpe: "8.5",
          is_warmup: false,
          notes: "solid",
        }),
      }),
    );
  });

  it("loads workout history", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ sessions: [{ session: { title: "Ноги A" } }] }));
    vi.stubGlobal("fetch", fetchMock);

    const history = await getHistory("jwt");

    expect(history.sessions[0].session.title).toBe("Ноги A");
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/workouts/history",
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: "Bearer jwt" }),
      }),
    );
  });
});

function jsonResponse(payload: unknown): Response {
  return new Response(JSON.stringify(payload), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}
