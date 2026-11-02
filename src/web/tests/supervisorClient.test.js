import {afterEach, expect, test, vi} from "vitest";
import {ApiClient} from "../src/api/client.js";

afterEach(() => vi.unstubAllGlobals());

test("proposal decisions use the served accept and decline routes", async () => {
    const fetched = vi.fn(async () => new Response("{}", {status: 200, headers: {"Content-Type": "application/json"}}));
    vi.stubGlobal("fetch", fetched);
    const api = new ApiClient({env: () => "main"});

    await api.supervisorProposal(3, 8, "accept");
    await api.supervisorProposal(4, 9, "decline");

    expect(fetched.mock.calls.map(([url, request]) => [url, request.method])).toEqual([
        ["/journal/plans/3/supervisor/receipts/8/accept", "POST"],
        ["/journal/plans/4/supervisor/receipts/9/decline", "POST"],
    ]);
});
